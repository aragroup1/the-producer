"""Video template definitions for genre-specific aesthetics.

Each template defines colors, visualizer style, text placement,
and motion parameters optimized for a specific genre/niche.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from enum import Enum


class VisualizerStyle(Enum):
    """Available visualizer styles."""
    WAVEFORM = "waveform"
    SPECTRUM = "spectrum"
    PARTICLES = "particles"
    BARS = "bars"
    CIRCULAR = "circular"
    GLITCH = "glitch"


@dataclass
class ColorScheme:
    """Color palette for a video template."""
    background: str = "#0a0a0a"
    primary: str = "#ffffff"
    secondary: str = "#888888"
    accent: str = "#ff3366"
    glow: str = "#ff3366"
    text: str = "#ffffff"
    text_shadow: str = "#000000"


@dataclass
class TextConfig:
    """Text overlay configuration."""
    title_font_size: int = 72
    subtitle_font_size: int = 36
    info_font_size: int = 24
    title_position: Tuple[float, float] = (0.5, 0.15)  # x, y (normalized 0-1)
    subtitle_position: Tuple[float, float] = (0.5, 0.25)
    info_position: Tuple[float, float] = (0.5, 0.85)
    font_family: str = "Arial"
    bold: bool = True
    uppercase: bool = True


@dataclass
class MotionConfig:
    """Motion and animation parameters."""
    bpm_sync: bool = True
    intensity_multiplier: float = 1.0
    smoothing: float = 0.3
    particle_count: int = 100
    particle_speed: float = 1.0
    camera_shake: float = 0.0
    zoom_pulse: bool = False


@dataclass
class VideoTemplate:
    """Complete video template definition."""
    name: str
    genre: str
    visualizer_style: VisualizerStyle
    color_scheme: ColorScheme
    text_config: TextConfig
    motion_config: MotionConfig
    aspect_ratio: str = "16:9"  # 16:9 or 9:16
    resolution: Tuple[int, int] = (1920, 1080)
    fps: int = 30
    description: str = ""


class TemplateRegistry:
    """Registry of all video templates."""
    
    _templates: Dict[str, VideoTemplate] = {}
    
    @classmethod
    def register(cls, template: VideoTemplate):
        """Register a template."""
        cls._templates[template.name] = template
    
    @classmethod
    def get(cls, name: str) -> Optional[VideoTemplate]:
        """Get a template by name."""
        return cls._templates.get(name)
    
    @classmethod
    def get_for_genre(cls, genre: str, aspect_ratio: str = "16:9") -> VideoTemplate:
        """Get best template for a genre."""
        # Try exact match
        for template in cls._templates.values():
            if template.genre == genre and template.aspect_ratio == aspect_ratio:
                return template
        
        # Try category match
        genre_map = {
            "trap": "dark_trap",
            "drill": "dark_drill",
            "boom_bap": "classic_boombap",
            "rage": "aggressive_rage",
            "phonk": "dark_phonk",
            "jersey_club": "bouncy_jersey",
            "plugg": "smooth_plugg",
            "west_coast": "funky_westcoast",
            "rnb": "smooth_rnb",
            "neo_soul": "groovy_neosoul",
            "afrobeats": "vibrant_afrobeats",
            "amapiano": "vibey_amapiano",
            "dancehall": "energetic_dancehall",
            "reggaeton": "tropical_reggaeton",
            "hyperpop": "glitch_hyperpop",
            "edm_trap": "festival_edm",
            "future_bass": "melodic_futurebass",
            "lofi": "chill_lofi",
            "ambient": "ethereal_ambient",
        }
        
        mapped = genre_map.get(genre)
        if mapped:
            for template in cls._templates.values():
                if template.genre == mapped and template.aspect_ratio == aspect_ratio:
                    return template
        
        # Default fallback
        default = cls._templates.get("default_16x9" if aspect_ratio == "16:9" else "default_9x16")
        if default:
            return default
        
        # Ultimate fallback
        return VideoTemplate(
            name="fallback",
            genre="default",
            visualizer_style=VisualizerStyle.WAVEFORM,
            color_scheme=ColorScheme(),
            text_config=TextConfig(),
            motion_config=MotionConfig(),
            aspect_ratio=aspect_ratio,
            resolution=(1920, 1080) if aspect_ratio == "16:9" else (1080, 1920)
        )
    
    @classmethod
    def list_templates(cls) -> List[str]:
        """List all registered template names."""
        return list(cls._templates.keys())
    
    @classmethod
    def list_genres(cls) -> List[str]:
        """List all genres with templates."""
        return list(set(t.genre for t in cls._templates.values()))


# ─── Register Default Templates ──────────────────────────────────────

# Dark Trap (16:9)
TemplateRegistry.register(VideoTemplate(
    name="dark_trap_16x9",
    genre="trap",
    visualizer_style=VisualizerStyle.BARS,
    color_scheme=ColorScheme(
        background="#0a0a0a",
        primary="#ff3366",
        secondary="#660022",
        accent="#ff0066",
        glow="#ff3366",
        text="#ffffff",
        text_shadow="#000000"
    ),
    text_config=TextConfig(
        title_font_size=80,
        subtitle_font_size=40,
        info_font_size=28,
        title_position=(0.5, 0.12),
        subtitle_position=(0.5, 0.22),
        info_position=(0.5, 0.88),
        uppercase=True,
        bold=True
    ),
    motion_config=MotionConfig(
        bpm_sync=True,
        intensity_multiplier=1.3,
        smoothing=0.2,
        particle_count=150,
        zoom_pulse=True
    ),
    aspect_ratio="16:9",
    resolution=(1920, 1080),
    description="Aggressive dark trap with pulsing bars and red glow"
))

# Dark Trap (9:16 Shorts)
TemplateRegistry.register(VideoTemplate(
    name="dark_trap_9x16",
    genre="trap",
    visualizer_style=VisualizerStyle.BARS,
    color_scheme=ColorScheme(
        background="#0a0a0a",
        primary="#ff3366",
        secondary="#660022",
        accent="#ff0066",
        glow="#ff3366",
        text="#ffffff",
        text_shadow="#000000"
    ),
    text_config=TextConfig(
        title_font_size=64,
        subtitle_font_size=32,
        info_font_size=24,
        title_position=(0.5, 0.08),
        subtitle_position=(0.5, 0.16),
        info_position=(0.5, 0.92),
        uppercase=True,
        bold=True
    ),
    motion_config=MotionConfig(
        bpm_sync=True,
        intensity_multiplier=1.3,
        smoothing=0.2,
        particle_count=100,
        zoom_pulse=True
    ),
    aspect_ratio="9:16",
    resolution=(1080, 1920),
    description="Vertical dark trap for Shorts/TikTok/Reels"
))

# UK Drill (16:9)
TemplateRegistry.register(VideoTemplate(
    name="uk_drill_16x9",
    genre="drill",
    visualizer_style=VisualizerStyle.SPECTRUM,
    color_scheme=ColorScheme(
        background="#0d0d0d",
        primary="#00ff88",
        secondary="#004422",
        accent="#00cc66",
        glow="#00ff88",
        text="#ffffff",
        text_shadow="#000000"
    ),
    text_config=TextConfig(
        title_font_size=78,
        subtitle_font_size=38,
        info_font_size=26,
        title_position=(0.5, 0.12),
        subtitle_position=(0.5, 0.22),
        info_position=(0.5, 0.88),
        uppercase=True,
        bold=True
    ),
    motion_config=MotionConfig(
        bpm_sync=True,
        intensity_multiplier=1.2,
        smoothing=0.25,
        camera_shake=0.02
    ),
    aspect_ratio="16:9",
    resolution=(1920, 1080),
    description="UK drill with green spectrum and subtle camera shake"
))

# UK Drill (9:16)
TemplateRegistry.register(VideoTemplate(
    name="uk_drill_9x16",
    genre="drill",
    visualizer_style=VisualizerStyle.SPECTRUM,
    color_scheme=ColorScheme(
        background="#0d0d0d",
        primary="#00ff88",
        secondary="#004422",
        accent="#00cc66",
        glow="#00ff88",
        text="#ffffff",
        text_shadow="#000000"
    ),
    text_config=TextConfig(
        title_font_size=60,
        subtitle_font_size=30,
        info_font_size=22,
        title_position=(0.5, 0.08),
        subtitle_position=(0.5, 0.16),
        info_position=(0.5, 0.92),
        uppercase=True,
        bold=True
    ),
    motion_config=MotionConfig(
        bpm_sync=True,
        intensity_multiplier=1.2,
        smoothing=0.25,
        camera_shake=0.02
    ),
    aspect_ratio="9:16",
    resolution=(1080, 1920),
    description="Vertical UK drill for Shorts/TikTok/Reels"
))

# Lo-Fi (16:9)
TemplateRegistry.register(VideoTemplate(
    name="lofi_16x9",
    genre="lofi",
    visualizer_style=VisualizerStyle.PARTICLES,
    color_scheme=ColorScheme(
        background="#2d2d2d",
        primary="#a8dadc",
        secondary="#457b9d",
        accent="#f1faee",
        glow="#a8dadc",
        text="#f1faee",
        text_shadow="#1d1d1d"
    ),
    text_config=TextConfig(
        title_font_size=68,
        subtitle_font_size=34,
        info_font_size=24,
        title_position=(0.5, 0.12),
        subtitle_position=(0.5, 0.22),
        info_position=(0.5, 0.88),
        uppercase=False,
        bold=False
    ),
    motion_config=MotionConfig(
        bpm_sync=False,
        intensity_multiplier=0.6,
        smoothing=0.5,
        particle_count=80,
        particle_speed=0.5
    ),
    aspect_ratio="16:9",
    resolution=(1920, 1080),
    description="Chill lo-fi with floating particles and soft colors"
))

# Lo-Fi (9:16)
TemplateRegistry.register(VideoTemplate(
    name="lofi_9x16",
    genre="lofi",
    visualizer_style=VisualizerStyle.PARTICLES,
    color_scheme=ColorScheme(
        background="#2d2d2d",
        primary="#a8dadc",
        secondary="#457b9d",
        accent="#f1faee",
        glow="#a8dadc",
        text="#f1faee",
        text_shadow="#1d1d1d"
    ),
    text_config=TextConfig(
        title_font_size=52,
        subtitle_font_size=26,
        info_font_size=20,
        title_position=(0.5, 0.08),
        subtitle_position=(0.5, 0.16),
        info_position=(0.5, 0.92),
        uppercase=False,
        bold=False
    ),
    motion_config=MotionConfig(
        bpm_sync=False,
        intensity_multiplier=0.6,
        smoothing=0.5,
        particle_count=60,
        particle_speed=0.5
    ),
    aspect_ratio="9:16",
    resolution=(1080, 1920),
    description="Vertical lo-fi for study/sleep Shorts"
))

# R&B (16:9)
TemplateRegistry.register(VideoTemplate(
    name="rnb_16x9",
    genre="rnb",
    visualizer_style=VisualizerStyle.CIRCULAR,
    color_scheme=ColorScheme(
        background="#1a1a2e",
        primary="#9b5de5",
        secondary="#f15bb5",
        accent="#00bbf9",
        glow="#9b5de5",
        text="#ffffff",
        text_shadow="#000000"
    ),
    text_config=TextConfig(
        title_font_size=74,
        subtitle_font_size=36,
        info_font_size=26,
        title_position=(0.5, 0.12),
        subtitle_position=(0.5, 0.22),
        info_position=(0.5, 0.88),
        uppercase=False,
        bold=True
    ),
    motion_config=MotionConfig(
        bpm_sync=True,
        intensity_multiplier=0.9,
        smoothing=0.35,
        particle_count=120
    ),
    aspect_ratio="16:9",
    resolution=(1920, 1080),
    description="Smooth R&B with circular visualizer and purple/pink gradients"
))

# Afrobeats (16:9)
TemplateRegistry.register(VideoTemplate(
    name="afrobeats_16x9",
    genre="afrobeats",
    visualizer_style=VisualizerStyle.WAVEFORM,
    color_scheme=ColorScheme(
        background="#0d1b2a",
        primary="#ffbe0b",
        secondary="#fb5607",
        accent="#ff006e",
        glow="#ffbe0b",
        text="#ffffff",
        text_shadow="#000000"
    ),
    text_config=TextConfig(
        title_font_size=76,
        subtitle_font_size=38,
        info_font_size=26,
        title_position=(0.5, 0.12),
        subtitle_position=(0.5, 0.22),
        info_position=(0.5, 0.88),
        uppercase=True,
        bold=True
    ),
    motion_config=MotionConfig(
        bpm_sync=True,
        intensity_multiplier=1.1,
        smoothing=0.3,
        particle_count=200,
        particle_speed=1.2
    ),
    aspect_ratio="16:9",
    resolution=(1920, 1080),
    description="Vibrant afrobeats with warm orange waveform"
))

# Default templates
TemplateRegistry.register(VideoTemplate(
    name="default_16x9",
    genre="default",
    visualizer_style=VisualizerStyle.WAVEFORM,
    color_scheme=ColorScheme(),
    text_config=TextConfig(),
    motion_config=MotionConfig(),
    aspect_ratio="16:9",
    resolution=(1920, 1080),
    description="Default waveform template"
))

TemplateRegistry.register(VideoTemplate(
    name="default_9x16",
    genre="default",
    visualizer_style=VisualizerStyle.WAVEFORM,
    color_scheme=ColorScheme(),
    text_config=TextConfig(
        title_font_size=56,
        subtitle_font_size=28,
        info_font_size=22,
        title_position=(0.5, 0.08),
        subtitle_position=(0.5, 0.16),
        info_position=(0.5, 0.92),
    ),
    motion_config=MotionConfig(),
    aspect_ratio="9:16",
    resolution=(1080, 1920),
    description="Default vertical waveform template"
))
