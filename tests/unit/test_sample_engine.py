"""Unit tests for the sample-based rendering engine."""

import os
import sys
import pytest
import numpy as np
import importlib.util

# Load sample_engine directly (hyphen in path prevents normal import)
spec = importlib.util.spec_from_file_location(
    'sample_engine', 
    os.path.join(os.path.dirname(__file__), '..', '..', 'services', 'sound-engine', 'app', 'sample_engine.py')
)
sample_engine_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sample_engine_mod)

SampleEngine = sample_engine_mod.SampleEngine
ADSR = sample_engine_mod.ADSR
Sample = sample_engine_mod.Sample


class TestADSR:
    """Test ADSR envelope generation."""
    
    def test_adsr_to_samples(self):
        """Test ADSR conversion to samples."""
        adsr = ADSR(attack_ms=10, decay_ms=50, sustain_level=0.5, release_ms=100)
        attack_s, decay_s, release_s = adsr.to_samples(sr=44100)
        
        assert attack_s == 441  # 10ms at 44.1kHz
        assert decay_s == 2205  # 50ms
        assert release_s == 4410  # 100ms
    
    def test_default_adsr_values(self):
        """Test default ADSR values."""
        adsr = ADSR()
        assert adsr.attack_ms == 5.0
        assert adsr.sustain_level == 0.7


class TestSampleEngine:
    """Test the sample engine."""
    
    @pytest.fixture
    def engine(self):
        """Create a sample engine with placeholder samples."""
        base_path = os.path.join(os.path.dirname(__file__), '..', '..', 'samples')
        return SampleEngine(sample_base_path=base_path, sample_rate=44100)
    
    def test_load_category(self, engine):
        """Test loading a sample category."""
        sample_map = engine.load_category('kick', 'trap')
        
        assert sample_map.category == 'kick'
        assert sample_map.genre == 'trap'
        assert len(sample_map.samples) > 0
        assert len(sample_map.name_map) > 0
    
    def test_load_nonexistent_category(self, engine):
        """Test loading a category that doesn't exist."""
        sample_map = engine.load_category('kick', 'nonexistent_genre')
        
        assert len(sample_map.samples) == 0
    
    def test_parse_root_note(self, engine):
        """Test parsing root note from filename."""
        assert engine._parse_root_note('808_C') == 48  # C3 (default octave)
        assert engine._parse_root_note('lead_A3') == 57  # A3
        assert engine._parse_root_note('kick_01') is None
    
    def test_render_drum_hit(self, engine):
        """Test rendering a single drum hit."""
        result = engine.render_drum_hit('kick', 'trap', velocity=100, start_time=0.0)
        
        assert result is not None
        audio, start_sample = result
        assert audio.ndim == 2  # Stereo
        assert audio.shape[0] == 2  # Two channels
        assert start_sample == 0
        assert np.max(np.abs(audio)) > 0
    
    def test_render_drum_hit_humanization(self, engine):
        """Test drum hit humanization."""
        # With humanization, start time should vary slightly
        results = []
        for _ in range(10):
            result = engine.render_drum_hit('kick', 'trap', 
                                            velocity=100, start_time=1.0,
                                            humanize_ms=10)
            if result:
                results.append(result[1])
        
        # Should have some variation
        assert len(set(results)) > 1
    
    def test_render_drum_pattern(self, engine):
        """Test rendering a full drum pattern."""
        pattern = {
            'kick': [(0, 100), (1, 90), (2, 95)],
            'snare': [(1, 110), (3, 110)],
            'hihat_closed': [(0, 70), (0.5, 65), (1, 70), (1.5, 75)],
        }
        
        # 2 bars at 140 BPM = ~3.4 seconds, enough for hits up to time 3
        audio = engine.render_drum_pattern(pattern, 'trap', bars=2)
        
        assert audio.ndim == 2
        assert audio.shape[0] == 2
        assert audio.shape[1] > 0
        assert np.max(np.abs(audio)) > 0
        assert np.max(np.abs(audio)) <= 0.95  # No clipping
    
    def test_render_melodic_track(self, engine):
        """Test rendering a melodic track."""
        notes = [
            {'pitch': 60, 'velocity': 100, 'start_time': 0.0, 'duration': 1.0},
            {'pitch': 62, 'velocity': 90, 'start_time': 1.0, 'duration': 1.0},
            {'pitch': 64, 'velocity': 100, 'start_time': 2.0, 'duration': 1.0},
        ]
        
        audio = engine.render_melodic_track(notes, 'synth_lead', 'trap')
        
        assert audio.ndim == 2
        assert audio.shape[0] == 2
        assert audio.shape[1] > 0
        assert np.max(np.abs(audio)) > 0
    
    def test_render_beat(self, engine):
        """Test rendering a full beat composition."""
        composition = {
            'genre': 'trap',
            'bpm': 140,
            'duration_bars': 4,
            'tracks': {
                'drums': {
                    'kick': [(0, 100), (1.5, 90), (2.5, 95)],
                    'snare': [(1, 110), (3, 110)],
                    'hihat_closed': [(0, 70), (0.5, 65), (1, 70), (1.5, 75)],
                },
                'bass': [
                    {'pitch': 36, 'velocity': 100, 'start_time': 0.0, 'duration': 2.0},
                    {'pitch': 36, 'velocity': 90, 'start_time': 2.0, 'duration': 2.0},
                ],
                'melody': [
                    {'pitch': 72, 'velocity': 80, 'start_time': 0.0, 'duration': 1.0},
                    {'pitch': 74, 'velocity': 85, 'start_time': 1.0, 'duration': 1.0},
                ],
            }
        }
        
        stems = engine.render_beat(composition, 'trap', bpm=140)
        
        assert 'drums' in stems
        assert 'bass' in stems
        assert 'melody' in stems
        
        for name, audio in stems.items():
            assert audio.ndim == 2
            assert audio.shape[0] == 2
            assert np.max(np.abs(audio)) > 0
    
    def test_mix_stems(self, engine):
        """Test mixing stems."""
        stems = {
            'drums': np.random.randn(2, 44100) * 0.1,
            'bass': np.random.randn(2, 44100) * 0.1,
            'melody': np.random.randn(2, 44100) * 0.05,
        }
        
        mix = engine.mix_stems(stems)
        
        assert mix.ndim == 2
        assert mix.shape[0] == 2
        assert np.max(np.abs(mix)) <= 0.95  # No clipping
    
    def test_velocity_scaling(self, engine):
        """Test velocity affects volume."""
        result_loud = engine.render_drum_hit('kick', 'trap', velocity=127, start_time=0)
        result_quiet = engine.render_drum_hit('kick', 'trap', velocity=30, start_time=0)
        
        assert result_loud is not None
        assert result_quiet is not None
        
        loud_peak = np.max(np.abs(result_loud[0]))
        quiet_peak = np.max(np.abs(result_quiet[0]))
        
        assert loud_peak > quiet_peak
    
    def test_pitch_shifting(self, engine):
        """Test pitch shifting for melodic samples."""
        # Load a sample
        sample_map = engine.load_category('synth_lead', 'trap')
        sample = sample_map.get_melodic_sample(60)  # C4
        
        assert sample is not None
        
        # Render at original pitch
        audio_orig, _ = engine.render_note(sample, 60, 100, 0, 1.0)
        
        # Render shifted up 7 semitones (perfect fifth)
        audio_shifted, _ = engine.render_note(sample, 67, 100, 0, 1.0)
        
        # Shifted should be shorter (higher pitch = shorter duration after stretch)
        assert audio_shifted.shape[1] < audio_orig.shape[1]


