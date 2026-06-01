"""Thumbnail style presets for genre-specific aesthetics.

Each preset defines colors, fonts, layouts, and effects optimized
for maximum CTR within a specific genre/niche.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from enum import Enum


class TextEffect(Enum):
    """Available text effects."""
    NONE = "none"
    GLOW = "glow"
    OUTLINE = "outline"
    SHADOW = "shadow"
    GRADIENT = "gradient"
    CHROME = "chrome"
    NEON = "neon"


class BackgroundStyle(Enum):
    """Background style options."""
    SOLID = "solid"
    GRADIENT = "gradient"
    BLURRED = "blurred"
    DARKENED = "darkened"
    VIGNETTE = "vignette"
    SPLIT = "split"


@dataclass
class FontConfig:
    """Font configuration."""
    family: str = "Arial"
    size_main: int = 120
    size_sub: int = 60
    size_info: int = 36
    weight: str = "bold"
    uppercase: bool = True
    letter_spacing: int = 4


@dataclass
class ColorPalette:
    """Color palette for thumbnails."""
    background: str = "#0a0a0a"
    background_secondary: str = "#1a1a1a"
    text_primary: str = "#ffffff"
    text_secondary: str = "#cccccc"
    accent: str = "#ff3366"
    accent_secondary: str = "#ff0066"
    glow: str = "#ff3366"
    border: str = "#333333"


@dataclass
class LayoutConfig:
    """Layout configuration."""
    text_position: str = "center"  # center, top, bottom, left, right
    text_align: str = "center"     # left, center, right
    padding: int = 40
    margin_top: int = 60
    margin_bottom: int = 60
    logo_position: Optional[str] = None  # top-left, top-right, bottom-left, bottom-right
    badge_position: Optional[str] = None


@dataclass
class StylePreset:
    """Complete thumbnail style preset."""
    name: str
    genre: str
    description: str
    colors: ColorPalette
    font: FontConfig
    layout: LayoutConfig
    text_effect: TextEffect
    background_style: BackgroundStyle
    # CTR psychology
    urgency_words: List[str] = None
    power_words: List[str] = None
    emoji_set: List[str] = None


class PresetRegistry:
    """Registry of all thumbnail style presets."""
    
    _presets: Dict[str, StylePreset] = {}
    
    @classmethod
    def register(cls, preset: StylePreset):
        """Register a preset."""
        cls._presets[preset.name] = preset
    
    @classmethod
    def get(cls, name: str) -> Optional[StylePreset]:
        """Get preset by name."""
        return cls._presets.get(name)
    
    @classmethod
    def get_for_genre(cls, genre: str) -> StylePreset:
        """Get best preset for a genre."""
        # Direct match
        for preset in cls._presets.values():
            if preset.genre == genre:
                return preset
        
        # Category match
        genre_map = {
            'trap': 'dark_trap',
            'drill': 'dark_drill',
            'boom_bap': 'classic_boombap',
            'rage': 'aggressive_rage',
            'phonk': 'dark_phonk',
            'jersey_club': 'bouncy_jersey',
            'plugg': 'smooth_plugg',
            'west_coast': 'funky_westcoast',
            'rnb': 'smooth_rnb',
            'neo_soul': 'groovy_neosoul',
            'afrobeats': 'vibrant_afrobeats',
            'amapiano': 'vibey_amapiano',
            'dancehall': 'energetic_dancehall',
            'reggaeton': 'tropical_reggaeton',
            'hyperpop': 'glitch_hyperpop',
            'edm_trap': 'festival_edm',
            'future_bass': 'melodic_futurebass',
            'lofi': 'chill_lofi',
            'ambient': 'ethereal_ambient',
        }
        
        mapped = genre_map.get(genre)
        if mapped:
            for preset in cls._presets.values():
                if preset.genre == mapped:
                    return preset
        
        # Default
        return cls._presets.get('default', cls._create_default())
    
    @classmethod
    def _create_default(cls) -> StylePreset:
        """Create default preset."""
        return StylePreset(
            name='default',
            genre='default',
            description='Default thumbnail style',
            colors=ColorPalette(),
            font=FontConfig(),
            layout=LayoutConfig(),
            text_effect=TextEffect.GLOW,
            background_style=BackgroundStyle.GRADIENT
        )
    
    @classmethod
    def list_presets(cls) -> List[str]:
        """List all preset names."""
        return list(cls._presets.keys())


# ─── Register Presets ────────────────────────────────────────────────

# Dark Trap
PresetRegistry.register(StylePreset(
    name='dark_trap',
    genre='trap',
    description='Aggressive dark trap with red neon glow',
    colors=ColorPalette(
        background='#0a0a0a',
        background_secondary='#1a0008',
        text_primary='#ffffff',
        text_secondary='#ff99bb',
        accent='#ff3366',
        accent_secondary='#ff0066',
        glow='#ff3366',
        border='#330011'
    ),
    font=FontConfig(
        family='Impact',
        size_main=140,
        size_sub=64,
        size_info=36,
        weight='bold',
        uppercase=True,
        letter_spacing=6
    ),
    layout=LayoutConfig(
        text_position='center',
        text_align='center',
        padding=50,
        margin_top=80,
        margin_bottom=80
    ),
    text_effect=TextEffect.NEON,
    background_style=BackgroundStyle.VIGNETTE,
    urgency_words=['FREE', 'HARD', 'INSANE', 'CRAZY'],
    power_words=['TYPE BEAT', 'INSTRUMENTAL', 'PROD'],
    emoji_set=['🔥', '💯', '⚡', '🎯']
))

# UK Drill
PresetRegistry.register(StylePreset(
    name='dark_drill',
    genre='drill',
    description='UK drill with green cyber aesthetic',
    colors=ColorPalette(
        background='#0d0d0d',
        background_secondary='#001a0d',
        text_primary='#ffffff',
        text_secondary='#88ffbb',
        accent='#00ff88',
        accent_secondary='#00cc66',
        glow='#00ff88',
        border='#002211'
    ),
    font=FontConfig(
        family='Impact',
        size_main=130,
        size_sub=60,
        size_info=34,
        weight='bold',
        uppercase=True,
        letter_spacing=5
    ),
    layout=LayoutConfig(
        text_position='center',
        text_align='center',
        padding=45,
        margin_top=70,
        margin_bottom=70
    ),
    text_effect=TextEffect.GLOW,
    background_style=BackgroundStyle.GRADIENT,
    urgency_words=['FREE', 'HARD', 'DARK', 'UK'],
    power_words=['DRILL', 'TYPE BEAT', 'INSTRUMENTAL'],
    emoji_set=['🔥', '💚', '⚡', '🎯']
))

# Lo-Fi
PresetRegistry.register(StylePreset(
    name='chill_lofi',
    genre='lofi',
    description='Chill lo-fi with soft pastel aesthetic',
    colors=ColorPalette(
        background='#2d2d2d',
        background_secondary='#3d3d3d',
        text_primary='#f1faee',
        text_secondary='#a8dadc',
        accent='#457b9d',
        accent_secondary='#1d3557',
        glow='#a8dadc',
        border='#4a4a4a'
    ),
    font=FontConfig(
        family='Arial',
        size_main=100,
        size_sub=50,
        size_info=30,
        weight='normal',
        uppercase=False,
        letter_spacing=3
    ),
    layout=LayoutConfig(
        text_position='bottom',
        text_align='center',
        padding=40,
        margin_top=60,
        margin_bottom=100
    ),
    text_effect=TextEffect.SHADOW,
    background_style=BackgroundStyle.BLURRED,
    urgency_words=['CHILL', 'RELAX', 'STUDY'],
    power_words=['LO-FI', 'BEAT', 'HIP HOP'],
    emoji_set=['🎧', '☕', '🌙', '📚']
))

# R&B
PresetRegistry.register(StylePreset(
    name='smooth_rnb',
    genre='rnb',
    description='Smooth R&B with purple/pink gradients',
    colors=ColorPalette(
        background='#1a1a2e',
        background_secondary='#16213e',
        text_primary='#ffffff',
        text_secondary='#f15bb5',
        accent='#9b5de5',
        accent_secondary='#00bbf9',
        glow='#9b5de5',
        border='#2a2a4e'
    ),
    font=FontConfig(
        family='Arial',
        size_main=120,
        size_sub=56,
        size_info=32,
        weight='bold',
        uppercase=False,
        letter_spacing=4
    ),
    layout=LayoutConfig(
        text_position='center',
        text_align='center',
        padding=45,
        margin_top=75,
        margin_bottom=75
    ),
    text_effect=TextEffect.GRADIENT,
    background_style=BackgroundStyle.GRADIENT,
    urgency_words=['SMOOTH', 'SEXY', 'SENSUAL'],
    power_words=['R&B', 'TYPE BEAT', 'INSTRUMENTAL'],
    emoji_set=['💜', '🔥', '💫', '🎵']
))

# Afrobeats
PresetRegistry.register(StylePreset(
    name='vibrant_afrobeats',
    genre='afrobeats',
    description='Vibrant afrobeats with warm tropical colors',
    colors=ColorPalette(
        background='#0d1b2a',
        background_secondary='#1b263b',
        text_primary='#ffffff',
        text_secondary='#ffbe0b',
        accent='#fb5607',
        accent_secondary='#ff006e',
        glow='#ffbe0b',
        border='#2a3a4a'
    ),
    font=FontConfig(
        family='Impact',
        size_main=130,
        size_sub=60,
        size_info=34,
        weight='bold',
        uppercase=True,
        letter_spacing=5
    ),
    layout=LayoutConfig(
        text_position='center',
        text_align='center',
        padding=45,
        margin_top=70,
        margin_bottom=70
    ),
    text_effect=TextEffect.GLOW,
    background_style=BackgroundStyle.GRADIENT,
    urgency_words=['FREE', 'HOT', 'AFRO'],
    power_words=['AFROBEATS', 'TYPE BEAT', 'INSTRUMENTAL'],
    emoji_set=['🔥', '🌍', '💃', '🎵']
))

# Boom Bap
PresetRegistry.register(StylePreset(
    name='classic_boombap',
    genre='boom_bap',
    description='Classic boom bap with vintage aesthetic',
    colors=ColorPalette(
        background='#1a1a2e',
        background_secondary='#2a2a3e',
        text_primary='#f4a261',
        text_secondary='#e76f51',
        accent='#e9c46a',
        accent_secondary='#f4a261',
        glow='#f4a261',
        border='#3a3a4e'
    ),
    font=FontConfig(
        family='Courier New',
        size_main=110,
        size_sub=52,
        size_info=30,
        weight='bold',
        uppercase=True,
        letter_spacing=4
    ),
    layout=LayoutConfig(
        text_position='center',
        text_align='center',
        padding=40,
        margin_top=70,
        margin_bottom=70
    ),
    text_effect=TextEffect.OUTLINE,
    background_style=BackgroundStyle.VIGNETTE,
    urgency_words=['CLASSIC', 'OLD SCHOOL', 'RAW'],
    power_words=['BOOM BAP', 'TYPE BEAT', 'HIP HOP'],
    emoji_set=['🎤', '💿', '🔥', '🎵']
))

# Default fallback
PresetRegistry.register(StylePreset(
    name='default',
    genre='default',
    description='Default thumbnail style',
    colors=ColorPalette(),
    font=FontConfig(),
    layout=LayoutConfig(),
    text_effect=TextEffect.GLOW,
    background_style=BackgroundStyle.GRADIENT,
    urgency_words=['FREE'],
    power_words=['TYPE BEAT'],
    emoji_set=['🔥']
))
