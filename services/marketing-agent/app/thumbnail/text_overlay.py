"""Text overlay renderer for thumbnails.

Renders type beat text with effects optimized for CTR:
- Glow effects
- Outlines
- Shadows
- Gradients
- Chrome/metallic
- Neon
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from typing import Tuple, List, Optional
import structlog

logger = structlog.get_logger()


class TextOverlayRenderer:
    """Render text overlays on thumbnails with various effects."""
    
    def __init__(self, width: int = 1280, height: int = 720):
        self.width = width
        self.height = height
    
    def render_text(self, img: Image.Image, text: str, position: Tuple[float, float],
                    font_size: int, color: str = "#ffffff",
                    effect: str = "glow", effect_color: str = "#ff3366",
                    bold: bool = True, uppercase: bool = True,
                    align: str = "center") -> Image.Image:
        """Render text with specified effect.
        
        Args:
            img: Base image
            text: Text to render
            position: (x, y) normalized 0-1
            font_size: Font size in pixels
            color: Text color
            effect: Text effect name
            effect_color: Effect color
            bold: Use bold font
            uppercase: Convert to uppercase
            align: Text alignment
        
        Returns:
            Image with text overlay
        """
        if uppercase:
            text = text.upper()
        
        # Load font
        font = self._load_font(font_size, bold)
        
        # Calculate position
        draw = ImageDraw.Draw(img)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = int(position[0] * self.width)
        y = int(position[1] * self.height)
        
        if align == "center":
            x -= text_width // 2
        elif align == "right":
            x -= text_width
        
        # Apply effect
        if effect == "glow":
            img = self._apply_glow(img, text, (x, y), font, color, effect_color)
        elif effect == "outline":
            img = self._apply_outline(img, text, (x, y), font, color, effect_color)
        elif effect == "shadow":
            img = self._apply_shadow(img, text, (x, y), font, color, effect_color)
        elif effect == "gradient":
            img = self._apply_gradient_text(img, text, (x, y), font, color, effect_color)
        elif effect == "neon":
            img = self._apply_neon(img, text, (x, y), font, color, effect_color)
        elif effect == "chrome":
            img = self._apply_chrome(img, text, (x, y), font, color)
        else:
            # Plain text
            draw.text((x, y), text, font=font, fill=color)
        
        return img
    
    def _load_font(self, size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
        """Load a font, falling back to defaults."""
        font_names = [
            f"arial{'bd' if bold else ''}.ttf",
            f"DejaVuSans{'-Bold' if bold else ''}.ttf",
            f"LiberationSans{'-Bold' if bold else ''}.ttf",
        ]
        
        import os
        font_paths = [
            "",
            "/usr/share/fonts/truetype/dejavu/",
            "/usr/share/fonts/truetype/liberation/",
            "/System/Library/Fonts/",
            "C:/Windows/Fonts/",
        ]
        
        for path in font_paths:
            for name in font_names:
                full_path = os.path.join(path, name)
                try:
                    return ImageFont.truetype(full_path, size)
                except:
                    continue
        
        return ImageFont.load_default()
    
    def _apply_glow(self, img: Image.Image, text: str, position: Tuple[int, int],
                    font: ImageFont.FreeTypeFont, text_color: str, 
                    glow_color: str, glow_radius: int = 15) -> Image.Image:
        """Apply glow effect behind text."""
        x, y = position
        
        # Create glow layer
        glow_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_layer)
        
        # Draw text multiple times with increasing blur
        for offset in range(glow_radius, 0, -3):
            alpha = int(50 * (1 - offset / glow_radius))
            rgb = self._hex_to_rgb(glow_color)
            glow_draw.text((x, y), text, font=font, 
                          fill=(rgb[0], rgb[1], rgb[2], alpha))
        
        # Blur glow
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=glow_radius))
        
        # Composite
        img = Image.alpha_composite(img.convert('RGBA'), glow_layer).convert('RGB')
        
        # Draw main text
        draw = ImageDraw.Draw(img)
        draw.text((x, y), text, font=font, fill=text_color)
        
        return img
    
    def _apply_outline(self, img: Image.Image, text: str, position: Tuple[int, int],
                       font: ImageFont.FreeTypeFont, text_color: str,
                       outline_color: str, outline_width: int = 4) -> Image.Image:
        """Apply outline effect to text."""
        x, y = position
        draw = ImageDraw.Draw(img)
        
        # Draw outline in all directions
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
        
        # Draw main text
        draw.text((x, y), text, font=font, fill=text_color)
        
        return img
    
    def _apply_shadow(self, img: Image.Image, text: str, position: Tuple[int, int],
                      font: ImageFont.FreeTypeFont, text_color: str,
                      shadow_color: str, offset: Tuple[int, int] = (4, 4),
                      blur: int = 8) -> Image.Image:
        """Apply drop shadow to text."""
        x, y = position
        
        # Create shadow layer
        shadow_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow_layer)
        
        rgb = self._hex_to_rgb(shadow_color)
        shadow_draw.text((x + offset[0], y + offset[1]), text, font=font,
                        fill=(rgb[0], rgb[1], rgb[2], 180))
        
        # Blur shadow
        shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=blur))
        
        # Composite
        img = Image.alpha_composite(img.convert('RGBA'), shadow_layer).convert('RGB')
        
        # Draw main text
        draw = ImageDraw.Draw(img)
        draw.text((x, y), text, font=font, fill=text_color)
        
        return img
    
    def _apply_gradient_text(self, img: Image.Image, text: str, 
                             position: Tuple[int, int],
                             font: ImageFont.FreeTypeFont, 
                             color1: str, color2: str) -> Image.Image:
        """Apply vertical gradient to text."""
        x, y = position
        
        # Create text mask
        mask = Image.new('L', img.size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.text((x, y), text, font=font, fill=255)
        
        # Create gradient
        rgb1 = self._hex_to_rgb(color1)
        rgb2 = self._hex_to_rgb(color2)
        
        # Get text bounds
        bbox = mask_draw.textbbox((x, y), text, font=font)
        text_height = bbox[3] - bbox[1]
        
        gradient = Image.new('RGB', (1, text_height))
        for row in range(text_height):
            t = row / text_height if text_height > 0 else 0
            r = int(rgb1[0] + (rgb2[0] - rgb1[0]) * t)
            g = int(rgb1[1] + (rgb2[1] - rgb1[1]) * t)
            b = int(rgb1[2] + (rgb2[2] - rgb1[2]) * t)
            gradient.putpixel((0, row), (r, g, b))
        
        # Scale gradient to full size
        gradient = gradient.resize(img.size)
        
        # Composite using mask
        result = img.copy()
        result.paste(gradient, (0, 0), mask)
        
        return result
    
    def _apply_neon(self, img: Image.Image, text: str, position: Tuple[int, int],
                    font: ImageFont.FreeTypeFont, text_color: str,
                    neon_color: str) -> Image.Image:
        """Apply neon tube effect to text."""
        x, y = position
        
        # Create neon glow layers
        result = img.convert('RGBA')
        
        # Outer glow (large, diffuse)
        outer = Image.new('RGBA', img.size, (0, 0, 0, 0))
        outer_draw = ImageDraw.Draw(outer)
        rgb = self._hex_to_rgb(neon_color)
        outer_draw.text((x, y), text, font=font, 
                       fill=(rgb[0], rgb[1], rgb[2], 60))
        outer = outer.filter(ImageFilter.GaussianBlur(radius=20))
        
        # Middle glow
        middle = Image.new('RGBA', img.size, (0, 0, 0, 0))
        middle_draw = ImageDraw.Draw(middle)
        middle_draw.text((x, y), text, font=font,
                        fill=(rgb[0], rgb[1], rgb[2], 120))
        middle = middle.filter(ImageFilter.GaussianBlur(radius=10))
        
        # Inner glow
        inner = Image.new('RGBA', img.size, (0, 0, 0, 0))
        inner_draw = ImageDraw.Draw(inner)
        inner_draw.text((x, y), text, font=font,
                       fill=(rgb[0], rgb[1], rgb[2], 200))
        inner = inner.filter(ImageFilter.GaussianBlur(radius=5))
        
        # Composite all layers
        result = Image.alpha_composite(result, outer)
        result = Image.alpha_composite(result, middle)
        result = Image.alpha_composite(result, inner)
        
        # White core
        core_draw = ImageDraw.Draw(result)
        core_draw.text((x, y), text, font=font, fill='#ffffff')
        
        return result.convert('RGB')
    
    def _apply_chrome(self, img: Image.Image, text: str, position: Tuple[int, int],
                      font: ImageFont.FreeTypeFont, base_color: str) -> Image.Image:
        """Apply chrome/metallic effect to text."""
        x, y = position
        
        # Create metallic gradient (silver)
        mask = Image.new('L', img.size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.text((x, y), text, font=font, fill=255)
        
        # Chrome gradient: dark → light → dark
        bbox = mask_draw.textbbox((x, y), text, font=font)
        text_height = bbox[3] - bbox[1]
        
        gradient = Image.new('RGB', (1, text_height))
        colors = [
            (80, 80, 90),   # Dark
            (200, 200, 210), # Light
            (255, 255, 255), # Highlight
            (200, 200, 210), # Light
            (80, 80, 90),   # Dark
        ]
        
        for row in range(text_height):
            t = row / text_height if text_height > 0 else 0
            idx = int(t * (len(colors) - 1))
            idx = min(idx, len(colors) - 2)
            local_t = t * (len(colors) - 1) - idx
            
            c1 = colors[idx]
            c2 = colors[idx + 1]
            r = int(c1[0] + (c2[0] - c1[0]) * local_t)
            g = int(c1[1] + (c2[1] - c1[1]) * local_t)
            b = int(c1[2] + (c2[2] - c1[2]) * local_t)
            gradient.putpixel((0, row), (r, g, b))
        
        gradient = gradient.resize(img.size)
        
        # Add outline
        outline = Image.new('RGBA', img.size, (0, 0, 0, 0))
        outline_draw = ImageDraw.Draw(outline)
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                if dx != 0 or dy != 0:
                    outline_draw.text((x + dx, y + dy), text, font=font, 
                                     fill=(40, 40, 50, 255))
        
        result = img.copy()
        result.paste(gradient, (0, 0), mask)
        result = Image.alpha_composite(result.convert('RGBA'), outline).convert('RGB')
        
        return result
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def render_multi_line(self, img: Image.Image, lines: List[dict]) -> Image.Image:
        """Render multiple lines of text.
        
        Args:
            img: Base image
            lines: List of dicts with keys: text, position, font_size, color, effect, etc.
        
        Returns:
            Image with all text rendered
        """
        for line in lines:
            img = self.render_text(
                img,
                text=line.get('text', ''),
                position=line.get('position', (0.5, 0.5)),
                font_size=line.get('font_size', 60),
                color=line.get('color', '#ffffff'),
                effect=line.get('effect', 'none'),
                effect_color=line.get('effect_color', '#000000'),
                bold=line.get('bold', True),
                uppercase=line.get('uppercase', True),
                align=line.get('align', 'center')
            )
        
        return img
