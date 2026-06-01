"""Celery tasks for mastering engine."""

import os
from typing import Dict, Any

from celery import Celery
import numpy as np
from scipy import signal
import structlog

from shared.utils.audio import load_audio, save_audio, measure_loudness

logger = structlog.get_logger()

# Initialize Celery
celery_app = Celery('master')
celery_app.conf.broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
celery_app.conf.result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

SAMPLE_RATE = 44100


class MasteringEngine:
    """AI-assisted mastering for commercial loudness."""
    
    TARGET_LUFS = {
        'streaming': -14.0,
        'beatstars': -9.0,
        'club': -8.0,
        'preview': -12.0
    }
    
    def __init__(self, target: str = 'beatstars', sample_rate: int = SAMPLE_RATE):
        self.target_lufs = self.TARGET_LUFS.get(target, -9.0)
        self.sample_rate = sample_rate
    
    def measure_loudness(self, audio: np.ndarray) -> Dict[str, float]:
        """Measure integrated LUFS and true peak."""
        try:
            import pyloudnorm as pyln
            
            meter = pyln.Meter(self.sample_rate)
            
            if audio.ndim == 1:
                audio_stereo = audio.reshape(1, -1)
            else:
                audio_stereo = audio
            
            loudness = meter.integrated_loudness(audio_stereo.T)
            true_peak = np.max(np.abs(audio))
            
            return {
                'lufs': float(loudness),
                'true_peak_db': float(20 * np.log10(true_peak + 1e-10)),
                'peak': float(true_peak),
                'needs_gain_db': self.target_lufs - loudness
            }
        except ImportError:
            # Fallback
            rms = np.sqrt(np.mean(audio ** 2))
            peak = np.max(np.abs(audio))
            return {
                'lufs': float(20 * np.log10(rms + 1e-10)),
                'true_peak_db': float(20 * np.log10(peak + 1e-10)),
                'peak': float(peak),
                'needs_gain_db': 0.0
            }
    
    def multiband_compression(self, audio: np.ndarray, 
                              bands: list = None) -> np.ndarray:
        """Apply multiband compression."""
        if bands is None:
            bands = [
                {'low': 20, 'high': 250, 'ratio': 3, 'threshold_db': -12},
                {'low': 250, 'high': 4000, 'ratio': 2, 'threshold_db': -15},
                {'low': 4000, 'high': 20000, 'ratio': 2, 'threshold_db': -18}
            ]
        
        output = np.zeros_like(audio)
        
        for band in bands:
            # Extract band
            sos = signal.butter(4, [band['low'], band['high']], 
                               btype='band', fs=self.sample_rate, output='sos')
            band_audio = signal.sosfilt(sos, audio)
            
            # Compress
            threshold = 10 ** (band['threshold_db'] / 20)
            ratio = band['ratio']
            
            envelope = np.abs(band_audio)
            gain = np.ones_like(band_audio)
            
            mask = envelope > threshold
            gain[mask] = (threshold + (envelope[mask] - threshold) / ratio) / envelope[mask]
            
            output += band_audio * gain
        
        return output
    
    def stereo_enhancement(self, audio: np.ndarray, amount: float = 0.1) -> np.ndarray:
        """Enhance stereo width."""
        if audio.ndim == 1:
            return audio
        
        left = audio[0]
        right = audio[1]
        
        mid = (left + right) / 2
        side = (left - right) / 2
        
        # Enhance side
        side *= (1 + amount)
        
        new_left = mid + side
        new_right = mid - side
        
        return np.stack([new_left, new_right])
    
    def loudness_match(self, audio: np.ndarray) -> np.ndarray:
        """Match target LUFS."""
        current = self.measure_loudness(audio)
        gain_db = current['needs_gain_db']
        
        # Limit gain to prevent clipping
        max_gain = -current['true_peak_db'] - 1.0
        gain_db = min(gain_db, max_gain)
        
        gain_linear = 10 ** (gain_db / 20)
        return audio * gain_linear
    
    def true_peak_limiter(self, audio: np.ndarray, ceiling_db: float = -1.0) -> np.ndarray:
        """Prevent inter-sample peaks."""
        ceiling = 10 ** (ceiling_db / 20)
        
        # Simple lookahead limiter
        lookahead = 4
        limited = np.copy(audio)
        
        for i in range(lookahead, len(audio) - lookahead):
            window = audio[i-lookahead:i+lookahead+1]
            peak = np.max(np.abs(window))
            
            if peak > ceiling:
                limited[i] = audio[i] * (ceiling / peak)
        
        return limited
    
    def apply_mastering(self, audio: np.ndarray) -> np.ndarray:
        """Apply full mastering chain."""
        logger.info("mastering_started", target_lufs=self.target_lufs)
        
        # 1. Multiband compression
        audio = self.multiband_compression(audio)
        
        # 2. Stereo enhancement
        if audio.ndim > 1:
            audio = self.stereo_enhancement(audio, amount=0.05)
        
        # 3. Loudness optimization
        audio = self.loudness_match(audio)
        
        # 4. True peak limiting
        audio = self.true_peak_limiter(audio)
        
        # Measure final loudness
        final = self.measure_loudness(audio)
        
        logger.info(
            "mastering_completed",
            final_lufs=final['lufs'],
            true_peak=final['true_peak_db']
        )
        
        return audio


# Initialize engine
master_engine = MasteringEngine()


@celery_app.task(bind=True, max_retries=2, default_retry_delay=30)
def apply_mastering(self, beat_id: str, audio_path: str,
                    target: str = 'beatstars') -> Dict[str, Any]:
    """Apply mastering to a beat."""
    logger.info("mastering_task_started", beat_id=beat_id, target=target)
    
    try:
        # Load audio
        audio, sr = load_audio(audio_path)
        
        # Apply mastering
        engine = MasteringEngine(target=target, sample_rate=sr)
        mastered = engine.apply_mastering(audio)
        
        # Save mastered audio
        output_dir = os.path.join(os.getenv('OUTPUT_PATH', '/app/output'), 'beats')
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, f'{beat_id}_mastered.wav')
        save_audio(mastered, output_path, sr=sr)
        
        # Measure final loudness
        loudness = engine.measure_loudness(mastered)
        
        logger.info("mastering_task_completed", beat_id=beat_id, output=output_path)
        
        return {
            "beat_id": beat_id,
            "status": "completed",
            "mastered_path": output_path,
            "loudness_lufs": loudness['lufs'],
            "true_peak_db": loudness['true_peak_db'],
            "target": target
        }
    
    except Exception as e:
        logger.error("mastering_task_failed", beat_id=beat_id, error=str(e))
        self.retry(exc=e)
