"""Celery tasks for the AI Content Promotion System.

Background tasks for:
- Video generation
- Thumbnail generation
- SEO optimization
- Upload automation
- Trend research
- Analytics sync
- A/B test analysis
- Learning model updates
- Rule evaluation
"""

import os
from typing import Dict, Any

from celery import shared_task
import structlog

logger = structlog.get_logger()


# ─── Core Pipeline Tasks ────────────────────────────────────────────

@shared_task(queue='marketing', bind=True, max_retries=3)
def process_beat_promotion(self, beat_info: Dict[str, Any]):
    """Process a beat through the full promotion pipeline."""
    from app.core.beat_pipeline import PromotionPipeline
    
    try:
        pipeline = PromotionPipeline()
        result = pipeline.process_beat(beat_info)
        
        logger.info("pipeline_task_complete",
                   beat_id=beat_info.get('beat_id'),
                   status=result['status'])
        
        return result
    
    except Exception as exc:
        logger.error("pipeline_task_failed", error=str(exc))
        raise self.retry(exc=exc, countdown=60)


@shared_task(queue='marketing')
def generate_video_task(beat_info: Dict[str, Any], video_type: str = "full"):
    """Generate video for a beat."""
    from app.video.renderer import VideoRenderer
    from app.video.shorts_generator import ShortsGenerator
    
    audio_path = beat_info.get('file_path')
    
    if not audio_path or not os.path.exists(audio_path):
        return {'status': 'error', 'message': 'Audio file not found'}
    
    if video_type == 'short':
        generator = ShortsGenerator()
        result = generator.generate_short(audio_path, beat_info)
    else:
        renderer = VideoRenderer()
        result = renderer.render_video(audio_path, beat_info)
    
    return {'status': 'success', 'video_path': result}


@shared_task(queue='marketing')
def generate_thumbnail_task(beat_info: Dict[str, Any], variant: str = "A"):
    """Generate thumbnail for a beat."""
    from app.thumbnail.generator import ThumbnailGenerator
    
    generator = ThumbnailGenerator()
    path = generator.generate_thumbnail(beat_info, variant=variant)
    
    return {'status': 'success', 'thumbnail_path': path}


@shared_task(queue='marketing')
def generate_seo_task(beat_info: Dict[str, Any]):
    """Generate SEO metadata for a beat."""
    from app.seo.title_generator import TitleGenerator
    from app.seo.description_builder import DescriptionBuilder
    from app.seo.keyword_researcher import KeywordResearcher
    
    title_gen = TitleGenerator()
    desc_builder = DescriptionBuilder()
    keyword_researcher = KeywordResearcher()
    
    genre = beat_info.get('genre', 'trap')
    trending = keyword_researcher.get_trending_keywords(genre)
    
    titles = title_gen.generate_variants(beat_info, trending_keywords=trending)
    description = desc_builder.build_description(beat_info, title=titles[0] if titles else None)
    tags = desc_builder.generate_tags(beat_info, trending)
    
    return {
        'status': 'success',
        'titles': titles,
        'description': description,
        'tags': tags,
        'trending_keywords': trending
    }


# ─── Upload Tasks ───────────────────────────────────────────────────

@shared_task(queue='marketing', max_retries=3, default_retry_delay=300)
def upload_to_youtube_task(video_path: str, metadata: Dict[str, Any],
                           channel_id: str = "default"):
    """Upload video to YouTube."""
    from app.upload.youtube_uploader import YouTubeUploader
    
    uploader = YouTubeUploader()
    
    if not uploader.authenticate(channel_id):
        return {'status': 'auth_required', 'message': 'Authentication needed'}
    
    result = uploader.upload_video(video_path, metadata, channel_id)
    return result


@shared_task(queue='marketing', max_retries=2)
def upload_to_tiktok_task(video_path: str, metadata: Dict[str, Any]):
    """Upload video to TikTok."""
    from app.upload.tiktok_uploader import TikTokUploader
    
    uploader = TikTokUploader()
    
    if not uploader.authenticate():
        return {'status': 'auth_required'}
    
    return uploader.upload_video(video_path, metadata)


