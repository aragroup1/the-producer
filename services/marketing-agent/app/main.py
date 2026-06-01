"""FastAPI service for the AI Content Promotion System.

Provides REST API for:
- Beat promotion pipeline
- Video generation
- Thumbnail generation
- SEO optimization
- Upload automation
- Multi-channel management
- Trend detection
- Analytics
- AI learning
- Automation rules
"""

import os
from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel, Field

from app.core.beat_pipeline import PromotionPipeline
from app.core.channel_manager import ChannelManager
from app.core.rule_engine import RuleEngine
from app.video.renderer import VideoRenderer
from app.video.shorts_generator import ShortsGenerator
from app.thumbnail.generator import ThumbnailGenerator
from app.seo.title_generator import TitleGenerator
from app.seo.description_builder import DescriptionBuilder
from app.seo.keyword_researcher import KeywordResearcher
from app.trends.youtube_trends import YouTubeTrendDetector
from app.trends.tiktok_trends import TikTokTrendDetector
from app.trends.google_trends import GoogleTrendDetector
from app.trends.beat_market_trends import BeatMarketTrendDetector
from app.analytics.ctr_tracker import CTRTracker
from app.learning.performance_model import PerformanceModel
from app.learning.genre_predictor import GenrePredictor
import structlog

logger = structlog.get_logger()

app = FastAPI(
    title="AI Content Promotion System",
    description="Autonomous AI growth engine for music marketing",
    version="2.0.0"
)

# Global engine instances
pipeline = PromotionPipeline()
channel_manager = ChannelManager()
rule_engine = RuleEngine()
video_renderer = VideoRenderer()
shorts_generator = ShortsGenerator()
thumbnail_generator = ThumbnailGenerator()
title_generator = TitleGenerator()
description_builder = DescriptionBuilder()
keyword_researcher = KeywordResearcher()
youtube_trends = YouTubeTrendDetector()
tiktok_trends = TikTokTrendDetector()
google_trends = GoogleTrendDetector()
beat_market = BeatMarketTrendDetector()
ctr_tracker = CTRTracker()
performance_model = PerformanceModel()
genre_predictor = GenrePredictor()


# ─── Pydantic Models ─────────────────────────────────────────────────

class BeatInfo(BaseModel):
    beat_id: str
    genre: str = "trap"
    bpm: int = 140
    key: str = "C"
    scale: str = "minor"
    mood: str = "dark"
    file_path: Optional[str] = None
    title: Optional[str] = None


class PipelineRequest(BaseModel):
    beat: BeatInfo
    generate_video: bool = True
    generate_thumbnails: bool = True
    generate_shorts: bool = True
    thumbnail_variants: int = 3


class VideoRequest(BaseModel):
    audio_path: str
    beat_info: BeatInfo
    template_name: Optional[str] = None
    duration: Optional[float] = None


class ShortRequest(BaseModel):
    audio_path: str
    beat_info: BeatInfo
    platform: str = "youtube_shorts"
    duration: Optional[float] = None


class ThumbnailRequest(BaseModel):
    beat_info: BeatInfo
    variant: str = "A"
    preset_name: Optional[str] = None


class SEORequest(BaseModel):
    beat_info: BeatInfo
    platform: str = "youtube"
    trending_keywords: Optional[List[str]] = None


class UploadRequest(BaseModel):
    video_path: str
    metadata: Dict[str, Any]
    platform: str = "youtube"
    channel_id: Optional[str] = None


class RuleCreateRequest(BaseModel):
    name: str
    description: str
    conditions: List[Dict[str, Any]]
    logical_op: str = "and"
    actions: List[Dict[str, Any]]
    cooldown_hours: int = 24


class CTRRecordRequest(BaseModel):
    video_id: str
    impressions: int
    clicks: int
    thumbnail_variant: str = "A"
    title_variant: str = "A"


# ─── Health & Status ────────────────────────────────────────────────

@app.get("/")
async def root():
    """Service health check."""
    return {
        "service": "ai-content-promotion",
        "status": "running",
        "version": "2.0.0",
        "engines": {
            "video_renderer": video_renderer.ffmpeg_available,
            "pipeline": True,
            "channels": len(channel_manager.channels),
            "rules": len(rule_engine.rules)
        }
    }


@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "pipeline_stats": pipeline.get_pipeline_stats()
    }


# ─── Pipeline Endpoints ─────────────────────────────────────────────

