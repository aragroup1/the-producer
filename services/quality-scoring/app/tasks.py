"""Celery tasks for quality scoring engine."""

import os
import uuid
import asyncio
from typing import Dict, Any

import numpy as np
import librosa
from scipy.spatial.distance import cosine
import structlog

from shared.celery_config import celery_app
from shared.db.database import AsyncSessionLocal
from shared.db.models import Beat
from shared.utils.audio import (
    load_audio, measure_loudness, analyze_spectral_balance,
    analyze_stereo_width, analyze_transients, detect_clipping
)

logger = structlog.get_logger()


async def _update_beat_status(beat_id: str, status: str, error: str = None):
    """Update beat status in the database."""
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        result = await session.execute(
            select(Beat).where(Beat.id == uuid.UUID(beat_id))
        )
        beat = result.scalar_one_or_none()
        if beat:
            beat.status = status
            await session.commit()
            logger.info("beat_status_updated", beat_id=beat_id, status=status)
        else:
            logger.warning("beat_not_found_for_status_update", beat_id=beat_id)


class QualityScorer:
    """Comprehensive quality scoring for generated beats."""
    
    # Quality thresholds
    THRESHOLDS = {
        'min_loudness_lufs': -16.0,
        'max_loudness_lufs': -6.0,
        'max_true_peak_db': -1.0,
        'min_spectral_balance': 0.05,
        'max_clip_ratio': 0.001,
        'min_drum_punch': 0.3,
        'min_stereo_width': 0.05,
        'max_repetition': 0.85,
        'min_quality_score': 6.0
    }
    
    def __init__(self):
        pass
    
    def score_loudness(self, audio: np.ndarray, sr: int) -> Dict[str, Any]:
        """Score loudness characteristics."""
        loudness = measure_loudness(audio, sr)
        
        lufs = loudness['lufs']
        true_peak = loudness['true_peak_db']
        
        # Score based on target range
        if -14 <= lufs <= -8:
            lufs_score = 10.0
        elif -16 <= lufs <= -6:
            lufs_score = 8.0
        elif -18 <= lufs <= -4:
            lufs_score = 6.0
        else:
            lufs_score = 4.0
        
        # True peak score
        if true_peak <= -1.0:
            peak_score = 10.0
        elif true_peak <= 0:
            peak_score = 7.0
        else:
            peak_score = 3.0
        
        return {
            'score': (lufs_score + peak_score) / 2,
            'lufs': lufs,
            'true_peak_db': true_peak,
            'passed': true_peak <= self.THRESHOLDS['max_true_peak_db']
        }
    
    def score_spectral_balance(self, audio: np.ndarray, sr: int) -> Dict[str, Any]:
        """Score frequency balance."""
        balance = analyze_spectral_balance(audio, sr)
        
        # Check for common issues
        issues = []
        
        # Too much bass
        if balance.get('sub_bass', 0) > 0.4:
            issues.append('excessive_sub_bass')
        
        # Missing lows
        if balance.get('bass', 0) < 0.05:
            issues.append('weak_bass')
        
        # Missing highs
        if balance.get('highs', 0) < 0.02:
            issues.append('dull_highs')
        
        # Harsh mids
        if balance.get('mids', 0) > 0.5:
            issues.append('harsh_mids')
        
        # Calculate score
        if len(issues) == 0:
            score = 10.0
        elif len(issues) == 1:
            score = 7.0
        elif len(issues) == 2:
            score = 5.0
        else:
            score = 3.0
        
        return {
            'score': score,
            'balance': balance,
            'issues': issues,
            'passed': score >= 5.0
        }
    
    def score_dynamics(self, audio: np.ndarray, sr: int) -> Dict[str, Any]:
        """Score dynamic range and punch."""
        transients = analyze_transients(audio, sr)
        
        onset_strength = transients['onset_strength_mean']
        spectral_flux = transients['spectral_flux_mean']
        
        # Score based on dynamic characteristics
        if onset_strength > 5 and spectral_flux > 2:
            score = 9.0
        elif onset_strength > 3 and spectral_flux > 1:
            score = 7.0
        elif onset_strength > 1:
            score = 5.0
        else:
            score = 3.0
        
        return {
            'score': score,
            'onset_strength': onset_strength,
            'spectral_flux': spectral_flux,
            'passed': score >= self.THRESHOLDS['min_drum_punch'] * 10
        }
    
    def score_stereo_field(self, audio: np.ndarray, sr: int) -> Dict[str, Any]:
        """Score stereo imaging."""
        width = analyze_stereo_width(audio)
        
        # Score based on width
        if 0.1 <= width <= 0.5:
            score = 9.0
        elif 0.05 <= width <= 0.6:
            score = 7.0
        elif width > 0:
            score = 5.0
        else:
            score = 3.0  # Mono
        
        return {
            'score': score,
            'stereo_width': width,
            'passed': width >= self.THRESHOLDS['min_stereo_width']
        }
    
    def score_clipping(self, audio: np.ndarray, sr: int) -> Dict[str, Any]:
        """Score clipping/distortion."""
        clipping = detect_clipping(audio)
        
        clip_ratio = clipping['clip_ratio']
        
        if clip_ratio == 0:
            score = 10.0
        elif clip_ratio < 0.0001:
            score = 8.0
        elif clip_ratio < 0.001:
            score = 6.0
        else:
            score = 2.0
        
        return {
            'score': score,
            'clipped_samples': clipping['clipped_samples'],
            'clip_ratio': clip_ratio,
            'passed': clip_ratio <= self.THRESHOLDS['max_clip_ratio']
        }
    
    def score_repetition(self, audio: np.ndarray, sr: int) -> Dict[str, Any]:
        """Score melodic/structural repetition."""
        if audio.ndim > 1:
            audio = np.mean(audio, axis=0)
        
        # Split into segments
        segment_length = sr * 4  # 4-second segments
        
        if len(audio) < segment_length * 2:
            return {'score': 7.0, 'repetition_ratio': 0.5, 'passed': True}
        
        segments = []
        for i in range(0, len(audio) - segment_length, segment_length):
            segment = audio[i:i + segment_length]
            
            # Simple spectral fingerprint
            spec = np.abs(librosa.stft(segment))
            fingerprint = np.mean(spec, axis=1)
            segments.append(fingerprint)
        
        if len(segments) < 2:
            return {'score': 7.0, 'repetition_ratio': 0.5, 'passed': True}
        
        # Compare segments
        similarities = []
        for i in range(len(segments) - 1):
            for j in range(i + 1, len(segments)):
                # Cosine similarity
                sim = 1 - cosine(segments[i], segments[j])
                similarities.append(sim)
        
        avg_similarity = np.mean(similarities) if similarities else 0.5
        
        # High similarity = repetitive
        if avg_similarity > 0.9:
            score = 3.0
        elif avg_similarity > 0.8:
            score = 5.0
        elif avg_similarity > 0.7:
            score = 7.0
        else:
            score = 9.0
        
        return {
            'score': score,
            'repetition_ratio': float(avg_similarity),
            'passed': avg_similarity <= self.THRESHOLDS['max_repetition']
        }
    
    def score_arrangement(self, audio: np.ndarray, sr: int,
                          expected_duration: float = 180) -> Dict[str, Any]:
        """Score arrangement quality."""
        duration = len(audio) / sr if audio.ndim == 1 else len(audio[0]) / sr
        
        issues = []
        
        # Check duration
        if duration < 60:
            issues.append('too_short')
        elif duration > 300:
            issues.append('too_long')
        
        # Check for silence at start/end
        if audio.ndim > 1:
            mono = np.mean(audio, axis=0)
        else:
            mono = audio
        
        start_rms = np.sqrt(np.mean(mono[:sr] ** 2))
        end_rms = np.sqrt(np.mean(mono[-sr:] ** 2))
        
        if start_rms < 0.001:
            issues.append('silent_start')
        if end_rms < 0.001:
            issues.append('abrupt_end')
        
        # Score
        if len(issues) == 0:
            score = 10.0
        elif len(issues) == 1:
            score = 7.0
        else:
            score = 5.0
        
        return {
            'score': score,
            'duration': duration,
            'issues': issues,
            'passed': score >= 5.0
        }
    
    def full_quality_check(self, audio_path: str, 
                           expected_duration: float = 180) -> Dict[str, Any]:
        """Run complete quality check suite."""
        logger.info("quality_check_started", audio=audio_path)
        
        audio, sr = load_audio(audio_path)
        
        # Run all checks
        loudness = self.score_loudness(audio, sr)
        spectral = self.score_spectral_balance(audio, sr)
        dynamics = self.score_dynamics(audio, sr)
        stereo = self.score_stereo_field(audio, sr)
        clipping = self.score_clipping(audio, sr)
        repetition = self.score_repetition(audio, sr)
        arrangement = self.score_arrangement(audio, sr, expected_duration)
        
        # Calculate overall score
        scores = [
            loudness['score'],
            spectral['score'],
            dynamics['score'],
            stereo['score'],
            clipping['score'],
            repetition['score'],
            arrangement['score']
        ]
        
        overall_score = np.mean(scores)
        
        # Determine pass/fail
        all_passed = all([
            loudness['passed'],
            spectral['passed'],
            dynamics['passed'],
            stereo['passed'],
            clipping['passed'],
            repetition['passed'],
            arrangement['passed']
        ])
        
        results = {
            'overall_score': round(overall_score, 2),
            'passed': all_passed and overall_score >= self.THRESHOLDS['min_quality_score'],
            'checks': {
                'loudness': loudness,
                'spectral_balance': spectral,
                'dynamics': dynamics,
                'stereo_field': stereo,
                'clipping': clipping,
                'repetition': repetition,
                'arrangement': arrangement
            }
        }
        
        logger.info(
            "quality_check_completed",
            score=overall_score,
            passed=results['passed']
        )
        
        return results


