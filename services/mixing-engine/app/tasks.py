"""Celery tasks for mixing engine."""

import os
from typing import Dict, Any

from celery import Celery
import numpy as np
from scipy import signal
import structlog

from shared.utils.audio import load_audio, save_audio, measure_loudness
from app.mix_chains import get_mix_chain

logger = structlog.get_logger()

# Initialize Celery
celery_app = Celery('mix')
celery_app.conf.broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
celery_app.conf.result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

SAMPLE_RATE = 44100


class DigitalMixingEngine:
    """Digital mixing engine implementing mix chain processing."""
    
    def __init__(self, sample_rate: int = SAMPLE_RATE):
        self.sample_rate = sample_rate
    
    def apply_eq(self, audio: np.ndarray, eq_settings: list) -> np.ndarray:
        """Apply parametric EQ."""
        for band in eq_settings:
            band_type = band['type']
            freq = band['freq']
            order = band.get('order', 2)
            
            if band_type == 'high_pass':
                sos = signal.butter(order, freq, btype='high', 
                                   fs=self.sample_rate, output='sos')
                audio = signal.sosfilt(sos, audio)
            
            elif band_type == 'low_pass':
                sos = signal.butter(order, freq, btype='low',
                                   fs=self.sample_rate, output='sos')
                audio = signal.sosfilt(sos, audio)
            
            elif band_type == 'bell':
                gain = band['gain']
                q = band['q']
                audio = self._peak_eq(audio, freq, gain, q)
            
            elif band_type == 'high_shelf':
                gain = band['gain']
                audio = self._high_shelf_eq(audio, freq, gain)
            
            elif band_type == 'low_shelf':
                gain = band['gain']
                audio = self._low_shelf_eq(audio, freq, gain)
        
        return audio
    
    def _peak_eq(self, audio: np.ndarray, freq: float, gain_db: float, 
                 q: float) -> np.ndarray:
        """Apply peak/bell EQ."""
        w0 = 2 * np.pi * freq / self.sample_rate
        alpha = np.sin(w0) / (2 * q)
        
        A = 10 ** (gain_db / 40)
        
        b0 = 1 + alpha * A
        b1 = -2 * np.cos(w0)
        b2 = 1 - alpha * A
        a0 = 1 + alpha / A
        a1 = -2 * np.cos(w0)
        a2 = 1 - alpha / A
        
        b = np.array([b0, b1, b2]) / a0
        a = np.array([a0, a1, a2]) / a0
        
        return signal.lfilter(b, a, audio)
    
    def _high_shelf_eq(self, audio: np.ndarray, freq: float, 
                       gain_db: float) -> np.ndarray:
        """Apply high shelf EQ."""
        w0 = 2 * np.pi * freq / self.sample_rate
        A = 10 ** (gain_db / 40)
        S = 1.0  # Shelf slope
        
        alpha = np.sin(w0) / 2 * np.sqrt((A + 1 / A) * (1 / S - 1) + 2)
        
        b0 = A * ((A + 1) + (A - 1) * np.cos(w0) + 2 * np.sqrt(A) * alpha)
        b1 = -2 * A * ((A - 1) + (A + 1) * np.cos(w0))
        b2 = A * ((A + 1) + (A - 1) * np.cos(w0) - 2 * np.sqrt(A) * alpha)
        a0 = (A + 1) - (A - 1) * np.cos(w0) + 2 * np.sqrt(A) * alpha
        a1 = 2 * ((A - 1) - (A + 1) * np.cos(w0))
        a2 = (A + 1) - (A - 1) * np.cos(w0) - 2 * np.sqrt(A) * alpha
        
        b = np.array([b0, b1, b2]) / a0
        a = np.array([a0, a1, a2]) / a0
        
        return signal.lfilter(b, a, audio)
    
    def _low_shelf_eq(self, audio: np.ndarray, freq: float,
                      gain_db: float) -> np.ndarray:
        """Apply low shelf EQ."""
        w0 = 2 * np.pi * freq / self.sample_rate
        A = 10 ** (gain_db / 40)
        S = 1.0
        
        alpha = np.sin(w0) / 2 * np.sqrt((A + 1 / A) * (1 / S - 1) + 2)
        
        b0 = A * ((A + 1) - (A - 1) * np.cos(w0) + 2 * np.sqrt(A) * alpha)
        b1 = 2 * A * ((A - 1) - (A + 1) * np.cos(w0))
        b2 = A * ((A + 1) - (A - 1) * np.cos(w0) - 2 * np.sqrt(A) * alpha)
        a0 = (A + 1) + (A - 1) * np.cos(w0) + 2 * np.sqrt(A) * alpha
        a1 = -2 * ((A - 1) + (A + 1) * np.cos(w0))
        a2 = (A + 1) + (A - 1) * np.cos(w0) - 2 * np.sqrt(A) * alpha
        
        b = np.array([b0, b1, b2]) / a0
        a = np.array([a0, a1, a2]) / a0
        
        return signal.lfilter(b, a, audio)
    
    def apply_compression(self, audio: np.ndarray, comp_settings: dict) -> np.ndarray:
        """Apply dynamic range compression."""
        threshold = 10 ** (comp_settings['threshold_db'] / 20)
        ratio = comp_settings['ratio']
        attack_ms = comp_settings['attack_ms']
        release_ms = comp_settings['release_ms']
        makeup_db = comp_settings.get('makeup_db', 0)
        
        attack_samples = max(1, int(attack_ms * self.sample_rate / 1000))
        release_samples = max(1, int(release_ms * self.sample_rate / 1000))
        
        # Handle stereo by processing each channel separately
        if audio.ndim > 1:
            result = np.zeros_like(audio)
            for ch in range(audio.shape[0]):
                result[ch] = self._compress_channel(audio[ch], threshold, ratio, attack_samples, release_samples)
            compressed = result
        else:
            compressed = self._compress_channel(audio, threshold, ratio, attack_samples, release_samples)
        
        # Apply makeup gain
        if makeup_db != 0:
            compressed *= 10 ** (makeup_db / 20)
        
        return compressed
    
    def _compress_channel(self, audio: np.ndarray, threshold: float, ratio: float,
                          attack_samples: int, release_samples: int) -> np.ndarray:
        """Compress a single audio channel."""
        envelope = np.zeros_like(audio)
        gain = np.ones_like(audio)
        
        for i in range(1, len(audio)):
            env_in = abs(audio[i])
            
            if env_in > envelope[i-1]:
                envelope[i] = envelope[i-1] + (env_in - envelope[i-1]) / attack_samples
            else:
                envelope[i] = envelope[i-1] + (env_in - envelope[i-1]) / release_samples
            
            if envelope[i] > threshold:
                gain[i] = (threshold + (envelope[i] - threshold) / ratio) / envelope[i]
            else:
                gain[i] = 1.0
        
        return audio * gain
    
    def apply_saturation(self, audio: np.ndarray, sat_settings: dict) -> np.ndarray:
        """Apply saturation/distortion."""
        amount = sat_settings['amount']
        sat_type = sat_settings.get('type', 'soft_clip')
        
        if sat_type == 'soft_clip':
            # Soft clipping using tanh
            return np.tanh(audio * (1 + amount * 3)) / (1 + amount)
        
        elif sat_type == 'hard_clip':
            threshold = 1.0 - amount * 0.3
            return np.clip(audio, -threshold, threshold)
        
        elif sat_type == 'tape':
            # Simple tape saturation approximation
            return audio * (1 + amount * 0.5) / (1 + amount * np.abs(audio))
        
        return audio
    
    def apply_sidechain(self, target: np.ndarray, source: np.ndarray,
                        amount: float, attack_ms: float, release_ms: float) -> np.ndarray:
        """Apply sidechain compression."""
        # Handle stereo by using mono mix for detection
        if source.ndim > 1:
            source_mono = np.mean(source, axis=0)
        else:
            source_mono = source
        
        source_env = np.abs(signal.hilbert(source_mono)) if len(source_mono) > 1 else np.abs(source_mono)
        
        attack_samples = max(1, int(attack_ms * self.sample_rate / 1000))
        release_samples = max(1, int(release_ms * self.sample_rate / 1000))
        
        smoothed_env = np.zeros_like(source_env)
        for i in range(1, len(source_env)):
            if source_env[i] > smoothed_env[i-1]:
                smoothed_env[i] = smoothed_env[i-1] + (source_env[i] - smoothed_env[i-1]) / attack_samples
            else:
                smoothed_env[i] = smoothed_env[i-1] + (source_env[i] - smoothed_env[i-1]) / release_samples
        
        max_env = np.max(smoothed_env)
        if max_env > 0:
            ducking = 1 - (smoothed_env / max_env) * amount
            ducking = np.clip(ducking, 0.1, 1.0)
            # Apply ducking to each channel
            if target.ndim > 1:
                for ch in range(target.shape[0]):
                    target[ch] *= ducking
                return target
            return target * ducking
        
        return target
    
    def apply_stereo_width(self, audio: np.ndarray, width: float) -> np.ndarray:
        """Adjust stereo width."""
        if audio.ndim == 1:
            return audio
        
        left = audio[0]
        right = audio[1]
        
        mid = (left + right) / 2
        side = (left - right) / 2
        
        # Adjust side level
        side *= width
        
        new_left = mid + side
        new_right = mid - side
        
        return np.stack([new_left, new_right])
    
    def apply_limiter(self, audio: np.ndarray, limiter_settings: dict) -> np.ndarray:
        """Apply brickwall limiter."""
        ceiling = 10 ** (limiter_settings['ceiling_db'] / 20)
        return np.clip(audio, -ceiling, ceiling)
    
    def mix_track(self, stems: Dict[str, np.ndarray], genre: str) -> np.ndarray:
        """Mix all stems using genre-specific chain."""
        chain = get_mix_chain(genre)
        processed_stems = {}
        
        for stem_name, stem_audio in stems.items():
            stem_chain = chain.get(stem_name, {})
            
            if not stem_chain:
                processed_stems[stem_name] = stem_audio
                continue
            
            processed = stem_audio.copy()
            
            # Apply gain
            gain_db = stem_chain.get('gain', 0)
            if gain_db != 0:
                processed *= 10 ** (gain_db / 20)
            
            # Apply EQ
            if 'eq' in stem_chain:
                processed = self.apply_eq(processed, stem_chain['eq'])
            
            # Apply compression
            if 'compression' in stem_chain:
                processed = self.apply_compression(processed, stem_chain['compression'])
            
            # Apply saturation
            if 'saturation' in stem_chain:
                processed = self.apply_saturation(processed, stem_chain['saturation'])
            
            # Apply stereo width
            if 'stereo_width' in stem_chain:
                processed = self.apply_stereo_width(processed, stem_chain['stereo_width'])
            
            processed_stems[stem_name] = processed
        
        # Apply sidechain (kick → bass)
        if 'drums' in processed_stems and 'bass' in processed_stems:
            bass_chain = chain.get('bass', {})
            sidechain = bass_chain.get('sidechain', {})
            
            if sidechain.get('enabled', False):
                processed_stems['bass'] = self.apply_sidechain(
                    processed_stems['bass'],
                    processed_stems['drums'],
                    sidechain['amount'],
                    sidechain['attack_ms'],
                    sidechain['release_ms']
                )
        
        # Sum to stereo mix
        mix = np.zeros_like(list(processed_stems.values())[0])
        for stem_audio in processed_stems.values():
            mix += stem_audio * 0.7  # Headroom
        
        # Apply master bus processing
        master_chain = chain.get('master_bus', {})
        
        if 'eq' in master_chain:
            mix = self.apply_eq(mix, master_chain['eq'])
        
        if 'compression' in master_chain:
            mix = self.apply_compression(mix, master_chain['compression'])
        
        if 'saturation' in master_chain:
            mix = self.apply_saturation(mix, master_chain['saturation'])
        
        if 'limiter' in master_chain:
            mix = self.apply_limiter(mix, master_chain['limiter'])
        
        return mix


