"""Video rendering engine using FFmpeg.

Renders audio + visualizer frames into MP4 videos.
Supports multiple formats: 16:9 YouTube, 9:16 Shorts/Reels/TikTok.
"""

import os
import subprocess
import tempfile
import structlog
from typing import Dict, Optional, Tuple, Any
from pathlib import Path

import numpy as np
import soundfile as sf
from PIL import Image

from .templates import TemplateRegistry, VideoTemplate
from .visualizers import WaveformVisualizer, SpectrumVisualizer, ParticleVisualizer

logger = structlog.get_logger()


class VideoRenderer:
    """Main video rendering engine."""
    
    def __init__(self, output_dir: str = "./output/videos"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Check ffmpeg
        self.ffmpeg_available = self._check_ffmpeg()
        if not self.ffmpeg_available:
            logger.warning("ffmpeg_not_found", message="Video rendering requires ffmpeg")
    
    def _check_ffmpeg(self) -> bool:
        """Check if ffmpeg is available."""
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def render_video(self, audio_path: str, beat_info: Dict[str, Any],
                     template_name: Optional[str] = None,
                     output_path: Optional[str] = None,
                     duration: Optional[float] = None) -> Optional[str]:
        """Render a full video from audio file.
        
        Args:
            audio_path: Path to audio file (WAV/MP3)
            beat_info: Dict with genre, bpm, key, title, etc.
            template_name: Specific template to use, or auto-select
            output_path: Output file path, or auto-generate
            duration: Max duration in seconds, or full audio
        
        Returns:
            Path to rendered MP4 file
        """
        if not self.ffmpeg_available:
            logger.error("ffmpeg_required", message="Install ffmpeg to render videos")
            return None
        
        # Load audio
        try:
            audio, sr = sf.read(audio_path)
            if audio.ndim > 1:
                audio = audio.mean(axis=1)
        except Exception as e:
            logger.error("audio_load_failed", path=audio_path, error=str(e))
            return None
        
        # Determine duration
        audio_duration = len(audio) / sr
        if duration and duration < audio_duration:
            audio = audio[:int(duration * sr)]
            audio_duration = duration
        
        # Select template
        genre = beat_info.get('genre', 'default')
        aspect = beat_info.get('aspect_ratio', '16:9')
        
        if template_name:
            template = TemplateRegistry.get(template_name)
        else:
            template = TemplateRegistry.get_for_genre(genre, aspect)
        
        if not template:
            logger.error("template_not_found", genre=genre, aspect=aspect)
            return None
        
        logger.info("rendering_video",
                   genre=genre,
                   template=template.name,
                   duration=audio_duration,
                   resolution=template.resolution)
        
        # Generate output path
        if not output_path:
            beat_id = beat_info.get('beat_id', 'unknown')
            suffix = '_short' if aspect == '9:16' else ''
            output_path = os.path.join(
                self.output_dir,
                f"{beat_id}{suffix}.mp4"
            )
        
        # Create visualizer
        visualizer = self._create_visualizer(template)
        
        # Prepare text overlay
        text_overlay = self._prepare_text_overlay(beat_info, template)
        
        # Render frames
        frame_dir = tempfile.mkdtemp()
        fps = template.fps
        total_frames = int(audio_duration * fps)
        samples_per_frame = sr // fps
        
        colors = {
            'background': template.color_scheme.background,
            'primary': template.color_scheme.primary,
            'secondary': template.color_scheme.secondary,
            'accent': template.color_scheme.accent,
            'glow': template.color_scheme.glow,
            'text': template.color_scheme.text,
            'text_shadow': template.color_scheme.text_shadow,
        }
        
        try:
            for frame_idx in range(total_frames):
                # Extract audio chunk for this frame
                start_sample = frame_idx * samples_per_frame
                end_sample = min(start_sample + samples_per_frame * 2, len(audio))
                chunk = audio[start_sample:end_sample]
                
                # Calculate energy
                energy = self._calculate_energy(chunk, audio)
                
                # Render frame
                frame = visualizer.render_frame(
                    chunk, energy,
                    bpm=beat_info.get('bpm', 140),
                    colors=colors,
                    text_overlay=text_overlay
                )
                
                # Save frame
                frame_img = Image.fromarray(frame)
                frame_path = os.path.join(frame_dir, f"frame_{frame_idx:06d}.png")
                frame_img.save(frame_path)
                
                # Progress log every 100 frames
                if frame_idx % 100 == 0:
                    progress = (frame_idx / total_frames) * 100
                    logger.info("render_progress", progress=f"{progress:.1f}%")
        
        except Exception as e:
            logger.error("frame_render_failed", error=str(e))
            import shutil
            shutil.rmtree(frame_dir, ignore_errors=True)
            return None
        
        # Compile with ffmpeg
        success = self._compile_video(frame_dir, audio_path, output_path, fps, audio_duration)
        
        # Cleanup
        import shutil
        shutil.rmtree(frame_dir, ignore_errors=True)
        
        if success:
            logger.info("video_rendered", output=output_path, 
                       duration=audio_duration, frames=total_frames)
            return output_path
        else:
            return None
    
    def _create_visualizer(self, template: VideoTemplate):
        """Create visualizer instance from template."""
        width, height = template.resolution
        fps = template.fps
        
        from .templates import VisualizerStyle
        
        if template.visualizer_style == VisualizerStyle.WAVEFORM:
            return WaveformVisualizer(width, height, fps)
        elif template.visualizer_style == VisualizerStyle.SPECTRUM:
            return SpectrumVisualizer(width, height, fps)
        elif template.visualizer_style == VisualizerStyle.PARTICLES:
            return ParticleVisualizer(width, height, fps)
        elif template.visualizer_style == VisualizerStyle.BARS:
            return SpectrumVisualizer(width, height, fps)  # Bars use spectrum
        elif template.visualizer_style == VisualizerStyle.CIRCULAR:
            return WaveformVisualizer(width, height, fps)  # Fallback
        else:
            return WaveformVisualizer(width, height, fps)
    
    def _prepare_text_overlay(self, beat_info: Dict[str, Any], 
                              template: VideoTemplate) -> Dict[str, str]:
        """Prepare text overlay from beat info."""
        genre = beat_info.get('genre', 'Beat')
        bpm = beat_info.get('bpm', '')
        key = beat_info.get('key', '')
        scale = beat_info.get('scale', '')
        
        # Title
        title = beat_info.get('title', f"{genre.replace('_', ' ').title()} Type Beat")
        
        # Subtitle
        subtitle = beat_info.get('subtitle', f"{bpm} BPM • {key} {scale.title()}")
        
        # Info line
        info = beat_info.get('info', "🎹 Free Beat • Subscribe for More")
        
        return {
            'title': title,
            'subtitle': subtitle,
            'info': info
        }
    
    def _calculate_energy(self, chunk: np.ndarray, full_audio: np.ndarray) -> float:
        """Calculate normalized energy level for a chunk."""
        if len(chunk) == 0:
            return 0.0
        
        # RMS energy
        rms = np.sqrt(np.mean(chunk ** 2))
        
        # Normalize against full audio
        max_rms = np.sqrt(np.mean(full_audio ** 2))
        if max_rms > 0:
            energy = rms / max_rms
        else:
            energy = 0.0
        
        # Apply curve for better visual dynamics
        energy = energy ** 0.7  # Compress high values
        
        return min(1.0, max(0.0, energy))
    
    def _parse_fps(self, fps_str: str) -> float:
        """Safely parse FPS from ffprobe output."""
        try:
            if '/' in fps_str:
                num, den = fps_str.split('/')
                return float(num) / float(den) if float(den) != 0 else 0.0
            return float(fps_str)
        except (ValueError, ZeroDivisionError):
            return 0.0

    def _compile_video(self, frame_dir: str, audio_path: str,
                       output_path: str, fps: int, duration: float) -> bool:
        """Compile frames and audio into MP4 using ffmpeg."""
        frame_pattern = os.path.join(frame_dir, "frame_%06d.png")
        
        cmd = [
            'ffmpeg', '-y',
            '-framerate', str(fps),
            '-i', frame_pattern,
            '-i', audio_path,
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-ar', '44100',
            '-pix_fmt', 'yuv420p',
            '-shortest',
            '-t', str(duration),
            output_path
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                logger.error("ffmpeg_compile_failed", 
                           stderr=result.stderr[:500])
                return False
            
            return True
        
        except subprocess.TimeoutExpired:
            logger.error("ffmpeg_timeout")
            return False
        except Exception as e:
            logger.error("ffmpeg_error", error=str(e))
            return False
    
    def render_short(self, audio_path: str, beat_info: Dict[str, Any],
                     hook_start: float = 0.0,
                     hook_duration: float = 30.0,
                     output_path: Optional[str] = None) -> Optional[str]:
        """Render a short-form video (YouTube Shorts / TikTok / Reels).
        
        Args:
            audio_path: Path to audio file
            beat_info: Beat metadata
            hook_start: Start time of hook in seconds
            hook_duration: Duration of hook in seconds (15-60)
            output_path: Output path
        
        Returns:
            Path to rendered short MP4
        """
        # Force 9:16 aspect ratio
        beat_info = dict(beat_info)
        beat_info['aspect_ratio'] = '9:16'
        
        # Extract hook segment
        hook_audio_path = self._extract_audio_segment(
            audio_path, hook_start, hook_duration
        )
        
        if not hook_audio_path:
            return None
        
        try:
            result = self.render_video(
                hook_audio_path,
                beat_info,
                output_path=output_path,
                duration=hook_duration
            )
            return result
        finally:
            # Cleanup temp audio
            if os.path.exists(hook_audio_path):
                os.remove(hook_audio_path)
    
    def _extract_audio_segment(self, audio_path: str, start: float, 
                               duration: float) -> Optional[str]:
        """Extract a segment of audio using ffmpeg."""
        if not self.ffmpeg_available:
            return None
        
        temp_path = tempfile.mktemp(suffix='.wav')
        
        cmd = [
            'ffmpeg', '-y',
            '-i', audio_path,
            '-ss', str(start),
            '-t', str(duration),
            '-acodec', 'pcm_s16le',
            '-ar', '44100',
            '-ac', '1',
            temp_path
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, check=True)
            return temp_path
        except subprocess.CalledProcessError:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return None
    
    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """Get information about a rendered video."""
        if not os.path.exists(video_path):
            return {}
        
        import json
        
        cmd = [
            'ffprobe', '-v', 'quiet',
            '-print_format', 'json',
            '-show_format', '-show_streams',
            video_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            
            format_info = data.get('format', {})
            streams = data.get('streams', [])
            video_stream = next((s for s in streams if s.get('codec_type') == 'video'), {})
            
            return {
                'duration': float(format_info.get('duration', 0)),
                'size_bytes': int(format_info.get('size', 0)),
                'bitrate': int(format_info.get('bit_rate', 0)),
                'width': int(video_stream.get('width', 0)),
                'height': int(video_stream.get('height', 0)),
                'fps': eval(video_stream.get('r_frame_rate', '0/1')),
                'codec': video_stream.get('codec_name', 'unknown')
            }
        except Exception as e:
            logger.error("ffprobe_failed", error=str(e))
            return {}
