"""VST host for rendering MIDI through virtual instruments."""

import os
import subprocess
import tempfile
from typing import Dict, List, Any, Optional
from pathlib import Path
import structlog

logger = structlog.get_logger()


class FluidSynthHost:
    """FluidSynth-based sound rendering host."""
    
    def __init__(self, soundfont_path: Optional[str] = None, 
                 sample_rate: int = 44100, buffer_size: int = 512):
        self.soundfont_path = soundfont_path or os.getenv('SOUNDFONT_PATH', '/app/soundfonts')
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.default_soundfont = self._find_default_soundfont()
    
    def _find_default_soundfont(self) -> Optional[str]:
        """Find a default soundfont file."""
        sf_dir = Path(self.soundfont_path)
        
        if not sf_dir.exists():
            return None
        
        # Prefer GeneralUser GS or FluidR3
        for name in ["GeneralUser_GS", "FluidR3_GM", "fluid", "general"]:
            matches = list(sf_dir.glob(f"*{name}*.sf2"))
            if matches:
                return str(matches[0])
        
        # Any sf2 file
        matches = list(sf_dir.glob("*.sf2"))
        if matches:
            return str(matches[0])
        
        return None
    
    def render_midi(
        self,
        midi_path: str,
        output_path: str,
        soundfont: Optional[str] = None,
        duration: Optional[float] = None
    ) -> str:
        """Render MIDI file to audio using FluidSynth."""
        
        sf = soundfont or self.default_soundfont
        
        if not sf:
            raise RuntimeError("No soundfont available")
        
        if not Path(sf).exists():
            raise FileNotFoundError(f"Soundfont not found: {sf}")
        
        cmd = [
            "fluidsynth",
            "-ni",  # No shell, just render
            "-g", "1.0",  # Gain
            "-r", str(self.sample_rate),
            "-o", f"audio.period-size={self.buffer_size}",
            "-F", output_path,  # Output file
            sf,
            midi_path
        ]
        
        logger.info("rendering_midi", midi=midi_path, output=output_path, soundfont=sf)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode != 0:
                logger.error("fluidsynth_error", error=result.stderr)
                raise RuntimeError(f"FluidSynth failed: {result.stderr}")
            
            logger.info("render_complete", output=output_path)
            return output_path
            
        except subprocess.TimeoutExpired:
            logger.error("render_timeout", midi=midi_path)
            raise RuntimeError("Rendering timed out")
    
    def render_stems(
        self,
        midi_path: str,
        output_dir: str,
        sound_map: Dict[str, Any],
        soundfont: Optional[str] = None
    ) -> Dict[str, str]:
        """Render each track as a separate stem."""
        
        # For FluidSynth, we render the full mix
        # True stem separation requires per-track MIDI files
        
        output_path = os.path.join(output_dir, "mix.wav")
        self.render_midi(midi_path, output_path, soundfont)
        
        return {"mix": output_path}
    
    def get_soundfont_info(self, soundfont_path: str) -> Dict[str, Any]:
        """Get information about a soundfont."""
        cmd = ["fluidsynth", "-ni", "-d", "1", soundfont_path]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            # Parse output for preset info
            presets = []
            for line in result.stderr.split('\n'):
                if 'preset' in line.lower():
                    presets.append(line.strip())
            
            return {
                "path": soundfont_path,
                "presets": presets[:20],  # First 20 presets
                "preset_count": len(presets)
            }
        except Exception as e:
            return {
                "path": soundfont_path,
                "error": str(e)
            }


class VSTHost:
    """Placeholder for future VST hosting (JUCE-based)."""
    
    def __init__(self, vst_path: Optional[str] = None):
        self.vst_path = vst_path or os.getenv('VST_PATH', '/app/vsts')
    
    def list_available_vsts(self) -> List[Dict[str, str]]:
        """List available VST plugins."""
        vst_dir = Path(self.vst_path)
        
        if not vst_dir.exists():
            return []
        
        vsts = []
        for ext in ['*.vst3', '*.dll', '*.so', '*.dylib']:
            for vst_file in vst_dir.glob(ext):
                vsts.append({
                    "name": vst_file.stem,
                    "path": str(vst_file),
                    "format": ext.replace('*', '')
                })
        
        return vsts
    
    def load_vst(self, vst_path: str) -> bool:
        """Load a VST plugin."""
        # TODO: Implement JUCE-based VST loading
        logger.warning("vst_loading_not_implemented", path=vst_path)
        return False
    
    def render_with_vst(
        self,
        midi_path: str,
        output_path: str,
        vst_path: str,
        preset: Optional[str] = None
    ) -> str:
        """Render MIDI through a VST plugin."""
        # TODO: Implement VST rendering
        raise NotImplementedError("VST rendering requires JUCE integration")