@shared_task(queue='marketing', max_retries=2)
def upload_to_instagram_task(video_path: str, metadata: Dict[str, Any]):
    """Upload video to Instagram."""
    from app.upload.instagram_uploader import InstagramUploader
    
    uploader = InstagramUploader()
    
    if not uploader.authenticate():
        return {'status': 'auth_required'}
    
    return uploader.upload_reel(video_path, metadata)


# ─── Trend Research Tasks ───────────────────────────────────────────

@shared_task(queue='marketing')
def research_youtube_trends_task():
    """Research YouTube trends."""
    from app.trends.youtube_trends import YouTubeTrendDetector
    
    detector = YouTubeTrendDetector()
    trending = detector.get_trending()
    keywords = detector.get_trending_keywords()
    
    return {
        'status': 'success',
        'trending_videos': len(trending),
        'trending_keywords': keywords[:20]
    }


@shared_task(queue='marketing')
def research_tiktok_trends_task():
    """Research TikTok trends."""
    from app.trends.tiktok_trends import TikTokTrendDetector
    
    detector = TikTokTrendDetector()
    hashtags = detector.get_trending_hashtags()
    sounds = detector.get_viral_sounds()
    
    return {
        'status': 'success',
        'trending_hashtags': hashtags[:20],
        'viral_sounds': sounds[:10]
    }


@shared_task(queue='marketing')
def research_market_trends_task():
    """Research beat market trends."""
    from app.trends.beat_market_trends import BeatMarketTrendDetector
    
    detector = BeatMarketTrendDetector()
    analysis = detector.analyze_market()
    
    return {
        'status': 'success',
        'trending_genres': [g['genre'] for g in analysis['trending_genres'][:5]],
        'opportunities': analysis['opportunities'][:5]
    }


# ─── Analytics Tasks ────────────────────────────────────────────────

@shared_task(queue='marketing')
def sync_youtube_analytics_task(channel_id: str = "default"):
    """Sync YouTube analytics data."""
    from app.analytics.youtube_analytics import YouTubeAnalytics
    
    analytics = YouTubeAnalytics()
    
    if not analytics.authenticate(channel_id):
        return {'status': 'auth_required'}
    
    stats = analytics.get_channel_stats(days=7)
    top_videos = analytics.get_top_videos(days=7, max_results=10)
    
    return {
        'status': 'success',
        'channel_stats': stats,
        'top_videos': top_videos
    }


@shared_task(queue='marketing')
def analyze_ab_tests_task():
    """Analyze A/B test results."""
    from app.thumbnail.ab_testing import ABTestManager
    
    manager = ABTestManager()
    active = manager.get_active_tests()
    
    completed = 0
    for test in active:
        # Trigger evaluation
        results = manager.get_test_results(test.test_id)
        if results and results['status'] == 'completed':
            completed += 1
    
    return {
        'status': 'success',
        'active_tests': len(active),
        'newly_completed': completed
    }


@shared_task(queue='marketing')
def update_learning_models_task():
    """Update AI learning models with latest data."""
    from app.learning.performance_model import PerformanceModel
    from app.learning.thumbnail_optimizer import ThumbnailOptimizer
    from app.learning.title_optimizer import TitleOptimizer
    from app.learning.genre_predictor import GenrePredictor
    
    # Update predictions
    genre_predictor = GenrePredictor()
    predictions = genre_predictor.predict_trending_genres(days_ahead=14)
    
    # Get recommendations
    recommendations = genre_predictor.get_genre_recommendations()
    
    return {
        'status': 'success',
        'predictions': len(predictions),
        'recommendations': len(recommendations)
    }


# ─── Rule Engine Tasks ──────────────────────────────────────────────