@app.post("/pipeline/process")
async def process_beat(request: PipelineRequest):
    """Process a beat through the full promotion pipeline."""
    beat_info = request.beat.model_dump()
    
    result = pipeline.process_beat(
        beat_info,
        generate_video=request.generate_video,
        generate_thumbnails=request.generate_thumbnails,
        generate_shorts=request.generate_shorts,
        variant_count=request.thumbnail_variants
    )
    
    return result


@app.post("/pipeline/batch")
async def batch_process(beats: List[BeatInfo]):
    """Process multiple beats in batch."""
    beat_infos = [b.model_dump() for b in beats]
    results = pipeline.batch_process(beat_infos)
    
    return {
        "processed": len(results),
        "successful": sum(1 for r in results if r['status'] == 'completed'),
        "failed": sum(1 for r in results if r['status'] == 'failed'),
        "results": results
    }


# ─── Video Endpoints ────────────────────────────────────────────────

@app.post("/videos/generate")
async def generate_video(request: VideoRequest):
    """Generate a video from audio."""
    beat_info = request.beat_info.model_dump()
    
    video_path = video_renderer.render_video(
        request.audio_path,
        beat_info,
        template_name=request.template_name,
        duration=request.duration
    )
    
    if not video_path:
        raise HTTPException(status_code=500, detail="Video generation failed")
    
    return {
        "status": "success",
        "video_path": video_path,
        "info": video_renderer.get_video_info(video_path)
    }


@app.post("/videos/shorts/generate")
async def generate_short(request: ShortRequest):
    """Generate a short-form video."""
    beat_info = request.beat_info.model_dump()
    
    short_path = shorts_generator.generate_short(
        request.audio_path,
        beat_info,
        platform=request.platform,
        duration=request.duration
    )
    
    if not short_path:
        raise HTTPException(status_code=500, detail="Short generation failed")
    
    return {
        "status": "success",
        "platform": request.platform,
        "video_path": short_path
    }


@app.post("/videos/shorts/all")
async def generate_all_shorts(audio_path: str, beat_info: BeatInfo):
    """Generate shorts for all platforms."""
    results = shorts_generator.generate_all_platforms(
        audio_path,
        beat_info.model_dump()
    )
    
    return {
        "status": "success",
        "shorts": results
    }


# ─── Thumbnail Endpoints ────────────────────────────────────────────

@app.post("/thumbnails/generate")
async def generate_thumbnail(request: ThumbnailRequest):
    """Generate a thumbnail."""
    beat_info = request.beat_info.model_dump()
    
    path = thumbnail_generator.generate_thumbnail(
        beat_info,
        variant=request.variant,
        preset_name=request.preset_name
    )
    
    if not path:
        raise HTTPException(status_code=500, detail="Thumbnail generation failed")
    
    # Score the thumbnail
    score = thumbnail_generator.get_thumbnail_score(path)
    
    return {
        "status": "success",
        "thumbnail_path": path,
        "score": score
    }


@app.post("/thumbnails/variants")
async def generate_thumbnail_variants(beat_info: BeatInfo, count: int = 3):
    """Generate multiple thumbnail variants."""
    paths = thumbnail_generator.generate_variants(
        beat_info.model_dump(),
        count=count
    )
    
    return {
        "status": "success",
        "variants": paths,
        "scores": [thumbnail_generator.get_thumbnail_score(p) for p in paths]
    }


# ─── SEO Endpoints ──────────────────────────────────────────────────

@app.post("/seo/titles")
async def generate_titles(request: SEORequest):
    """Generate optimized titles."""
    beat_info = request.beat_info.model_dump()
    
    titles = title_generator.generate_variants(
        beat_info,
        count=3,
        trending_keywords=request.trending_keywords
    )
    
    scored_titles = [
        {
            'title': t,
            'scores': title_generator.score_title(t, beat_info)
        }
        for t in titles
    ]
    
    return {
        "status": "success",
        "titles": scored_titles
    }


@app.post("/seo/description")
async def generate_description(beat_info: BeatInfo, 
                                title: Optional[str] = None):
    """Generate optimized description."""
    description = description_builder.build_description(
        beat_info.model_dump(),
        title=title
    )
    
    return {
        "status": "success",
        "description": description,
        "scores": description_builder.score_description(description)
    }


@app.post("/seo/tags")
async def generate_tags(beat_info: BeatInfo,
                        trending_keywords: Optional[List[str]] = None):
    """Generate optimized tags."""
    tags = description_builder.generate_tags(
        beat_info.model_dump(),
        trending_keywords
    )
    
    return {
        "status": "success",
        "tags": tags,
        "total_length": sum(len(t) for t in tags)
    }


