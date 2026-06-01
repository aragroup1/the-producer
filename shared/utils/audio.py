"""Shared audio processing utilities."""

import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
from typing import Tuple, Optional, Dict, Any
import tempfile


SAMPLE_RATE = 44100
N_FFT = 2048
HOP_LENGTH = 512


def load_audio(path: str, sr: int = SAMPLE_RATE) -> Tuple[np.ndarray, int]:
    """Load audio file as numpy array."""
    audio, loaded_sr = librosa.load(path, sr=sr, mono=False)
    if audio.ndim == 1:
        audio = np.stack([audio, audio])
    return audio, loaded_sr


def save_audio(audio: np.ndarray, path: str, sr: int = SAMPLE_RATE, subtype: str = "PCM_24") -> str:
    """Save audio array to file."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    sf.write(path, audio.T if audio.ndim > 1 else audio, sr, subtype=subtype)
    return path


def normalize_audio(audio: np.ndarray, target_db: float = -1.0) -> np.ndarray:
    """Normalize audio to target peak dB."""
    peak = np.max(np.abs(audio))
    if peak > 0:
        target_peak = 10 ** (target_db / 20)
        audio = audio * (target_peak / peak)
    return audio


def measure_loudness(audio: np.ndarray, sr: int = SAMPLE_RATE) -> Dict[str, float]:
    """Measure integrated LUFS and true peak."""
    try:
        import pyloudnorm as pyln
        meter = pyln.Meter(sr)
        
        # pyloudnorm expects (channels, samples)
        if audio.ndim == 1:
            audio = audio.reshape(1, -1)
        else:
            audio = audio
        
        loudness = meter.integrated_loudness(audio.T)
        true_peak = np.max(np.abs(audio))
        
        return {
            "lufs": float(loudness),
            "true_peak_db": float(20 * np.log10(true_peak + 1e-10)),
            "peak": float(true_peak)
        }
    except ImportError:
        # Fallback: simple RMS measurement
        rms = np.sqrt(np.mean(audio ** 2))
        peak = np.max(np.abs(audio))
        return {
            "lufs": float(20 * np.log10(rms + 1e-10)),
            "true_peak_db": float(20 * np.log10(peak + 1e-10)),
            "peak": float(peak)
        }


def analyze_spectral_balance(audio: np.ndarray, sr: int = SAMPLE_RATE) -> Dict[str, float]:
    """Analyze spectral balance of audio."""
    if audio.ndim > 1:
        audio = np.mean(audio, axis=0)
    
    # STFT
    D = np.abs(librosa.stft(audio, n_fft=N_FFT, hop_length=HOP_LENGTH))
    
    # Frequency bands
    freqs = librosa.fft_frequencies(sr=sr, n_fft=N_FFT)
    
    bands = {
        "sub_bass": (20, 60),
        "bass": (60, 250),
        "low_mids": (250, 500),
        "mids": (500, 2000),
        "high_mids": (2000, 6000),
        "highs": (6000, 20000)
    }
    
    band_energy = {}
    total_energy = np.sum(D ** 2)
    
    for band_name, (low, high) in bands.items():
        mask = (freqs >= low) & (freqs < high)
        energy = np.sum(D[mask] ** 2)
        band_energy[band_name] = float(energy / (total_energy + 1e-10))
    
    return band_energy


def analyze_stereo_width(audio: np.ndarray) -> float:
    """Analyze stereo width of audio."""
    if audio.ndim == 1:
        return 0.0
    
    left = audio[0]
    right = audio[1]
    
    # Mid/Side
    mid = (left + right) / 2
    side = (left - right) / 2
    
    mid_energy = np.sum(mid ** 2)
    side_energy = np.sum(side ** 2)
    
    width = side_energy / (mid_energy + side_energy + 1e-10)
    return float(width)


def analyze_transients(audio: np.ndarray, sr: int = SAMPLE_RATE) -> Dict[str, float]:
    """Analyze transient/punch characteristics."""
    if audio.ndim > 1:
        audio = np.mean(audio, axis=0)
    
    # Onset strength
    onset_env = librosa.onset.onset_strength(y=audio, sr=sr)
    
    # Spectral flux
    flux = np.diff(onset_env)
    flux = np.maximum(flux, 0)
    
    return {
        "onset_strength_mean": float(np.mean(onset_env)),
        "onset_strength_max": float(np.max(onset_env)),
        "spectral_flux_mean": float(np.mean(flux)),
        "spectral_flux_max": float(np.max(flux))
    }


def detect_clipping(audio: np.ndarray, threshold: float = 0.99) -> Dict[str, Any]:
    """Detect clipping in audio."""
    clipped_samples = np.sum(np.abs(audio) > threshold)
    total_samples = audio.size
    clip_ratio = clipped_samples / total_samples
    
    return {
        "clipped_samples": int(clipped_samples),
        "total_samples": int(total_samples),
        "clip_ratio": float(clip_ratio),
        "has_clipping": clip_ratio > 0.001
    }


def generate_watermark(audio: np.ndarray, sr: int = SAMPLE_RATE) -> np.ndarray:
    """Add watermark to preview audio."""
    # Simple voice watermark every 8 seconds
    watermark_interval = 8 * sr
    
    # Create silent watermark (just for structure)
    # In production, overlay "AI Producer" voice
    watermarked = audio.copy()
    
    return watermarked


def trim_silence(audio: np.ndarray, threshold_db: float = -60) -> np.ndarray:
    """Trim silence from start and end of audio."""
    if audio.ndim > 1:
        # Use first channel for detection
        mono = np.mean(audio, axis=0)
    else:
        mono = audio
    
    threshold = 10 ** (threshold_db / 20)
    
    # Find non-silent regions
    non_silent = np.where(np.abs(mono) > threshold)[0]
    
    if len(non_silent) == 0:
        return audio
    
    start = max(0, non_silent[0] - int(0.1 * SAMPLE_RATE))
    end = min(len(mono), non_silent[-1] + int(0.1 * SAMPLE_RATE))
    
    if audio.ndim > 1:
        return audio[:, start:end]
    return audio[start:end]


def create_preview(audio: np.ndarray, sr: int = SAMPLE_RATE, 
                   duration: float = 30.0, fade_in: float = 0.5, 
                   fade_out: float = 1.0) -> np.ndarray:
    """Create a preview clip from full audio."""
    total_samples = audio.shape[-1]
    preview_samples = int(duration * sr)
    
    # Take middle section for preview
    start = max(0, (total_samples - preview_samples) // 2)
    end = min(total_samples, start + preview_samples)
    
    if audio.ndim > 1:
        preview = audio[:, start:end]
    else:
        preview = audio[start:end]
    
    # Apply fades
    fade_in_samples = min(int(fade_in * sr), preview.shape[-1])
    fade_out_samples = min(int(fade_out * sr), preview.shape[-1])
    
    fade_in_curve = np.linspace(0, 1, fade_in_samples)
    fade_out_curve = np.linspace(1, 0, fade_out_samples)
    
    if preview.ndim > 1:
        for ch in range(preview.shape[0]):
            preview[ch, :fade_in_samples] *= fade_in_curve
            preview[ch, -fade_out_samples:] *= fade_out_curve
    else:
        preview[:fade_in_samples] *= fade_in_curve
        preview[-fade_out_samples:] *= fade_out_curve
    
    return preview
