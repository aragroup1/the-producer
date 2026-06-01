"""Video preview generator for social media.

Creates waveform visualizations with branding overlays.
Uses matplotlib + ffmpeg for rendering.
"""

import os
import tempfile
from typing import Optional, Tuple
from pathlib import Path
import numpy as np
import structlog

logger = structlog.get_logger()


class VideoPreviewGenerator:
    """Generate video previews from audio files."""
    
    # Color schemes by genre
    COLOR_SCHEMES = {
        "trap": {"bg": "#0a0a0a", "wave": "#ff3366", "accent": "#ff0066"},
        "drill": {"bg": "#0d0d0d", "wave": "#00ff88", "accent": "#00cc66"},
        "boom_bap": {"bg": "#1a1a2e", "wave": "#f4a261", "accent": "#e76f51"},
        "rnb": {"bg": "#1a1a2e", "wave": "#9b5de5", "accent": "#f15bb5"},
        "afrobeats": {"bg": "#0d1b2a", "wave": "#ffbe0b", "accent": "#fb5607"},
        "lofi": {"bg": "#2d2d2d", "wave": "#a8dadc", "accent": "#457b9d"},
        "default": {"bg": "#0a0a0a", "wave": "#ffffff", "accent": "#cccccc"}
    }
    
    def __init__(self, output_dir: str = "./output/videos"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_waveform_video(self, audio_path: str, title: str,
                                genre: str = "default",
                                duration: Optional[float] = None,
                                resolution: Tuple[int, int] = (1080, 1920)) -> Optional[str]:
        """Generate a vertical video with waveform visualization.
        
        Args:
            audio_path: Path to audio file
            title: Beat title for overlay
            genre: Genre for color scheme
            duration: Max video duration (seconds), None = full audio
            resolution: Output resolution (width, height)
        
        Returns:
            Path to generated video file
        """
        try:
            import soundfile as sf
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            logger.error("missing_dependencies", 
                        message="Install soundfile and Pillow for video generation")
            return None
        
        # Load audio
        audio, sr = sf.read(audio_path)
        if audio.ndim > 1:
            audio = audio.mean(axis=1)
        
        # Determine duration
        audio_duration = len(audio) / sr
        if duration and duration < audio_duration:
            audio = audio[:int(duration * sr)]
            audio_duration = duration
        
        # Generate frames
        colors = self.COLOR_SCHEMES.get(genre, self.COLOR_SCHEMES["default"])
        
        # Create frame directory
        frame_dir = tempfile.mkdtemp()
        
        # Video parameters
        fps = 30
        total_frames = int(audio_duration * fps)
        
        # Generate frames
        for frame_idx in range(total_frames):
            frame = self._render_frame(
                audio, sr, frame_idx, fps, total_frames,
                title, colors, resolution
            )
            
            frame_path = os.path.join(frame_dir, f"frame_{frame_idx:06d}.png")
            frame.save(frame_path)
        
        # Compile video with ffmpeg
        output_path = os.path.join(
            self.output_dir,
            f"{Path(audio_path).stem}.mp4"
        )
        
        self._compile_video(frame_dir, audio_path, output_path, fps)
        
        # Cleanup frames
        import shutil
        shutil.rmtree(frame_dir)
        
        logger.info("video_generated", output=output_path)
        return output_path
    
    def _render_frame(self, audio: np.ndarray, sr: int, frame_idx: int,
                      fps: int, total_frames: int,
                      title: str, colors: dict,
                      resolution: Tuple[int, int]) -> "Image.Image":
        """Render a single video frame."""
        from PIL import Image, ImageDraw, ImageFont
        
        width, height = resolution
        
        # Create image
        img = Image.new('RGB', (width, height), colors["bg"])
        draw = ImageDraw.Draw(img)
        
        # Calculate waveform window
        samples_per_frame = sr // fps
        start_sample = frame_idx * samples_per_frame
        end_sample = min(start_sample + samples_per_frame * 2, len(audio))
        
        window = audio[start_sample:end_sample]
        if len(window) == 0:
            return img
        
        # Draw waveform
        bar_count = 60
        bar_width = width // bar_count
        samples_per_bar = len(window) // bar_count
        
        for i in range(bar_count):
            bar_start = i * samples_per_bar
            bar_end = min(bar_start + samples_per_bar, len(window))
            bar_samples = window[bar_start:bar_end]
            
            if len(bar_samples) > 0:
                amplitude = np.abs(bar_samples).mean()
                bar_height = int(amplitude * height * 0.6)
                
                x = i * bar_width + bar_width // 4
                y_center = height // 2
                
                # Draw bar
                draw.rectangle(
                    [x, y_center - bar_height, x + bar_width // 2, y_center + bar_height],
                    fill=colors["wave"]
                )
        
        # Draw title
        try:
            font = ImageFont.truetype("arial.ttf", 48)
        except:
            font = ImageFont.load_default()
        
        # Title background
        title_bbox = draw.textbbox((0, 0), title, font=font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) // 2
        title_y = height - 150
        
        draw.rectangle(
            [title_x - 20, title_y - 10, title_x + title_width + 20, title_y + 60],
            fill=(0, 0, 0, 180)
        )
        draw.text((title_x, title_y), title, fill=colors["accent"], font=font)
        
        # Progress bar
        progress = (frame_idx / total_frames) if total_frames > 0 else 0
        draw.rectangle(
            [0, height - 10, int(width * progress), height],
            fill=colors["accent"]
        )
        
        return img
    
    def _compile_video(self, frame_dir: str, audio_path: str,
                       output_path: str, fps: int):
        """Compile frames + audio into MP4 using ffmpeg."""
        import subprocess
        
        cmd = [
            "ffmpeg", "-y",
            "-framerate", str(fps),
            "-i", os.path.join(frame_dir, "frame_%06d.png"),
            "-i", audio_path,
            "-c:v", "libx264",
            "-c:a", "aac",
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-shortest",
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            logger.error("ffmpeg_failed", error=str(e))
            raise
        except FileNotFoundError:
            logger.error("ffmpeg_not_found", 
                        message="Install ffmpeg for video generation")
            raise
