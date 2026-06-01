"""Tests for core pipeline and channel management."""

import os
import pytest
import tempfile

from app.core.beat_pipeline import PromotionPipeline
from app.core.channel_manager import ChannelManager, Channel, ChannelPlatform
from app.core.rule_engine import RuleEngine, Rule, Condition


class TestPromotionPipeline:
    """Test promotion pipeline."""
    
    @pytest.fixture
    def temp_output(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    def test_pipeline_initialization(self, temp_output):
        """Test pipeline setup."""
        pipeline = PromotionPipeline(output_base=temp_output)
        
        assert pipeline.video_renderer is not None
        assert pipeline.thumbnail_generator is not None
    
    def test_generate_seo(self, temp_output):
        """Test SEO generation."""
        pipeline = PromotionPipeline(output_base=temp_output)
        
        beat_info = {
            'beat_id': 'trap_140_C_minor_test',
            'genre': 'trap',
            'bpm': 140,
            'key': 'C',
            'scale': 'minor'
        }
        
        seo = pipeline._generate_seo(beat_info)
        
        assert 'titles' in seo
        assert 'description' in seo
        assert 'tags' in seo
        assert len(seo['titles']) > 0
    
    def test_build_upload_plans(self, temp_output):
        """Test upload plan generation."""
        pipeline = PromotionPipeline(output_base=temp_output)
        
        pipeline_result = {
            'beat_id': 'test_beat',
            'outputs': {
                'seo': {
                    'primary_title': 'Test Title',
                    'description': 'Test description',
                    'tags': ['trap', 'beat'],
                    'hashtags': '#trap #beat'
                },
                'video': '/tmp/test.mp4',
                'thumbnails': ['/tmp/thumb.png'],
                'shorts': {
                    'youtube_shorts': '/tmp/short.mp4',
                    'tiktok': '/tmp/tiktok.mp4',
                    'instagram_reels': '/tmp/reel.mp4'
                }
            }
        }
        
        plans = pipeline._build_upload_plans(pipeline_result)
        
        assert 'youtube' in plans
        assert 'youtube_shorts' in plans
        assert 'tiktok' in plans
        assert 'instagram_reels' in plans


class TestChannelManager:
    """Test channel management."""
    
    @pytest.fixture
    def temp_storage(self):
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            yield f.name
        os.unlink(f.name)
    
    def test_default_channels(self, temp_storage):
        """Test default channels are created."""
        manager = ChannelManager(storage_path=temp_storage)
        
        assert len(manager.channels) > 0
        
        # Check for expected channels
        channel_ids = [ch.id for ch in manager.channels.values()]
        assert 'drill_beats_yt' in channel_ids
        assert 'trap_beats_yt' in channel_ids
    
    def test_get_channel(self, temp_storage):
        """Test retrieving channel."""
        manager = ChannelManager(storage_path=temp_storage)
        
        channel = manager.get_channel('drill_beats_yt')
        assert channel is not None
        assert channel.niche == 'drill'
    
    def test_assign_beat_to_channel(self, temp_storage):
        """Test beat assignment."""
        manager = ChannelManager(storage_path=temp_storage)
        
        beat_info = {
            'beat_id': 'drill_150_D_minor',
            'genre': 'drill',
            'bpm': 150
        }
        
        channel = manager.assign_beat_to_channel(beat_info)
        
        assert channel is not None
        assert channel.niche == 'drill'
    
    def test_channel_stats(self, temp_storage):
        """Test channel stats."""
        manager = ChannelManager(storage_path=temp_storage)
        
        stats = manager.get_channel_stats('trap_beats_yt')
        
        assert stats is not None
        assert 'today_uploads' in stats
        assert 'upload_frequency' in stats


class TestRuleEngine:
    """Test automation rules."""
    
    @pytest.fixture
    def temp_storage(self):
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            yield f.name
        os.unlink(f.name)
    
    def test_default_rules(self, temp_storage):
        """Test default rules are loaded."""
        engine = RuleEngine(storage_path=temp_storage)
        
        assert len(engine.rules) > 0
        
        rules = engine.list_rules()
        rule_names = [r['name'] for r in rules]
        assert 'High CTR Drill Boost' in rule_names
    
    def test_rule_evaluation(self, temp_storage):
        """Test rule evaluation."""
        engine = RuleEngine(storage_path=temp_storage)
        
        # Context that should trigger the drill rule
        context = {
            'genre': 'drill',
            'ctr': 0.06
        }
        
        triggered = engine.evaluate_all(context)
        
        assert len(triggered) > 0
    
    def test_rule_not_triggered(self, temp_storage):
        """Test rule not triggering when conditions not met."""
        engine = RuleEngine(storage_path=temp_storage)
        
        # Context that should NOT trigger
        context = {
            'genre': 'lofi',
            'ctr': 0.01
        }
        
        triggered = engine.evaluate_all(context)
        
        # Should not trigger drill rule
        drill_triggers = [t for t in triggered if 'drill' in t['rule_name'].lower()]
        assert len(drill_triggers) == 0
    
    def test_add_rule(self, temp_storage):
        """Test adding custom rule."""
        engine = RuleEngine(storage_path=temp_storage)
        
        rule = Rule(
            id='test_rule',
            name='Test Rule',
            description='A test rule',
            conditions=[
                Condition(metric='views', operator='>', value=10000)
            ],
            logical_op='and',
            actions=[{'type': 'log', 'message': 'High views!'}]
        )
        
        engine.add_rule(rule)
        
        assert 'test_rule' in engine.rules
    
    def test_disable_enable_rule(self, temp_storage):
        """Test toggling rules."""
        engine = RuleEngine(storage_path=temp_storage)
        
        engine.disable_rule('high_ctr_drill')
        rule = engine.get_rule('high_ctr_drill')
        assert not rule.enabled
        
        engine.enable_rule('high_ctr_drill')
        rule = engine.get_rule('high_ctr_drill')
        assert rule.enabled
