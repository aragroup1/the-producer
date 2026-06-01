"""Tests for the marketing agent."""

import os
import json
import tempfile
import pytest
from datetime import datetime, timedelta

from app.core.beat_pipeline import PromotionPipeline
from app.scheduler import ContentCalendar, AnalyticsTracker, PostSchedule


class TestPromotionPipeline:
    """Test the beat promotion pipeline."""
    
    @pytest.fixture
    def temp_output(self):
        """Create a temporary output directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def sample_beat_file(self, temp_output):
        """Create a sample beat file."""
        beat_id = "trap_140_C_minor_standard_20240101"
        beat_path = os.path.join(temp_output, f"{beat_id}_mix.wav")
        
        # Create empty file (just for path testing)
        with open(beat_path, 'w') as f:
            f.write("")
        
        return beat_id, beat_path
    
    def test_scan_finds_new_beats(self, temp_output, sample_beat_file):
        """Test that scan finds new beats via pipeline."""
        pipeline = PromotionPipeline(output_base=temp_output)
        
        # Verify pipeline stats are available
        stats = pipeline.get_pipeline_stats()
        assert 'output_directories' in stats
    
    def test_generate_metadata(self, temp_output):
        """Test metadata generation via pipeline."""
        pipeline = PromotionPipeline(output_base=temp_output)
        
        beat_info = {
            "beat_id": "trap_140_C_minor_standard_20240101",
            "genre": "trap",
            "bpm": 140,
            "key": "C",
            "scale": "minor"
        }
        
        seo_package = pipeline._generate_seo(beat_info)
        
        assert "titles" in seo_package
        assert "description" in seo_package
        assert "tags" in seo_package
        assert len(seo_package["titles"]) > 0
        assert "trap" in seo_package["titles"][0].lower() or "140" in seo_package["titles"][0]
    
    def test_generate_upload_plan(self, temp_output):
        """Test upload plan generation via pipeline."""
        pipeline = PromotionPipeline(output_base=temp_output)
        
        beat_info = {
            "beat_id": "trap_140_C_minor_standard",
            "file_path": "/tmp/test.wav",
            "genre": "trap",
            "bpm": 140,
            "key": "C",
            "scale": "minor"
        }
        
        # Run pipeline with video/shorts disabled for speed
        result = pipeline.process_beat(
            beat_info,
            generate_video=False,
            generate_thumbnails=False,
            generate_shorts=False
        )
        
        assert result["status"] in ("completed", "failed")
        assert "outputs" in result
        if result["status"] == "completed":
            assert "upload_plans" in result["outputs"]
            plans = result["outputs"]["upload_plans"]
            assert "youtube" in plans
            assert "tiktok" in plans
    
    def test_process_beat(self, temp_output, sample_beat_file):
        """Test full beat processing via pipeline."""
        pipeline = PromotionPipeline(output_base=temp_output)
        
        beat_id, beat_path = sample_beat_file
        beat_info = {
            "beat_id": beat_id,
            "file_path": beat_path,
            "genre": "trap",
            "bpm": 140,
            "key": "C",
            "scale": "minor",
            "structure": "standard",
            "timestamp": "20240101"
        }
        
        result = pipeline.process_beat(
            beat_info,
            generate_video=False,
            generate_thumbnails=False,
            generate_shorts=False
        )
        
        assert result["status"] in ("completed", "failed")
        assert "outputs" in result
    
    def test_pipeline_stats(self, temp_output):
        """Test pipeline stats retrieval."""
        pipeline = PromotionPipeline(output_base=temp_output)
        
        stats = pipeline.get_pipeline_stats()
        
        assert "output_directories" in stats
        assert "videos" in stats["output_directories"]
        assert "shorts" in stats["output_directories"]
        assert "thumbnails" in stats["output_directories"]


class TestContentCalendar:
    """Test the content calendar."""
    
    @pytest.fixture
    def temp_calendar(self):
        """Create a temporary calendar."""
        with tempfile.TemporaryDirectory() as tmpdir:
            calendar_path = os.path.join(tmpdir, "calendar.json")
            yield ContentCalendar(calendar_path=calendar_path)
    
    def test_schedule_beat(self, temp_calendar):
        """Test scheduling a beat."""
        metadata = {
            "title": "Test Beat",
            "description": "Test description",
            "tags": ["trap", "beat"]
        }
        
        schedules = temp_calendar.schedule_beat(
            "test_beat_001",
            ["youtube", "tiktok"],
            metadata
        )
        
        assert len(schedules) == 2
        assert schedules[0].platform == "youtube"
        assert schedules[1].platform == "tiktok"
        assert schedules[0].status == "pending"
    
    def test_get_ready_posts(self, temp_calendar):
        """Test getting ready posts."""
        # Schedule a post in the past
        past_time = datetime.now() - timedelta(hours=1)
        
        schedule = PostSchedule(
            beat_id="test_beat",
            platform="youtube",
            scheduled_time=past_time,
            content={"title": "Test"}
        )
        
        temp_calendar.schedules.append(schedule)
        temp_calendar.save_calendar()
        
        ready = temp_calendar.get_ready_posts()
        
        assert len(ready) == 1
        assert ready[0].status == "ready"
    
    def test_mark_posted(self, temp_calendar):
        """Test marking a post as posted."""
        schedule = PostSchedule(
            beat_id="test_beat",
            platform="youtube",
            scheduled_time=datetime.now(),
            content={"title": "Test"}
        )
        
        temp_calendar.schedules.append(schedule)
        temp_calendar.save_calendar()
        
        temp_calendar.mark_posted("test_beat", "youtube", "https://youtube.com/test")
        
        assert temp_calendar.schedules[0].status == "posted"
        assert temp_calendar.schedules[0].post_url == "https://youtube.com/test"
    
    def test_get_stats(self, temp_calendar):
        """Test getting statistics."""
        # Add some schedules
        for i in range(5):
            temp_calendar.schedules.append(PostSchedule(
                beat_id=f"beat_{i}",
                platform="youtube",
                scheduled_time=datetime.now(),
                content={}
            ))
        
        # Mark some as posted
        temp_calendar.schedules[0].status = "posted"
        temp_calendar.schedules[1].status = "posted"
        temp_calendar.schedules[2].status = "failed"
        
        stats = temp_calendar.get_stats()
        
        assert stats["total_posts"] == 5
        assert stats["posted"] == 2
        assert stats["failed"] == 1
        assert stats["pending"] == 2


class TestAnalyticsTracker:
    """Test analytics tracking."""
    
    @pytest.fixture
    def temp_analytics(self):
        """Create temporary analytics tracker."""
        with tempfile.TemporaryDirectory() as tmpdir:
            analytics_path = os.path.join(tmpdir, "analytics.json")
            yield AnalyticsTracker(analytics_path=analytics_path)
    
    def test_record_post(self, temp_analytics):
        """Test recording a post."""
        temp_analytics.record_post(
            "beat_001",
            "youtube",
            "https://youtube.com/test"
        )
        
        assert "beat_001" in temp_analytics.data
        assert "youtube" in temp_analytics.data["beat_001"]
        assert temp_analytics.data["beat_001"]["youtube"]["post_url"] == "https://youtube.com/test"
    
    def test_update_engagement(self, temp_analytics):
        """Test updating engagement metrics."""
        temp_analytics.record_post("beat_001", "youtube", "https://youtube.com/test")
        
        temp_analytics.update_engagement("beat_001", "youtube", {
            "views": 100,
            "likes": 10,
            "comments": 5
        })
        
        engagement = temp_analytics.data["beat_001"]["youtube"]["engagement"]
        assert engagement["views"] == 100
        assert engagement["likes"] == 10
        assert engagement["comments"] == 5
    
    def test_get_beat_performance(self, temp_analytics):
        """Test getting beat performance."""
        temp_analytics.record_post("beat_001", "youtube", "https://youtube.com/test")
        temp_analytics.record_post("beat_001", "tiktok", "https://tiktok.com/test")
        
        temp_analytics.update_engagement("beat_001", "youtube", {"views": 1000})
        temp_analytics.update_engagement("beat_001", "tiktok", {"views": 500})
        
        perf = temp_analytics.get_beat_performance("beat_001")
        
        assert perf["total_views"] == 1500
        assert perf["platform_count"] == 2
    
    def test_get_top_performers(self, temp_analytics):
        """Test getting top performers."""
        # Record multiple beats
        for i in range(3):
            temp_analytics.record_post(f"beat_{i}", "youtube", f"https://youtube.com/{i}")
            temp_analytics.update_engagement(f"beat_{i}", "youtube", {"views": (i + 1) * 100})
        
        top = temp_analytics.get_top_performers(limit=2)
        
        assert len(top) == 2
        assert top[0]["beat_id"] == "beat_2"  # 300 views
        assert top[1]["beat_id"] == "beat_1"  # 200 views