@app.get("/seo/keywords/research")
async def research_keywords(genre: str):
    """Research keywords for a genre."""
    keywords = keyword_researcher.research_genre_keywords(genre)
    
    return {
        "status": "success",
        "genre": genre,
        "keywords": [
            {
                'keyword': kw.keyword,
                'estimated_volume': kw.search_volume,
                'difficulty': kw.difficulty,
                'trend_score': kw.trend_score
            }
            for kw in keywords[:10]
        ]
    }


@app.get("/seo/keywords/trending")
async def get_trending_keywords(genre: str):
    """Get trending keywords for a genre."""
    keywords = keyword_researcher.get_trending_keywords(genre)
    
    return {
        "status": "success",
        "genre": genre,
        "trending_keywords": keywords
    }


# ─── Channel Management Endpoints ───────────────────────────────────

@app.get("/channels")
async def list_channels():
    """List all channels."""
    return {
        "channels": [
            {
                'id': ch.id,
                'name': ch.name,
                'platform': ch.platform.value,
                'niche': ch.niche,
                'upload_frequency': ch.upload_frequency,
                'is_active': ch.is_active
            }
            for ch in channel_manager.channels.values()
        ]
    }


@app.get("/channels/{channel_id}/stats")
async def get_channel_stats(channel_id: str):
    """Get channel statistics."""
    stats = channel_manager.get_channel_stats(channel_id)
    
    if not stats:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    return stats


@app.get("/channels/{channel_id}/schedule")
async def get_channel_schedule(channel_id: str, days: int = 7):
    """Get upload schedule for a channel."""
    schedule = channel_manager.get_upload_schedule(channel_id, days=days)
    
    return {
        "channel_id": channel_id,
        "schedule": schedule
    }


@app.post("/channels/assign")
async def assign_beat_to_channel(beat_info: BeatInfo):
    """Find the best channel for a beat."""
    channel = channel_manager.assign_beat_to_channel(beat_info.model_dump())
    
    if not channel:
        return {"status": "no_channel", "message": "No suitable channel found"}
    
    return {
        "status": "success",
        "channel": {
            'id': channel.id,
            'name': channel.name,
            'niche': channel.niche,
            'platform': channel.platform.value
        }
    }


# ─── Trend Detection Endpoints ──────────────────────────────────────

@app.get("/trends/youtube")
async def get_youtube_trends():
    """Get YouTube trending data."""
    trending = youtube_trends.get_trending()
    keywords = youtube_trends.get_trending_keywords()
    
    return {
        "trending_videos": [
            {
                'title': v.title,
                'channel': v.channel,
                'rank': v.rank
            }
            for v in trending[:10]
        ],
        "trending_keywords": keywords[:10]
    }


@app.get("/trends/tiktok")
async def get_tiktok_trends():
    """Get TikTok trending data."""
    hashtags = tiktok_trends.get_trending_hashtags()
    sounds = tiktok_trends.get_viral_sounds()
    
    return {
        "trending_hashtags": hashtags[:10],
        "viral_sounds": sounds[:5]
    }


@app.get("/trends/market")
async def get_market_trends():
    """Get beat market trends."""
    analysis = beat_market.analyze_market()
    
    return analysis


@app.get("/trends/genre/{genre}")
async def get_genre_trends(genre: str):
    """Get trends for a specific genre."""
    youtube_kw = youtube_trends.get_search_trends(f"{genre} type beat")
    tiktok_trend = tiktok_trends.get_trending_for_genre(genre)
    
    return {
        "genre": genre,
        "youtube_searches": youtube_kw[:10],
        "tiktok_hashtags": tiktok_trend[:10]
    }


# ─── Analytics Endpoints ────────────────────────────────────────────

@app.post("/analytics/ctr")
async def record_ctr(request: CTRRecordRequest):
    """Record CTR data."""
    ctr_tracker.record_ctr(
        request.video_id,
        request.impressions,
        request.clicks,
        request.thumbnail_variant,
        request.title_variant
    )
    
    return {"status": "success"}


@app.get("/analytics/ctr/summary")
async def get_ctr_summary(days: int = 30):
    """Get CTR performance summary."""
    return ctr_tracker.get_performance_summary(days=days)


@app.get("/analytics/ctr/recommendations")
async def get_ctr_recommendations():
    """Get CTR improvement recommendations."""
    return {"recommendations": ctr_tracker.get_recommendations()}


@app.get("/analytics/ctr/variants")
async def get_variant_performance(variant_type: str = "thumbnail"):
    """Get A/B variant performance."""
    return ctr_tracker.get_variant_performance(variant_type)


# ─── AI Learning Endpoints ──────────────────────────────────────────

