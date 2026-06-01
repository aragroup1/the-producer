"""Thumbnail generator — creates CTR-optimized thumbnails for beats.

Generates multiple variants per beat with genre-specific aesthetics,
text effects, and A/B test readiness.
"""

import os
import random
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import structlog

from .style_presets import PresetRegistry, StylePreset
from .text_overlay import TextOverlayRenderer

logger = structlog.get_logger()


class ThumbnailGenerator:
    """Generate thumbnails optimized for YouTube CTR."""
    
    # Standard YouTube thumbnail size
    THUMB_WIDTH = 1280
    THUMB_HEIGHT = 720
    
    def __init__(self, output_dir: str = "./output/thumbnails"):
        self.output_dir = output_dir
        self.text_renderer = TextOverlayRenderer(self.THUMB_WIDTH, self.THUMB_HEIGHT)
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_thumbnail(self, beat_info: Dict[str, Any],
                           variant: str = "A",
                           preset_name: Optional[str] = None) -> Optional[str]:
        """Generate a single thumbnail.
        
        Args:
            beat_info: Beat metadata (genre, bpm, key, title, etc.)
            variant: A, B, or C for A/B testing
            preset_name: Specific preset, or auto-select by genre
        
        Returns:
            Path to generated thumbnail PNG
        """
        genre = beat_info.get('genre', 'default')
        
        # Get preset
        if preset_name:
            preset = PresetRegistry.get(preset_name)
        else:
            preset = PresetRegistry.get_for_genre(genre)
        
        if not preset:
            preset = PresetRegistry.get('default')
        
        # Create base image
        img = self._create_background(preset)
        
        # Apply background effects
        img = self._apply_background_effects(img, preset)
        
        # Generate text content
        text_lines = self._generate_text_content(beat_info, preset, variant)
        
        # Render text
        img = self.text_renderer.render_multi_line(img, text_lines)
        
        # Apply post-processing
        img = self._post_process(img, preset)
        
        # Save
        beat_id = beat_info.get('beat_id', 'unknown')
        output_path = os.path.join(
            self.output_dir,
            f"{beat_id}_thumb_{variant}.png"
        )
        
        img.save(output_path, 'PNG')
        
        logger.info("thumbnail_generated",
                   beat_id=beat_id,
                   variant=variant,
                   preset=preset.name,
                   path=output_path)
        
        return output_path
    
    def generate_variants(self, beat_info: Dict[str, Any],
                          count: int = 3) -> List[str]:
        """Generate multiple thumbnail variants for A/B testing.
        
        Args:
            beat_info: Beat metadata
            count: Number of variants (2 or 3)
        
        Returns:
            List of thumbnail file paths
        """
        variants = []
        labels = ['A', 'B', 'C'][:count]
        
        for label in labels:
            try:
                path = self.generate_thumbnail(beat_info, variant=label)
                if path:
                    variants.append(path)
            except Exception as e:
                logger.error("variant_generation_failed",
                           variant=label, error=str(e))
        
        return variants
    
    def _create_background(self, preset: StylePreset) -> Image.Image:
        """Create base background image."""
        width, height = self.THUMB_WIDTH, self.THUMB_HEIGHT
        
        if preset.background_style.value == 'gradient':
            # Create gradient background
            img = Image.new('RGB', (width, height))
            color1 = self._hex_to_rgb(preset.colors.background)
            color2 = self._hex_to_rgb(preset.colors.background_secondary)
            
            for y in range(height):
                t = y / height
                r = int(color1[0] + (color2[0] - color1[0]) * t)
                g = int(color1[1] + (color2[1] - color1[1]) * t)
                b = int(color1[2] + (color2[2] - color1[2]) * t)
                
                for x in range(width):
                    img.putpixel((x, y), (r, g, b))
        
        elif preset.background_style.value == 'split':
            # Split background (two colors side by side or top/bottom)
            img = Image.new('RGB', (width, height))
            color1 = self._hex_to_rgb(preset.colors.background)
            color2 = self._hex_to_rgb(preset.colors.background_secondary)
            
            # Diagonal split
            for y in range(height):
                for x in range(width):
                    t = (x + y) / (width + height)
                    if t < 0.5:
                        img.putpixel((x, y), color1)
                    else:
                        img.putpixel((x, y), color2)
        
        else:
            # Solid background
            img = Image.new('RGB', (width, height), preset.colors.background)
        
        return img
    
    def _apply_background_effects(self, img: Image.Image, 
                                  preset: StylePreset) -> Image.Image:
        """Apply background effects like vignette, blur, etc."""
        if preset.background_style.value == 'vignette':
            img = self._apply_vignette(img, intensity=0.6)
        
        # Add subtle noise for texture
        img = self._add_noise(img, amount=0.02)
        
        return img
    
    def _apply_vignette(self, img: Image.Image, 
                        intensity: float = 0.5) -> Image.Image:
        """Apply vignette effect (darken edges)."""
        width, height = img.size
        
        # Create vignette mask
        vignette = Image.new('L', (width, height), 255)
        
        center_x, center_y = width // 2, height // 2
        max_dist = np.sqrt(center_x**2 + center_y**2)
        
        pixels = vignette.load()
        for y in range(height):
            for x in range(width):
                dist = np.sqrt((x - center_x)**2 + (y - center_y)**2)
                t = dist / max_dist if max_dist > 0 else 0
                # Smooth falloff
                factor = 1 - (t ** 2) * intensity
                factor = max(0.3, factor)
                pixels[x, y] = int(255 * factor)
        
        # Apply mask
        img = Image.composite(
            img,
            Image.new('RGB', (width, height), '#000000'),
            vignette
        )
        
        return img
    
    def _add_noise(self, img: Image.Image, 
                   amount: float = 0.02) -> Image.Image:
        """Add subtle noise for texture."""
        arr = np.array(img).astype(np.float32)
        noise = np.random.normal(0, amount * 255, arr.shape)
        arr = arr + noise
        arr = np.clip(arr, 0, 255).astype(np.uint8)
        return Image.fromarray(arr)
    
    def _generate_text_content(self, beat_info: Dict[str, Any],
                               preset: StylePreset,
                               variant: str) -> List[dict]:
        """Generate text lines for the thumbnail.
        
        Creates different layouts per variant for A/B testing.
        """
        genre = beat_info.get('genre', 'BEAT')
        bpm = beat_info.get('bpm', '')
        key = beat_info.get('key', '')
        scale = beat_info.get('scale', '')
        
        # Main title
        title = self._generate_title(beat_info, preset, variant)
        
        # Subtitle with BPM/Key
        subtitle = f"{bpm} BPM • {key} {scale.title()}" if bpm else ""
        
        lines = []
        
        if variant == 'A':
            # Variant A: Big title centered, subtitle below
            lines = [
                {
                    'text': title,
                    'position': (0.5, 0.45),
                    'font_size': preset.font.size_main,
                    'color': preset.colors.text_primary,
                    'effect': preset.text_effect.value,
                    'effect_color': preset.colors.glow,
                    'bold': True,
                    'uppercase': preset.font.uppercase,
                    'align': 'center'
                },
                {
                    'text': subtitle,
                    'position': (0.5, 0.65),
                    'font_size': preset.font.size_sub,
                    'color': preset.colors.text_secondary,
                    'effect': 'shadow',
                    'effect_color': preset.colors.border,
                    'bold': False,
                    'uppercase': False,
                    'align': 'center'
                }
            ]
        
        elif variant == 'B':
            # Variant B: Title at top, "FREE" badge prominent
            free_text = random.choice(preset.urgency_words or ['FREE'])
            lines = [
                {
                    'text': free_text,
                    'position': (0.5, 0.25),
                    'font_size': preset.font.size_main + 20,
                    'color': preset.colors.accent,
                    'effect': 'neon',
                    'effect_color': preset.colors.accent_secondary,
                    'bold': True,
                    'uppercase': True,
                    'align': 'center'
                },
                {
                    'text': title,
                    'position': (0.5, 0.55),
                    'font_size': preset.font.size_main - 20,
                    'color': preset.colors.text_primary,
                    'effect': preset.text_effect.value,
                    'effect_color': preset.colors.glow,
                    'bold': True,
                    'uppercase': preset.font.uppercase,
                    'align': 'center'
                },
                {
                    'text': subtitle,
                    'position': (0.5, 0.75),
                    'font_size': preset.font.size_sub,
                    'color': preset.colors.text_secondary,
                    'effect': 'shadow',
                    'effect_color': preset.colors.border,
                    'bold': False,
                    'uppercase': False,
                    'align': 'center'
                }
            ]
        
        elif variant == 'C':
            # Variant C: Minimal, artist-style
            emoji = random.choice(preset.emoji_set or ['🔥']) if preset.emoji_set else '🔥'
            lines = [
                {
                    'text': emoji,
                    'position': (0.5, 0.2),
                    'font_size': 80,
                    'color': preset.colors.accent,
                    'effect': 'none',
                    'bold': False,
                    'uppercase': False,
                    'align': 'center'
                },
                {
                    'text': title,
                    'position': (0.5, 0.5),
                    'font_size': preset.font.size_main,
                    'color': preset.colors.text_primary,
                    'effect': preset.text_effect.value,
                    'effect_color': preset.colors.glow,
                    'bold': True,
                    'uppercase': preset.font.uppercase,
                    'align': 'center'
                },
                {
                    'text': f"{bpm} BPM",
                    'position': (0.5, 0.72),
                    'font_size': preset.font.size_info,
                    'color': preset.colors.accent,
                    'effect': 'glow',
                    'effect_color': preset.colors.accent_secondary,
                    'bold': True,
                    'uppercase': False,
                    'align': 'center'
                }
            ]
        
        return lines
    
    def _generate_title(self, beat_info: Dict[str, Any],
                        preset: StylePreset,
                        variant: str) -> str:
        """Generate thumbnail title text."""
        genre = beat_info.get('genre', 'BEAT')
        
        # Clean genre name
        genre_display = genre.replace('_', ' ').upper()
        
        # Power words
        power = random.choice(preset.power_words or ['TYPE BEAT'])
        
        if variant == 'A':
            return f"{genre_display} {power}"
        elif variant == 'B':
            urgency = random.choice(preset.urgency_words or ['HARD'])
            return f"{urgency} {genre_display} {power}"
        else:
            return f"{genre_display} {power}"
    
    def _post_process(self, img: Image.Image, 
                      preset: StylePreset) -> Image.Image:
        """Apply final post-processing."""
        # Slight contrast boost
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.1)
        
        # Slight saturation boost
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.15)
        
        # Sharpen
        img = img.filter(ImageFilter.SHARPEN)
        
        return img
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def get_thumbnail_score(self, thumbnail_path: str) -> Dict[str, float]:
        """Analyze thumbnail for CTR optimization.
        
        Returns scores for various factors.
        """
        try:
            img = Image.open(thumbnail_path)
            arr = np.array(img)
            
            # Contrast score
            gray = np.mean(arr, axis=2)
            contrast = np.std(gray) / 255.0
            
            # Brightness score (optimal: 0.4-0.7)
            brightness = np.mean(gray) / 255.0
            brightness_score = 1.0 - abs(brightness - 0.55) * 2
            
            # Colorfulness
            r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]
            colorfulness = np.std([np.std(r), np.std(g), np.std(b)]) / 255.0
            
            # Edge density (text readability) - use simple gradient instead of scipy
            gy, gx = np.gradient(gray)
            edge_magnitude = np.sqrt(gx**2 + gy**2)
            edge_density = np.mean(edge_magnitude) / 255.0
            
            return {
                'contrast': round(contrast, 3),
                'brightness': round(brightness, 3),
                'brightness_score': round(max(0, brightness_score), 3),
                'colorfulness': round(colorfulness, 3),
                'edge_density': round(edge_density, 3),
                'overall': round((contrast + brightness_score + colorfulness + edge_density) / 4, 3)
            }
        except Exception as e:
            logger.error("thumbnail_analysis_failed", error=str(e))
            return {}