# Initialize engine
mix_engine = DigitalMixingEngine()


@celery_app.task(bind=True, max_retries=2, default_retry_delay=30)
def apply_mixing(self, beat_id: str, audio_path: str, 
                 genre: str, stems: Dict[str, str] = None) -> Dict[str, Any]:
    """Apply mixing to a beat."""
    logger.info("mixing_started", beat_id=beat_id, genre=genre)
    
    try:
        # Load audio
        audio, sr = load_audio(audio_path)
        
        # For now, apply simple genre-specific EQ/compression
        # Full stem mixing requires separate stem files
        chain = get_mix_chain(genre, 'master_bus')
        
        if chain:
            if 'eq' in chain:
                audio = mix_engine.apply_eq(audio, chain['eq'])
            
            if 'compression' in chain:
                audio = mix_engine.apply_compression(audio, chain['compression'])
            
            if 'limiter' in chain:
                audio = mix_engine.apply_limiter(audio, chain['limiter'])
        
        # Save mixed audio
        output_dir = os.path.join(os.getenv('OUTPUT_PATH', '/app/output'), 'beats')
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, f'{beat_id}_mixed.wav')
        save_audio(audio, output_path, sr=sr)
        
        logger.info("mixing_completed", beat_id=beat_id, output=output_path)
        
        return {
            "beat_id": beat_id,
            "status": "completed",
            "mixed_path": output_path,
            "genre": genre
        }
    
    except Exception as e:
        logger.error("mixing_failed", beat_id=beat_id, error=str(e))
        self.retry(exc=e)