# Initialize scorer
scorer = QualityScorer()


@celery_app.task(bind=True, max_retries=2, default_retry_delay=30)
def run_quality_control(self, state: Dict[str, Any]) -> Dict[str, Any]:
    """Run quality control on a beat.
    
    Expects `state` from apply_mastering containing at least:
      - beat_id
      - mastered_path
    """
    beat_id = state["beat_id"]
    audio_path = state.get("mastered_path")
    expected_duration = state.get("expected_duration", 180)
    
    logger.info("qc_task_started", beat_id=beat_id)
    
    try:
        results = scorer.full_quality_check(audio_path, expected_duration)
        
        logger.info(
            "qc_task_completed",
            beat_id=beat_id,
            score=results['overall_score'],
            passed=results['passed']
        )
        
        # Update beat status based on QC result: qc → approved or failed
        if results["passed"]:
            asyncio.run(_update_beat_status(beat_id, 'approved'))
        else:
            asyncio.run(_update_beat_status(beat_id, 'failed'))
        
        # Update state for downstream tasks
        state["qc_results"] = results
        state["qc_passed"] = results["passed"]
        state["quality_score"] = results["overall_score"]
        return state
    
    except Exception as e:
        logger.error("qc_task_failed", beat_id=beat_id, error=str(e))
        asyncio.run(_update_beat_status(beat_id, 'failed'))
        self.retry(exc=e)
