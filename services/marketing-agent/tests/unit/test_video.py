"""Tests for video generation engine."""

import os
import pytest
import tempfile
import numpy as np
from PIL import Image

from app.video.templates import TemplateRegistry, VideoTemplate, VisualizerStyle
from app.video.visualizers import WaveformVisualizer, SpectrumVisualizer, ParticleVisualizer
from app.video.renderer import VideoRenderer
from app.video.shorts_generator import ShortsGenerator


class TestTemplates:
    """Test video template system."""
    
    def test_registry_has_templates(self):
        """Test that templates are registered."""
        templates = TemplateRegistry.list_templates()
        assert len(templates) > 0
        assert 'dark_trap_16x9' in templates
        assert 'default_16x9' in templates
    
    def test_get_template_by_name(self):
        """Test retrieving template by name."""
        template = TemplateRegistry.get('dark_trap_16x9')
        assert template is not None
        assert template.genre == 'trap'
        assert template.aspect_ratio == '16:9'
    
    def test_get_template_for_genre(self):
        """Test auto-selecting template for genre."""
        template = TemplateRegistry.get_for_genre('trap', '16:9')
        assert template is not None
        assert template.genre == 'trap'
        
        # Test fallback
        template = TemplateRegistry.get_for_genre('unknown_genre', '16:9')
        assert template is not None
    
    def test_template_colors(self):
        """Test template color schemes."""
        template = TemplateRegistry.get('dark_trap_16x9')
        assert template.color_scheme.background == '#0a0a0a'
        assert template.color_scheme.primary == '#ff3366'


class TestVisualizers:
    """Test audio visualizers."""
    
    def test_waveform_visualizer(self):
        """Test waveform visualizer renders frames."""
        viz = WaveformVisualizer(width=640, height=360, fps=30)
        
        # Create fake audio chunk
        audio = np.sin(np.linspace(0, 4*np.pi, 1470)) * 0.5
        
        frame = viz.render_frame(
            audio, energy=0.5, bpm=140,
            colors={'background': '#0a0a0a', 'primary': '#ffffff'},
            text_overlay={'title': 'Test', 'subtitle': 'BPM'}
        )
        
        assert frame.shape == (360, 640, 3)
        assert frame.dtype == np.uint8
    
    def test_spectrum_visualizer(self):
        """Test spectrum visualizer."""
        viz = SpectrumVisualizer(width=640, height=360, fps=30)
        
        audio = np.random.randn(1470) * 0.3
        
        frame = viz.render_frame(
            audio, energy=0.7, bpm=140,
            colors={'background': '#0d0d0d', 'primary': '#00ff88'}
        )
        
        assert frame.shape == (360, 640, 3)
    
    def test_particle_visualizer(self):
        """Test particle visualizer."""
        viz = ParticleVisualizer(width=640, height=360, fps=30)
        
        audio = np.random.randn(1470) * 0.2
        
        frame = viz.render_frame(
            audio, energy=0.3, bpm=90,
            colors={'background': '#2d2d2d', 'primary': '#a8dadc'}
        )
        
        assert frame.shape == (360, 640, 3)


class TestVideoRenderer:
    """Test video rendering."""
    
    @pytest.fixture
    def temp_audio(self):
        """Create temporary audio file."""
        import soundfile as sf
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            # Generate 2-second sine wave
            sr = 44100
            t = np.linspace(0, 2, sr * 2)
            audio = np.sin(2 * np.pi * 440 * t) * 0.5
            sf.write(f.name, audio, sr)
            yield f.name
        
        os.unlink(f.name)
    
    @pytest.fixture
    def temp_output(self):
        """Create temporary output directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    def test_renderer_initialization(self, temp_output):
        """Test renderer setup."""
        renderer = VideoRenderer(output_dir=temp_output)
        assert renderer.output_dir == temp_output
    
    def test_calculate_energy(self, temp_output):
        """Test energy calculation."""
        renderer = VideoRenderer(output_dir=temp_output)
        
        audio = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        full = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        
        energy = renderer._calculate_energy(audio, full)
        assert 0 <= energy <= 1.0


class TestShortsGenerator:
    """Test shorts generation."""
    
    def test_detect_hook(self):
        """Test hook detection."""
        import soundfile as sf
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            # Create audio with varying energy
            sr = 44100
            audio = np.zeros(sr * 30)  # 30 seconds
            
            # Add energy spike at 10-15 seconds
            audio[10*sr:15*sr] = np.sin(2*np.pi*440*np.linspace(0, 5, 5*sr)) * 0.8
            
            # Lower energy elsewhere
            audio[:10*sr] = np.sin(2*np.pi*220*np.linspace(0, 10, 10*sr)) * 0.2
            audio[15*sr:] = np.sin(2*np.pi*220*np.linspace(0, 15, 15*sr)) * 0.2
            
            sf.write(f.name, audio, sr)
            
            generator = ShortsGenerator()
            start, confidence = generator._detect_hook(f.name, 15.0)
            
            # Should detect around 5-10 seconds (window-based detection)
            assert 3 <= start <= 15
            assert 0 <= confidence <= 1.0
        
        os.unlink(f.name)
    
    def test_platform_durations(self):
        """Test platform duration limits."""
        generator = ShortsGenerator()
        
        assert generator.PLATFORM_DURATIONS['youtube_shorts'] == (15, 60)
        assert generator.PLATFORM_DURATIONS['tiktok'] == (15, 60)
        assert generator.PLATFORM_DURATIONS['instagram_reels'] == (15, 90)
