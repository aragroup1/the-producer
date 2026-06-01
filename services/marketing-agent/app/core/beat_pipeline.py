"""Promotion Pipeline — Orchestrates the full beat promotion workflow.

Flow: Beat → Metadata → Video → Thumbnail → Upload Plan → Schedule
"""

import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import structlog

from app.video.renderer import VideoRenderer
from app.video.shorts_generator import ShortsGenerator
from app.thumbnail.generator import ThumbnailGenerator
from app.seo.title_generator import TitleGenerator
from app.seo.description_builder import DescriptionBuilder
from app.seo.keyword_researcher import KeywordResearcher

logger = structlog.get_logger()


class PromotionPipeline:
    """Orchestrate full promotion pipeline for a beat."""
    
    def __init__(self, output_base: str = "./output"):
        self.output_base = output_base
        
        # Sub-engines
        self.video_renderer = VideoRenderer(output_dir=os.path.join(output_base, "videos"))
        self.shorts_generator = ShortsGenerator(output_dir=os.path.join(output_base, "videos", "shorts"))
        self.thumbnail_generator = ThumbnailGenerator(output_dir=os.path.join(output_base, "thumbnails"))
        self.title_generator = TitleGenerator()
        self.description_builder = DescriptionBuilder()
        self.keyword_researcher = KeywordResearcher()
    
    def process_beat(self, beat_info: Dict[str, Any],
                     generate_video: bool = True,
                     generate_thumbnails: bool = True,
                     generate_shorts: bool = True,
                     variant_count: int = 3) -> Dict[str, Any]:
        """Process a single beat through the full pipeline.
        
        Args:
            beat_info: Beat metadata
            generate_video: Generate full video
            generate_thumbnails: Generate thumbnail variants
            generate_shorts: Generate short-form videos
            variant_count: Number of thumbnail variants
        
        Returns:
            Complete promotion package
        """
        beat_id = beat_info.get('beat_id', 'unknown')
        logger.info("pipeline_started", beat_id=beat_id)
        
        result = {
            'beat_id': beat_id,
            'status': 'processing',
            'started_at': datetime.now().isoformat(),
            'outputs': {}
        }
        
        try:
            # Step 1: Generate SEO metadata
            logger.info("step_seo_metadata", beat_id=beat_id)
            seo_package = self._generate_seo(beat_info)
            result['outputs']['seo'] = seo_package
            
            # Step 2: Generate thumbnails
            if generate_thumbnails:
                logger.info("step_thumbnails", beat_id=beat_id)
                thumbnail_paths = self.thumbnail_generator.generate_variants(
                    beat_info, count=variant_count
                )
                result['outputs']['thumbnails'] = thumbnail_paths
            
            # Step 3: Generate full video
            if generate_video:
                logger.info("step_video", beat_id=beat_id)
                audio_path = beat_info.get('file_path')
                if audio_path and os.path.exists(audio_path):
                    video_path = self.video_renderer.render_video(
                        audio_path,
                        beat_info
                    )
                    result['outputs']['video'] = video_path
                else:
                    logger.warning("audio_not_found", 
                                 beat_id=beat_id, 
                                 path=audio_path)
            
            # Step 4: Generate shorts
            if generate_shorts:
                logger.info("step_shorts", beat_id=beat_id)
                audio_path = beat_info.get('file_path')
                if audio_path and os.path.exists(audio_path):
                    shorts = self.shorts_generator.generate_all_platforms(
                        audio_path, beat_info
                    )
                    result['outputs']['shorts'] = shorts
            
            # Step 5: Build upload plans
            logger.info("step_upload_plans", beat_id=beat_id)
            upload_plans = self._build_upload_plans(result)
            result['outputs']['upload_plans'] = upload_plans
            
            result['status'] = 'completed'
            result['completed_at'] = datetime.now().isoformat()
            
            logger.info("pipeline_completed", beat_id=beat_id)
        
        except Exception as e:
            logger.error("pipeline_failed", beat_id=beat_id, error=str(e))
            result['status'] = 'failed'
            result['error'] = str(e)
        
        return result
    
    def _generate_seo(self, beat_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete SEO package."""
        # Research keywords
        genre = beat_info.get('genre', 'trap')
        trending_keywords = self.keyword_researcher.get_trending_keywords(genre)
        
        # Generate titles
        titles = self.title_generator.generate_variants(
            beat_info, 
            count=3,
            trending_keywords=trending_keywords
        )
        
        # Generate descriptions (use first title or fallback)
        primary_title = titles[0] if titles else f"{beat_info.get('genre', 'Beat').title()} Type Beat"
        description = self.description_builder.build_description(beat_info, title=primary_title)
        shorts_description = self.description_builder.build_shorts_description(beat_info)
        
        # Generate tags
        tags = self.description_builder.generate_tags(beat_info, trending_keywords)
        
        return {
            'titles': titles,
            'description': description,
            'shorts_description': shorts_description,
            'tags': tags,
            'trending_keywords': trending_keywords,
            'primary_title': titles[0] if titles else '',
            'hashtags': self._extract_hashtags(description)
        }
    
    def _build_upload_plans(self, pipeline_result: Dict[str, Any]) -> Dict[str, Any]:
        """Build upload plans for all platforms."""
        seo = pipeline_result['outputs'].get('seo', {})
        video = pipeline_result['outputs'].get('video')
        thumbnails = pipeline_result['outputs'].get('thumbnails', [])
        shorts = pipeline_result['outputs'].get('shorts', {})
        
        beat_id = pipeline_result['beat_id']
        
        plans = {
            'youtube': {
                'platform': 'youtube',
                'title': seo.get('primary_title', ''),
                'description': seo.get('description', ''),
                'tags': seo.get('tags', []),
                'category': 'Music',
                'privacy': 'public',
                'video_path': video,
                'thumbnail_path': thumbnails[0] if thumbnails else None,
                'made_for_kids': False
            },
            'youtube_shorts': {
                'platform': 'youtube_shorts',
                'title': seo.get('primary_title', '') + ' #Shorts',
                'description': seo.get('shorts_description', ''),
                'tags': seo.get('tags', [])[:10],
                'video_path': shorts.get('youtube_shorts'),
                'category': 'Music',
                'privacy': 'public'
            },
            'tiktok': {
                'platform': 'tiktok',
                'caption': f"{seo.get('primary_title', '')}\n\n{seo.get('hashtags', '')}",
                'video_path': shorts.get('tiktok'),
                'allow_duet': True,
                'allow_stitch': True
            },
            'instagram_reels': {
                'platform': 'instagram_reels',
                'caption': f"{seo.get('primary_title', '')}\n\n{seo.get('hashtags', '')}",
                'video_path': shorts.get('instagram_reels'),
                'share_to_feed': True
            }
        }
        
        return plans
    
    def _extract_hashtags(self, text: str) -> str:
        """Extract hashtags from text."""
        import re
        hashtags = re.findall(r'#\w+', text)
        return ' '.join(hashtags)
    
    def batch_process(self, beat_infos: List[Dict[str, Any]],
                      max_parallel: int = 4) -> List[Dict[str, Any]]:
        """Process multiple beats in batch.
        
        Args:
            beat_infos: List of beat metadata dicts
            max_parallel: Max concurrent processing (for Celery)
        
        Returns:
            List of promotion results
        """
        results = []
        
        for beat_info in beat_infos:
            try:
                result = self.process_beat(beat_info)
                results.append(result)
            except Exception as e:
                logger.error("batch_process_failed", 
                           beat_id=beat_info.get('beat_id'), 
                           error=str(e))
                results.append({
                    'beat_id': beat_info.get('beat_id'),
                    'status': 'failed',
                    'error': str(e)
                })
        
        return results
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics."""
        return {
            'video_renderer_available': self.video_renderer.ffmpeg_available,
            'output_directories': {
                'videos': self.video_renderer.output_dir,
                'shorts': self.shorts_generator.output_dir,
                'thumbnails': self.thumbnail_generator.output_dir,
            }
        }
