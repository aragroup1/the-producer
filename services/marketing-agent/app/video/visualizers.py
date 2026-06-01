"""Audio visualizer renderers using numpy + Pillow.

Generates frame-by-frame visualizations that sync to audio energy.
Each visualizer produces RGB frames as numpy arrays for FFmpeg encoding.
"""

import numpy as np
from typing import Tuple, List, Optional, Callable
from PIL import Image, ImageDraw, ImageFont
import structlog

logger = structlog.get_logger()


class BaseVisualizer:
    """Base class for all visualizers."""
    
    def __init__(self, width: int = 1920, height: int = 1080, fps: int = 30):
        self.width = width
        self.height = height
        self.fps = fps
        self.frame_count = 0
    
    def render_frame(self, audio_chunk: np.ndarray, 
                     energy: float, bpm: float = 140,
                     colors: dict = None, text_overlay: dict = None) -> np.ndarray:
        """Render a single frame.
        
        Args:
            audio_chunk: Audio samples for this frame (mono)
            energy: Normalized energy level (0.0 - 1.0)
            bpm: Beat BPM for sync
            colors: Color scheme dict
            text_overlay: Text to render {title, subtitle, info}
        
        Returns:
            RGB frame as numpy array (H, W, 3)
        """
        raise NotImplementedError
    
    def _create_base_image(self, bg_color: str = "#0a0a0a") -> Tuple[Image.Image, ImageDraw.Draw]:
        """Create base image with background."""
        img = Image.new('RGB', (self.width, self.height), bg_color)
        draw = ImageDraw.Draw(img)
        return img, draw
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _interpolate_color(self, color1: str, color2: str, t: float) -> str:
        """Interpolate between two hex colors."""
        rgb1 = self._hex_to_rgb(color1)
        rgb2 = self._hex_to_rgb(color2)
        rgb = tuple(int(a + (b - a) * t) for a, b in zip(rgb1, rgb2))
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    
    def _draw_text(self, img: Image.Image, text: str, position: Tuple[float, float],
                   font_size: int, color: str = "#ffffff", bold: bool = True,
                   shadow: bool = True, shadow_color: str = "#000000"):
        """Draw text with optional shadow."""
        draw = ImageDraw.Draw(img)
        
        # Try to load font
        try:
            font = ImageFont.truetype("arialbd.ttf" if bold else "arial.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
            except:
                font = ImageFont.load_default()
        
        # Calculate position
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = int(position[0] * self.width - text_width / 2)
        y = int(position[1] * self.height - text_height / 2)
        
        # Draw shadow
        if shadow:
            draw.text((x + 3, y + 3), text, font=font, fill=shadow_color)
        
        # Draw text
        draw.text((x, y), text, font=font, fill=color)
    
    def _get_bars(self, audio_chunk: np.ndarray, num_bars: int = 60) -> np.ndarray:
        """Extract frequency bars from audio chunk using FFT."""
        if len(audio_chunk) == 0:
            return np.zeros(num_bars)
        
        # FFT
        fft = np.fft.rfft(audio_chunk)
        magnitudes = np.abs(fft)
        
        # Divide into frequency bands
        bands = np.array_split(magnitudes, num_bars)
        bars = np.array([np.mean(band) if len(band) > 0 else 0 for band in bands])
        
        # Normalize
        max_val = np.max(bars)
        if max_val > 0:
            bars = bars / max_val
        
        return bars


class WaveformVisualizer(BaseVisualizer):
    """Classic waveform visualizer with centered line."""
    
    def render_frame(self, audio_chunk: np.ndarray,
                     energy: float, bpm: float = 140,
                     colors: dict = None, text_overlay: dict = None) -> np.ndarray:
        """Render waveform frame."""
        colors = colors or {}
        bg = colors.get('background', '#0a0a0a')
        primary = colors.get('primary', '#ffffff')
        secondary = colors.get('secondary', '#888888')
        accent = colors.get('accent', '#ff3366')
        
        img, draw = self._create_base_image(bg)
        
        # Draw waveform
        if len(audio_chunk) > 0:
            # Resample to fit width
            samples_per_pixel = max(1, len(audio_chunk) // self.width)
            waveform = []
            
            for i in range(0, min(len(audio_chunk), self.width * samples_per_pixel), samples_per_pixel):
                chunk = audio_chunk[i:i+samples_per_pixel]
                if len(chunk) > 0:
                    waveform.append(np.mean(np.abs(chunk)))
                else:
                    waveform.append(0)
            
            waveform = np.array(waveform)
            
            # Normalize
            max_val = np.max(waveform) if np.max(waveform) > 0 else 1
            waveform = waveform / max_val
            
            # Scale by energy
            waveform = waveform * energy * (self.height * 0.35)
            
            # Draw center line
            center_y = self.height // 2
            
            for i in range(len(waveform) - 1):
                x1 = int(i * self.width / len(waveform))
                x2 = int((i + 1) * self.width / len(waveform))
                
                y1_top = int(center_y - waveform[i])
                y1_bottom = int(center_y + waveform[i])
                
                # Color based on amplitude
                intensity = waveform[i] / (self.height * 0.35) if self.height > 0 else 0
                if intensity > 0.7:
                    color = accent
                elif intensity > 0.4:
                    color = primary
                else:
                    color = secondary
                
                # Draw vertical line
                draw.line([(x1, y1_top), (x1, y1_bottom)], fill=color, width=2)
        
        # Draw glow effect around center
        glow_color = colors.get('glow', accent)
        glow_intensity = int(energy * 30)
        if glow_intensity > 0:
            draw.line([(0, center_y - 2), (self.width, center_y - 2)], 
                     fill=glow_color, width=glow_intensity)
        
        # Text overlay
        if text_overlay:
            text_color = colors.get('text', '#ffffff')
            shadow_color = colors.get('text_shadow', '#000000')
            
            if 'title' in text_overlay:
                self._draw_text(img, text_overlay['title'], 
                              (0.5, 0.12), 72, text_color, shadow_color=shadow_color)
            if 'subtitle' in text_overlay:
                self._draw_text(img, text_overlay['subtitle'],
                              (0.5, 0.22), 36, text_color, bold=False, shadow_color=shadow_color)
            if 'info' in text_overlay:
                self._draw_text(img, text_overlay['info'],
                              (0.5, 0.88), 24, text_color, bold=False, shadow_color=shadow_color)
        
        return np.array(img)


class SpectrumVisualizer(BaseVisualizer):
    """Frequency spectrum bar visualizer."""
    
    def __init__(self, width: int = 1920, height: int = 1080, fps: int = 30):
        super().__init__(width, height, fps)
        self.prev_bars = None
        self.smoothing = 0.3
    
    def render_frame(self, audio_chunk: np.ndarray,
                     energy: float, bpm: float = 140,
                     colors: dict = None, text_overlay: dict = None) -> np.ndarray:
        """Render spectrum bars frame."""
        colors = colors or {}
        bg = colors.get('background', '#0a0a0a')
        primary = colors.get('primary', '#00ff88')
        secondary = colors.get('secondary', '#004422')
        accent = colors.get('accent', '#00cc66')
        
        img, draw = self._create_base_image(bg)
        
        # Get frequency bars
        num_bars = 64
        bars = self._get_bars(audio_chunk, num_bars)
        
        # Apply smoothing
        if self.prev_bars is not None and len(self.prev_bars) == len(bars):
            bars = self.smoothing * self.prev_bars + (1 - self.smoothing) * bars
        self.prev_bars = bars.copy()
        
        # Scale bars
        bar_width = self.width // num_bars
        max_bar_height = int(self.height * 0.6)
        center_y = self.height // 2
        
        for i, bar_height_norm in enumerate(bars):
            bar_height = int(bar_height_norm * energy * max_bar_height)
            
            x = i * bar_width + bar_width // 4
            bar_w = bar_width // 2
            
            # Color gradient based on height
            t = bar_height / max_bar_height if max_bar_height > 0 else 0
            if t > 0.7:
                color = accent
            elif t > 0.4:
                color = primary
            else:
                color = secondary
            
            # Draw mirrored bars (up and down from center)
            draw.rectangle(
                [x, center_y - bar_height, x + bar_w, center_y + bar_height],
                fill=color
            )
        
        # Text overlay
        if text_overlay:
            text_color = colors.get('text', '#ffffff')
            shadow_color = colors.get('text_shadow', '#000000')
            
            if 'title' in text_overlay:
                self._draw_text(img, text_overlay['title'],
                              (0.5, 0.12), 72, text_color, shadow_color=shadow_color)
            if 'subtitle' in text_overlay:
                self._draw_text(img, text_overlay['subtitle'],
                              (0.5, 0.22), 36, text_color, bold=False, shadow_color=shadow_color)
            if 'info' in text_overlay:
                self._draw_text(img, text_overlay['info'],
                              (0.5, 0.88), 24, text_color, bold=False, shadow_color=shadow_color)
        
        return np.array(img)


class ParticleVisualizer(BaseVisualizer):
    """Floating particle visualizer for chill genres."""
    
    def __init__(self, width: int = 1920, height: int = 1080, fps: int = 30):
        super().__init__(width, height, fps)
        self.particles = []
        self._init_particles(100)
    
    def _init_particles(self, count: int):
        """Initialize particle positions."""
        self.particles = [
            {
                'x': np.random.randint(0, self.width),
                'y': np.random.randint(0, self.height),
                'vx': np.random.uniform(-2, 2),
                'vy': np.random.uniform(-1, -0.2),
                'size': np.random.randint(2, 6),
                'opacity': np.random.uniform(0.3, 1.0),
                'phase': np.random.uniform(0, 2 * np.pi)
            }
            for _ in range(count)
        ]
    
    def render_frame(self, audio_chunk: np.ndarray,
                     energy: float, bpm: float = 140,
                     colors: dict = None, text_overlay: dict = None) -> np.ndarray:
        """Render particle frame."""
        colors = colors or {}
        bg = colors.get('background', '#2d2d2d')
        primary = colors.get('primary', '#a8dadc')
        secondary = colors.get('secondary', '#457b9d')
        accent = colors.get('accent', '#f1faee')
        
        img, draw = self._create_base_image(bg)
        
        # Update and draw particles
        for p in self.particles:
            # Update position
            p['x'] += p['vx'] * (1 + energy * 2)
            p['y'] += p['vy'] * (1 + energy * 0.5)
            
            # Wrap around
            if p['x'] < 0:
                p['x'] = self.width
            elif p['x'] > self.width:
                p['x'] = 0
            if p['y'] < 0:
                p['y'] = self.height
            elif p['y'] > self.height:
                p['y'] = 0
            
            # Oscillate size with energy
            oscillation = np.sin(self.frame_count * 0.05 + p['phase'])
            size = int(p['size'] * (1 + energy * oscillation * 0.5))
            size = max(1, size)
            
            # Color based on height
            t = p['y'] / self.height
            if t < 0.3:
                color = accent
            elif t < 0.7:
                color = primary
            else:
                color = secondary
            
            # Draw particle
            rgb = self._hex_to_rgb(color)
            alpha = int(p['opacity'] * 255)
            
            draw.ellipse(
                [p['x'] - size, p['y'] - size, p['x'] + size, p['y'] + size],
                fill=color
            )
        
        self.frame_count += 1
        
        # Text overlay
        if text_overlay:
            text_color = colors.get('text', '#f1faee')
            shadow_color = colors.get('text_shadow', '#1d1d1d')
            
            if 'title' in text_overlay:
                self._draw_text(img, text_overlay['title'],
                              (0.5, 0.12), 68, text_color, shadow_color=shadow_color)
            if 'subtitle' in text_overlay:
                self._draw_text(img, text_overlay['subtitle'],
                              (0.5, 0.22), 34, text_color, bold=False, shadow_color=shadow_color)
            if 'info' in text_overlay:
                self._draw_text(img, text_overlay['info'],
                              (0.5, 0.88), 24, text_color, bold=False, shadow_color=shadow_color)
        
        return np.array(img)
