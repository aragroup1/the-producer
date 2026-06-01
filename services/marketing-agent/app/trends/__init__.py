"""Trend Detection Engine."""

from .youtube_trends import YouTubeTrendDetector
from .tiktok_trends import TikTokTrendDetector
from .google_trends import GoogleTrendDetector
from .beat_market_trends import BeatMarketTrendDetector

__all__ = [
    "YouTubeTrendDetector",
    "TikTokTrendDetector",
    "GoogleTrendDetector",
    "BeatMarketTrendDetector",
]
