"""Unit tests for audio processing utilities."""

import numpy as np
import pytest

from shared.utils.audio import (
    measure_loudness, analyze_spectral_balance, analyze_stereo_width,
    analyze_transients, detect_clipping, create_preview, normalize_audio,
    save_audio, load_audio
)


class TestAudioProcessing:
    """Test audio processing functions."""
    
    @pytest.fixture
    def sample_audio(self):
        """Generate sample stereo audio for testing."""
        sr = 44100
        duration = 1
        t = np.linspace(0, duration, int(sr * duration))
        mono = np.sin(2 * np.pi * 440 * t) * 0.5
        stereo = np.stack([mono, mono * 0.8])
        return stereo, sr
    
    def test_measure_loudness(self, sample_audio):
        """Test loudness measurement."""
        audio, sr = sample_audio
        loudness = measure_loudness(audio, sr)
        
        assert 'lufs' in loudness
        assert 'true_peak_db' in loudness
        assert 'peak' in loudness
        assert loudness['peak'] <= 1.0
        assert loudness['peak'] >= 0
    
    def test_analyze_spectral_balance(self, sample_audio):
        """Test spectral balance analysis."""
        audio, sr = sample_audio
        balance = analyze_spectral_balance(audio, sr)
        
        assert 'sub_bass' in balance
        assert 'bass' in balance
        assert 'mids' in balance
        assert 'highs' in balance
        
        # Energy should sum to approximately 1
        total = sum(balance.values())
        assert 0.9 <= total <= 1.1
    
    def test_analyze_stereo_width(self, sample_audio):
        """Test stereo width analysis."""
        audio, sr = sample_audio
        width = analyze_stereo_width(audio)
        
        assert 0 <= width <= 1
        # Our test audio has slight width difference
        assert width > 0
    
    def test_analyze_stereo_width_mono(self):
        """Test stereo width for mono audio."""
        audio = np.ones(1000)
        width = analyze_stereo_width(audio)
        assert width == 0.0
    
    def test_detect_clipping_clean(self, sample_audio):
        """Test clipping detection on clean audio."""
        audio, sr = sample_audio
        clipping = detect_clipping(audio)
        
        assert clipping['clipped_samples'] == 0
        assert clipping['clip_ratio'] == 0
        assert not clipping['has_clipping']
    
    def test_detect_clipping_clipped(self):
        """Test clipping detection on clipped audio."""
        audio = np.ones(1000) * 1.5  # Above 1.0 threshold
        clipping = detect_clipping(audio)
        
        assert clipping['clipped_samples'] > 0
        assert clipping['has_clipping']
    
    def test_create_preview(self, sample_audio):
        """Test preview generation."""
        audio, sr = sample_audio
        preview = create_preview(audio, sr, duration=0.5)
        
        assert preview.shape[0] == audio.shape[0]  # Same channels
        assert preview.shape[1] == int(0.5 * sr)  # Correct duration
    
    def test_normalize_audio(self, sample_audio):
        """Test audio normalization."""
        audio, sr = sample_audio
        normalized = normalize_audio(audio, target_db=-6)
        
        peak = np.max(np.abs(normalized))
        expected_peak = 10 ** (-6 / 20)
        assert abs(peak - expected_peak) < 0.01
    
    def test_save_and_load_audio(self, tmp_path, sample_audio):
        """Test saving and loading audio."""
        audio, sr = sample_audio
        path = str(tmp_path / "test.wav")
        
        save_audio(audio, path, sr=sr)
        loaded, loaded_sr = load_audio(path)
        
        assert loaded_sr == sr
        assert loaded.shape == audio.shape
        np.testing.assert_array_almost_equal(loaded, audio, decimal=4)
