"""Tests for thumbnail generation engine."""

import os
import pytest
import tempfile
from PIL import Image

from app.thumbnail.style_presets import PresetRegistry, StylePreset
from app.thumbnail.text_overlay import TextOverlayRenderer
from app.thumbnail.generator import ThumbnailGenerator
from app.thumbnail.ab_testing import ABTestManager


class TestStylePresets:
    """Test style preset system."""
    
    def test_presets_registered(self):
        """Test that presets are registered."""
        presets = PresetRegistry.list_presets()
        assert len(presets) > 0
        assert 'dark_trap' in presets
    
    def test_get_preset(self):
        """Test retrieving preset."""
        preset = PresetRegistry.get('dark_trap')
        assert preset is not None
        assert preset.genre == 'trap'
        assert preset.colors.accent == '#ff3366'
    
    def test_get_for_genre(self):
        """Test genre matching."""
        preset = PresetRegistry.get_for_genre('trap')
        assert preset is not None
        assert preset.genre == 'trap'
        
        # Test fallback
        preset = PresetRegistry.get_for_genre('unknown')
        assert preset is not None


class TestTextOverlay:
    """Test text overlay rendering."""
    
    def test_render_text(self):
        """Test basic text rendering."""
        renderer = TextOverlayRenderer(1280, 720)
        
        img = Image.new('RGB', (1280, 720), '#0a0a0a')
        result = renderer.render_text(
            img, "TEST BEAT", (0.5, 0.5), 100,
            color='#ffffff', effect='shadow'
        )
        
        assert result.size == (1280, 720)
    
    def test_render_multi_line(self):
        """Test multi-line text rendering."""
        renderer = TextOverlayRenderer(1280, 720)
        
        img = Image.new('RGB', (1280, 720), '#0a0a0a')
        lines = [
            {'text': 'LINE 1', 'position': (0.5, 0.3), 'font_size': 80},
            {'text': 'LINE 2', 'position': (0.5, 0.6), 'font_size': 40}
        ]
        
        result = renderer.render_multi_line(img, lines)
        assert result.size == (1280, 720)


class TestThumbnailGenerator:
    """Test thumbnail generation."""
    
    @pytest.fixture
    def temp_output(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    def test_generate_thumbnail(self, temp_output):
        """Test thumbnail generation."""
        generator = ThumbnailGenerator(output_dir=temp_output)
        
        beat_info = {
            'beat_id': 'trap_140_C_minor_test',
            'genre': 'trap',
            'bpm': 140,
            'key': 'C',
            'scale': 'minor'
        }
        
        path = generator.generate_thumbnail(beat_info, variant='A')
        
        assert path is not None
        assert os.path.exists(path)
        
        # Verify image
        img = Image.open(path)
        assert img.size == (1280, 720)
    
    def test_generate_variants(self, temp_output):
        """Test generating multiple variants."""
        generator = ThumbnailGenerator(output_dir=temp_output)
        
        beat_info = {
            'beat_id': 'drill_150_D_minor_test',
            'genre': 'drill',
            'bpm': 150,
            'key': 'D',
            'scale': 'minor'
        }
        
        paths = generator.generate_variants(beat_info, count=3)
        
        assert len(paths) == 3
        for path in paths:
            assert os.path.exists(path)
    
    def test_thumbnail_score(self, temp_output):
        """Test thumbnail scoring."""
        generator = ThumbnailGenerator(output_dir=temp_output)
        
        beat_info = {
            'beat_id': 'test_beat',
            'genre': 'trap',
            'bpm': 140
        }
        
        path = generator.generate_thumbnail(beat_info)
        score = generator.get_thumbnail_score(path)
        
        assert 'contrast' in score
        assert 'brightness' in score
        assert 'overall' in score


class TestABTesting:
    """Test A/B testing framework."""
    
    @pytest.fixture
    def temp_storage(self):
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            yield f.name
        os.unlink(f.name)
    
    def test_create_test(self, temp_storage):
        """Test creating A/B test."""
        manager = ABTestManager(storage_path=temp_storage)
        
        test = manager.create_test(
            beat_id='test_beat',
            video_content_id='video_001',
            thumbnail_paths=['/tmp/thumb_A.png', '/tmp/thumb_B.png']
        )
        
        assert test.test_id is not None
        assert len(test.variants) == 2
        assert test.status == 'running'
    
    def test_record_impressions(self, temp_storage):
        """Test recording impressions."""
        manager = ABTestManager(storage_path=temp_storage)
        
        test = manager.create_test(
            beat_id='test_beat',
            video_content_id='video_001',
            thumbnail_paths=['/tmp/thumb_A.png', '/tmp/thumb_B.png']
        )
        
        manager.record_impression(test.test_id, 'A')
        manager.record_impression(test.test_id, 'A')
        manager.record_impression(test.test_id, 'B')
        
        variant_a = [v for v in test.variants if v.label == 'A'][0]
        assert variant_a.impressions == 2
    
    def test_winner_calculation(self, temp_storage):
        """Test winner calculation."""
        manager = ABTestManager(storage_path=temp_storage)
        
        test = manager.create_test(
            beat_id='test_beat',
            video_content_id='video_001',
            thumbnail_paths=['/tmp/thumb_A.png', '/tmp/thumb_B.png']
        )
        
        # Simulate A performing better
        for _ in range(1000):
            manager.record_impression(test.test_id, 'A')
            manager.record_impression(test.test_id, 'B')
        
        for _ in range(100):
            manager.record_click(test.test_id, 'A')
        
        for _ in range(50):
            manager.record_click(test.test_id, 'B')
        
        # Should have a winner
        results = manager.get_test_results(test.test_id)
        assert results is not None