@app.get("/learning/genre-predictions")
async def get_genre_predictions(days_ahead: int = 14):
    """Get genre trend predictions."""
    predictions = genre_predictor.predict_trending_genres(days_ahead)
    
    return {
        "predictions": predictions,
        "generated_at": datetime.now().isoformat()
    }


@app.get("/learning/genre-recommendations")
async def get_genre_recommendations():
    """Get genre production recommendations."""
    recommendations = genre_predictor.get_genre_recommendations()
    
    return {
        "recommendations": recommendations
    }


@app.get("/learning/performance")
async def get_performance_insights(genre: Optional[str] = None):
    """Get performance insights."""
    return performance_model.get_best_practices(genre)


# ─── Automation Rules Endpoints ─────────────────────────────────────

@app.get("/rules")
async def list_rules():
    """List all automation rules."""
    return rule_engine.list_rules()


@app.post("/rules")
async def create_rule(request: RuleCreateRequest):
    """Create a new automation rule."""
    from app.core.rule_engine import Rule, Condition
    
    conditions = [Condition(**c) for c in request.conditions]
    
    rule = Rule(
        id=f"custom_{datetime.now().timestamp()}",
        name=request.name,
        description=request.description,
        conditions=conditions,
        logical_op=request.logical_op,
        actions=request.actions,
        cooldown_hours=request.cooldown_hours
    )
    
    rule_engine.add_rule(rule)
    
    return {"status": "success", "rule_id": rule.id}


@app.post("/rules/{rule_id}/toggle")
async def toggle_rule(rule_id: str):
    """Toggle rule enabled/disabled."""
    rule = rule_engine.get_rule(rule_id)
    
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    if rule.enabled:
        rule_engine.disable_rule(rule_id)
    else:
        rule_engine.enable_rule(rule_id)
    
    return {"status": "success", "enabled": not rule.enabled}


@app.get("/rules/stats")
async def get_rule_stats():
    """Get rule engine statistics."""
    return rule_engine.get_stats()


@app.post("/rules/evaluate")
async def evaluate_rules(context: Dict[str, Any]):
    """Manually evaluate rules with context."""
    # Sanitize context - only allow known metric keys
    allowed_metrics = {
        'ctr', 'views', 'genre', 'mood', 'bpm', 'trend_score',
        'day_of_week', 'impressions', 'clicks', 'ab_test_confidence',
        'ab_test_ctr_improvement', 'trend_keyword', 'trend_growth',
        'views_per_hour', 'subscriber_conversion'
    }
    
    sanitized = {}
    for key, value in context.items():
        if key in allowed_metrics:
            sanitized[key] = value
    
    triggered = rule_engine.evaluate_all(sanitized)
    
    return {
        "triggered_rules": len(triggered),
        "actions": triggered
    }


# ─── Upload Endpoints ───────────────────────────────────────────────

@app.post("/upload/youtube")
async def upload_youtube(request: UploadRequest):
    """Upload to YouTube."""
    from app.upload.youtube_uploader import YouTubeUploader
    import os
    
    # Validate video path
    video_path = request.video_path
    if not os.path.exists(video_path):
        raise HTTPException(status_code=400, detail="Video file not found")
    
    # Prevent path traversal
    video_path = os.path.abspath(video_path)
    if not video_path.startswith(os.path.abspath("./output")) and not video_path.startswith(os.path.abspath("./")):
        raise HTTPException(status_code=400, detail="Invalid video path")
    
    uploader = YouTubeUploader()
    
    if not uploader.authenticate(request.channel_id or "default"):
        return {
            "status": "auth_required",
            "message": "YouTube authentication required. Provide client_secrets.json"
        }
    
    result = uploader.upload_video(
        video_path,
        request.metadata,
        request.channel_id or "default"
    )
    
    return result


# ─── Background Tasks ───────────────────────────────────────────────

@app.post("/pipeline/run-all")
async def run_full_pipeline(background_tasks: BackgroundTasks):
    """Run full pipeline for all pending beats."""
    background_tasks.add_task(_auto_pipeline_task)
    
    return {
        "status": "started",
        "message": "Pipeline running in background"
    }


def _auto_pipeline_task():
    """Background task to process pending beats."""
    import os
    from pathlib import Path
    
    # Scan for new beats
    output_dir = os.path.abspath("./output")
    if not os.path.exists(output_dir):
        logger.warning("output_dir_not_found", path=output_dir)
        return
    
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
    
    for beat_info in new_beats:
        try:
            pipeline.process_beat(beat_info)
        except Exception as e:
            logger.error("auto_pipeline_failed", 
                       beat_id=beat_info.get('beat_id'), 
                       error=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
