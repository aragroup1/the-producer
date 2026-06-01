"""Shorts/Reels/TikTok video generator.

Automatically extracts the best hook from a beat and generates
a vertical 9:16 video optimized for short-form platforms.
"""

import os
import numpy as np
import soundfile as sf
import structlog
from typing import Dict, Optional, Any, List, Tuple

from .renderer import VideoRenderer
from .templates import TemplateRegistry

logger = structlog.get_logger()


class ShortsGenerator:
    """Generate short-form videos from beats."""
    
    # Optimal durations per platform
    PLATFORM_DURATIONS = {
        'youtube_shorts': (15, 60),   # 15-60 seconds
        'tiktok': (15, 60),           # 15-60 seconds
        'instagram_reels': (15, 90),  # 15-90 seconds
    }
    
    # Default hook duration
    DEFAULT_HOOK_DURATION = 30.0
    
    def __init__(self, output_dir: str = "./output/videos/shorts"):
        self.output_dir = output_dir
        self.renderer = VideoRenderer(output_dir=output_dir)
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_short(self, audio_path: str, beat_info: Dict[str, Any],
                       platform: str = 'youtube_shorts',
                       duration: Optional[float] = None,
                       auto_detect_hook: bool = True) -> Optional[str]:
        """Generate a short-form video.
        
        Args:
            audio_path: Path to full beat audio
            beat_info: Beat metadata
            platform: Target platform
            duration: Override duration, or auto-select
            auto_detect_hook: Automatically find the best hook section
        
        Returns:
            Path to generated short video
        """
        # Validate platform
        if platform not in self.PLATFORM_DURATIONS:
            logger.warning("unknown_platform", platform=platform, 
                         defaulting='youtube_shorts')
            platform = 'youtube_shorts'
        
        # Determine duration
        min_dur, max_dur = self.PLATFORM_DURATIONS[platform]
        if duration is None:
            duration = min(max_dur, self.DEFAULT_HOOK_DURATION)
        duration = max(min_dur, min(max_dur, duration))
        
        # Find hook section
        if auto_detect_hook:
            hook_start, hook_confidence = self._detect_hook(audio_path, duration)
            logger.info("hook_detected", start=hook_start, 
                       confidence=hook_confidence)
        else:
            hook_start = 0.0
        
        # Prepare beat info for short
        short_info = dict(beat_info)
        short_info['aspect_ratio'] = '9:16'
        short_info['platform'] = platform
        
        # Generate output path
        beat_id = beat_info.get('beat_id', 'unknown')
        output_path = os.path.join(
            self.output_dir,
            f"{beat_id}_{platform}.mp4"
        )
        
        # Render
        result = self.renderer.render_short(
            audio_path,
            short_info,
            hook_start=hook_start,
            hook_duration=duration,
            output_path=output_path
        )
        
        if result:
            logger.info("short_generated", 
                       platform=platform,
                       path=result,
                       duration=duration,
                       hook_start=hook_start)
        
        return result
    
    def generate_all_platforms(self, audio_path: str, 
                               beat_info: Dict[str, Any]) -> Dict[str, Optional[str]]:
        """Generate shorts for all platforms.
        
        Returns:
            Dict mapping platform name to video path
        """
        results = {}
        
        for platform in self.PLATFORM_DURATIONS.keys():
            try:
                path = self.generate_short(audio_path, beat_info, platform=platform)
                results[platform] = path
            except Exception as e:
                logger.error("short_generation_failed", 
                           platform=platform, error=str(e))
                results[platform] = None
        
        return results
    
    def _detect_hook(self, audio_path: str, 
                     target_duration: float) -> Tuple[float, float]:
        """Detect the best hook section in a beat.
        
        Uses energy analysis to find the most intense section
        that fits the target duration.
        
        Returns:
            (start_time, confidence_score)
        """
        try:
            audio, sr = sf.read(audio_path)
            if audio.ndim > 1:
                audio = audio.mean(axis=1)
        except Exception as e:
            logger.error("audio_load_failed", error=str(e))
            return 0.0, 0.0
        
        total_duration = len(audio) / sr
        
        # If beat is shorter than target, start from beginning
        if total_duration <= target_duration:
            return 0.0, 1.0
        
        # Analyze energy in windows
        window_size = int(target_duration * sr)
        hop_size = int(5 * sr)  # 5-second hops
        
        best_start = 0
        best_energy = 0
        
        for start_sample in range(0, len(audio) - window_size, hop_size):
            window = audio[start_sample:start_sample + window_size]
            
            # Calculate energy metrics
            rms = np.sqrt(np.mean(window ** 2))
            
            # Onset density (number of significant energy spikes)
            frame_size = int(0.1 * sr)  # 100ms frames
            frames = [window[i:i+frame_size] for i in range(0, len(window), frame_size)]
            energies = [np.sqrt(np.mean(f ** 2)) for f in frames if len(f) > 0]
            
            if len(energies) > 1:
                # Count onsets (energy increases)
                onsets = sum(1 for i in range(1, len(energies)) 
                           if energies[i] > energies[i-1] * 1.5)
                onset_density = onsets / len(energies)
            else:
                onset_density = 0
            
            # Combined score: energy + onset density
            score = rms * (1 + onset_density * 2)
            
            if score > best_energy:
                best_energy = score
                best_start = start_sample / sr
        
        # Normalize confidence
        max_possible = np.sqrt(np.mean(audio ** 2)) * 3
        confidence = min(1.0, best_energy / max_possible) if max_possible > 0 else 0.5
        
        # Avoid starting too close to end
        if best_start + target_duration > total_duration - 5:
            best_start = max(0, total_duration - target_duration - 5)
        
        return best_start, confidence
    
    def _get_beat_drop_times(self, audio_path: str) -> List[float]:
        """Detect beat drop/change moments.
        
        Returns:
            List of timestamps where significant changes occur
        """
        try:
            audio, sr = sf.read(audio_path)
            if audio.ndim > 1:
                audio = audio.mean(axis=1)
        except Exception:
            return []
        
        # Calculate energy in short windows
        window_size = int(2 * sr)  # 2-second windows
        hop_size = int(0.5 * sr)   # 0.5-second hops
        
        energies = []
        times = []
        
        for start in range(0, len(audio) - window_size, hop_size):
            window = audio[start:start + window_size]
            energy = np.sqrt(np.mean(window ** 2))
            energies.append(energy)
            times.append(start / sr)
        
        # Find significant energy increases (drops)
        drops = []
        for i in range(2, len(energies) - 2):
            # Check if this window is significantly higher than previous
            prev_avg = np.mean(energies[i-2:i])
            if prev_avg > 0 and energies[i] > prev_avg * 1.8:
                drops.append(times[i])
        
        return drops
    
    def generate_hook_preview(self, audio_path: str, 
                              beat_info: Dict[str, Any],
                              preview_duration: float = 15.0) -> Optional[str]:
        """Generate a very short hook preview (for teasers).
        
        Args:
            audio_path: Full beat audio
            beat_info: Beat metadata
            preview_duration: Duration in seconds (default 15)
        
        Returns:
            Path to preview video
        """
        # Find the most intense 15-second section
        hook_start, confidence = self._detect_hook(audio_path, preview_duration)
        
        # Use the drop if available
        drops = self._get_beat_drop_times(audio_path)
        if drops:
            # Pick the drop that's closest to the detected hook
            best_drop = min(drops, key=lambda d: abs(d - hook_start))
            if abs(best_drop - hook_start) < 10:  # Within 10 seconds
                hook_start = best_drop
        
        beat_id = beat_info.get('beat_id', 'unknown')
        output_path = os.path.join(
            self.output_dir,
            f"{beat_id}_preview.mp4"
        )
        
        short_info = dict(beat_info)
        short_info['aspect_ratio'] = '9:16'
        short_info['title'] = beat_info.get('title', '') + ' 🔥'
        
        return self.renderer.render_short(
            audio_path, short_info,
            hook_start=hook_start,
            hook_duration=preview_duration,
            output_path=output_path
        )