class TestIntegration:
    """Integration tests with the composition engine."""
    
    @pytest.fixture
    def engine(self):
        base_path = os.path.join(os.path.dirname(__file__), '..', '..', 'samples')
        return SampleEngine(sample_base_path=base_path, sample_rate=44100)
    
    def test_compose_and_render(self, engine):
        """Test full compose → render pipeline."""
        import importlib.util
        
        # Load composition engine directly (hyphen in path prevents normal import)
        spec = importlib.util.spec_from_file_location(
            'music_transformer',
            os.path.join(os.path.dirname(__file__), '..', '..', 'services', 'composition-engine', 'app', 'models', 'music_transformer.py')
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        CompositionEngine = mod.CompositionEngine
        
        # Compose
        composer = CompositionEngine()
        composition = composer.compose_beat(
            genre='trap',
            bpm=140,
            key='C',
            duration_bars=4
        )
        
        assert 'tracks' in composition
        
        # Render
        stems = engine.render_beat(composition, 'trap', bpm=140)
        
        assert len(stems) > 0
        
        # Mix
        mix = engine.mix_stems(stems)
        
        assert mix.ndim == 2
        assert np.max(np.abs(mix)) > 0
        assert np.max(np.abs(mix)) <= 0.95
    
    def test_save_and_load_stems(self, engine, tmp_path):
        """Test saving stems and loading them back."""
        import soundfile as sf
        
        stems = {
            'drums': np.random.randn(2, 44100) * 0.1,
            'bass': np.random.randn(2, 44100) * 0.1,
        }
        
        output_dir = str(tmp_path)
        paths = engine.save_stems(stems, 'test_beat', output_dir)
        
        assert 'drums' in paths
        assert 'bass' in paths
        assert os.path.exists(paths['drums'])
        assert os.path.exists(paths['bass'])
        
        # Load back and verify
        drums, sr = sf.read(paths['drums'])
        assert sr == 44100
        assert drums.shape[1] == 2  # Stereo