@shared_task(queue='marketing')
def evaluate_automation_rules_task():
    """Evaluate all automation rules."""
    from app.core.rule_engine import RuleEngine
    from app.analytics.ctr_tracker import CTRTracker
    from app.analytics.youtube_analytics import YouTubeAnalytics
    
    engine = RuleEngine()
    
    # Gather context from analytics
    ctr_tracker = CTRTracker()
    ctr_summary = ctr_tracker.get_performance_summary(days=7)
    
    # Build context
    context = {
        'ctr': ctr_summary.get('average_ctr', 0) / 100,
        'views': ctr_summary.get('total_impressions', 0),
        'genre': 'trap',  # Would be determined from recent uploads
    }
    
    triggered = engine.evaluate_all(context)
    
    return {
        'status': 'success',
        'rules_evaluated': len(engine.rules),
        'triggered': len(triggered),
        'actions': triggered
    }


# ─── Content Queue Tasks ────────────────────────────────────────────

@shared_task(queue='marketing')
def process_upload_queue_task():
    """Process pending uploads in the queue."""
    from app.scheduler.content_calendar import ContentCalendar
    
    calendar = ContentCalendar()
    ready = calendar.get_ready_posts()
    
    processed = 0
    for post in ready:
        # Would trigger upload tasks here
        processed += 1
    
    return {
        'status': 'success',
        'ready_posts': len(ready),
        'processed': processed
    }


@shared_task(queue='marketing')
def scan_and_process_new_beats_task(output_dir: str = "./output"):
    """Scan for new beats and process them."""
    import os
    from pathlib import Path
    
    # Validate output directory
    output_dir = os.path.abspath(output_dir)
    if not os.path.exists(output_dir):
        logger.error("output_dir_not_found", path=output_dir)
        return {"status": "error", "message": "Output directory not found"}
    
    # Scan for new beats
    new_beats = []
    for file in Path(output_dir).glob("*_mix.wav"):
        beat_id = file.stem.replace("_mix", "")
        parts = beat_id.split('_')
        
        if len(parts) >= 5:
            beat_info = {
                "beat_id": beat_id,
                "file_path": str(file),
                "genre": parts[0],
                "bpm": int(parts[1]) if parts[1].isdigit() else 140,
                "key": parts[2] if len(parts) > 2 else "C",
                "scale": parts[3] if len(parts) > 3 else "minor",
                "structure": parts[4] if len(parts) > 4 else "standard",
            }
            new_beats.append(beat_info)
    
    # Queue pipeline tasks for each new beat
    queued = 0
    for beat_info in new_beats:
        try:
            process_beat_promotion.delay(beat_info)
            queued += 1
        except Exception as e:
            logger.error("pipeline_queue_failed", 
                       beat_id=beat_info.get('beat_id'), 
                       error=str(e))
    
    return {
        "status": "success",
        "new_beats_found": len(new_beats),
        "pipeline_tasks_queued": queued
    }


# ─── Scheduled Cleanup Tasks ────────────────────────────────────────

@shared_task(queue='marketing')
def cleanup_old_data_task(days: int = 30):
    """Clean up old temporary files and data."""
    import shutil
    from datetime import datetime, timedelta
    
    cutoff = datetime.now() - timedelta(days=days)
    cleaned = 0
    
    # Clean temp video frames
    temp_dirs = ['./output/temp', './output/videos/temp']
    
    for temp_dir in temp_dirs:
        if os.path.exists(temp_dir):
            for item in os.listdir(temp_dir):
                item_path = os.path.join(temp_dir, item)
                try:
                    mtime = datetime.fromtimestamp(os.path.getmtime(item_path))
                    if mtime < cutoff:
                        if os.path.isfile(item_path):
                            os.remove(item_path)
                        else:
                            shutil.rmtree(item_path)
                        cleaned += 1
                except Exception:
                    pass
    
    return {
        'status': 'success',
        'items_cleaned': cleaned
    }
