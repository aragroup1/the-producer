"""Video Generation Engine — FFmpeg-based music video renderer."""

from .renderer import VideoRenderer
from .visualizers import WaveformVisualizer, SpectrumVisualizer, ParticleVisualizer
from .shorts_generator import ShortsGenerator
from .templates import VideoTemplate, TemplateRegistry

__all__ = [
    "VideoRenderer",
    "WaveformVisualizer",
    "SpectrumVisualizer", 
    "ParticleVisualizer",
    "ShortsGenerator",
    "VideoTemplate",
    "TemplateRegistry",
]
