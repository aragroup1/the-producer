"""Marketing Agent — Automated beat promotion and distribution."""

# Core pipeline
from .core.beat_pipeline import PromotionPipeline
from .core.channel_manager import ChannelManager
from .core.rule_engine import RuleEngine

# Video
from .video.renderer import VideoRenderer
from .video.shorts_generator import ShortsGenerator

# Thumbnail
from .thumbnail.generator import ThumbnailGenerator
from .thumbnail.ab_testing import ABTestManager

# SEO
from .seo.title_generator import TitleGenerator
from .seo.description_builder import DescriptionBuilder

__all__ = [
    "PromotionPipeline",
    "ChannelManager",
    "RuleEngine",
    "VideoRenderer",
    "ShortsGenerator",
    "ThumbnailGenerator",
    "ABTestManager",
    "TitleGenerator",
    "DescriptionBuilder",
]
