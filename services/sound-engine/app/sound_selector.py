"""AI sound selection engine."""

import os
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
import structlog

logger = structlog.get_logger()


class SoundSelector:
    """Intelligently assign sounds to MIDI tracks based on genre and mood."""
    
    # Default soundfont assignments by genre
    SOUNDFONT_ASSIGNMENTS = {
        "trap": {
            "drums": {
                "kick": "Acoustic Bass Drum",
                "snare": "Acoustic Snare",
                "hihat": "Closed Hi-Hat",
                "open_hihat": "Open Hi-Hat",
                "clap": "Hand Clap",
                "crash": "Crash Cymbal 1",
                "ride": "Ride Cymbal 1"
            },
            "bass": {
                "type": "synth_bass",
                "program": 39,  # Synth Bass 1
                "description": "Deep sub bass"
            },
            "synth_lead": {
                "type": "lead",
                "program": 81,  # Lead 1 (square)
                "description": "Bright lead synth"
            },
            "synth_pad": {
                "type": "pad",
                "program": 95,  # Pad 1 (new age)
                "description": "Atmospheric pad"
            },
            "piano": {
                "type": "piano",
                "program": 1,  # Acoustic Grand Piano
                "description": "Bright piano"
            },
            "pluck": {
                "type": "pluck",
                "program": 25,  # Acoustic Guitar (nylon)
                "description": "Plucked synth"
            }
        },
        "drill": {
            "drums": {
                "kick": "Acoustic Bass Drum",
                "snare": "Acoustic Snare",
                "hihat": "Closed Hi-Hat",
                "open_hihat": "Open Hi-Hat",
                "clap": "Hand Clap",
                "crash": "Crash Cymbal 1"
            },
            "bass": {
                "type": "synth_bass",
                "program": 39,
                "description": "Dark sliding bass"
            },
            "synth_lead": {
                "type": "lead",
                "program": 87,  # Lead 7 (fifths)
                "description": "Dark lead"
            },
            "synth_pad": {
                "type": "pad",
                "program": 97,  # Pad 3 (polysynth)
                "description": "Dark pad"
            },
            "piano": {
                "type": "piano",
                "program": 2,  # Bright Acoustic Piano
                "description": "Dark piano"
            }
        },
        "lofi": {
            "drums": {
                "kick": "Acoustic Bass Drum",
                "snare": "Acoustic Snare",
                "hihat": "Closed Hi-Hat",
                "open_hihat": "Open Hi-Hat",
                "rim": "Side Stick",
                "shaker": "Shaker"
            },
            "bass": {
                "type": "electric_bass",
                "program": 33,  # Electric Bass (finger)
                "description": "Warm bass"
            },
            "synth_lead": {
                "type": "lead",
                "program": 89,  # Pad 2 (warm)
                "description": "Warm lead"
            },
            "synth_pad": {
                "type": "pad",
                "program": 95,
                "description": "Warm pad"
            },
            "piano": {
                "type": "piano",
                "program": 1,
                "description": "Soft piano"
            },
            " Rhodes": {
                "type": "epiano",
                "program": 5,  # Electric Piano 1
                "description": "Rhodes"
            }
        },
        "afrobeats": {
            "drums": {
                "kick": "Acoustic Bass Drum",
                "snare": "Acoustic Snare",
                "hihat": "Closed Hi-Hat",
                "shaker": "Shaker",
                "tom": "Low Tom",
                "perc": "Tambourine"
            },
            "bass": {
                "type": "synth_bass",
                "program": 39,
                "description": "Bouncy bass"
            },
            "synth_lead": {
                "type": "lead",
                "program": 81,
                "description": "Bright lead"
            },
            "synth_pad": {
                "type": "pad",
                "program": 91,
                "description": "Bright pad"
            },
            "piano": {
                "type": "piano",
                "program": 1,
                "description": "Bright piano"
            },
            "guitar": {
                "type": "guitar",
                "program": 25,
                "description": "Nylon guitar"
            }
        }
    }
    
    def __init__(self, soundfont_path: Optional[str] = None):
        self.soundfont_path = soundfont_path or os.getenv('SOUNDFONT_PATH', '/app/soundfonts')
        self.assignments = {}
    
    def assign_sounds(
        self,
        genre: str,
        mood: str = "dark",
        tracks: List[str] = None,
        composition_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Assign sounds to tracks based on genre."""
        
        genre_assignments = self.SOUNDFONT_ASSIGNMENTS.get(genre, self.SOUNDFONT_ASSIGNMENTS["trap"])
        
        sound_map = {
            "genre": genre,
            "mood": mood,
            "tracks": {}
        }
        
        # Assign sounds to each track
        for track_name, track_config in genre_assignments.items():
            if track_name == "drums":
                # Drums use GM mapping
                sound_map["tracks"][track_name] = {
                    "type": "drum_kit",
                    "channel": 9,  # GM drum channel
                    "instruments": track_config
                }
            else:
                # Melodic instruments
                sound_map["tracks"][track_name] = {
                    "type": track_config.get("type", "synth"),
                    "program": track_config.get("program", 1),
                    "channel": self._get_channel(track_name),
                    "description": track_config.get("description", ""),
                    "soundfont": self._find_soundfont(track_name, genre)
                }
        
        logger.info("sounds_assigned", genre=genre, tracks=list(sound_map["tracks"].keys()))
        
        return sound_map
    
    def _get_channel(self, track_name: str) -> int:
        """Get MIDI channel for track."""
        channels = {
            "bass": 0,
            "synth_lead": 1,
            "synth_pad": 2,
            "piano": 3,
            "pluck": 4,
            "guitar": 5,
            " Rhodes": 6
        }
        return channels.get(track_name, 0)
    
    def _find_soundfont(self, track_name: str, genre: str) -> Optional[str]:
        """Find appropriate soundfont file."""
        soundfont_dir = Path(self.soundfont_path)
        
        if not soundfont_dir.exists():
            return None
        
        # Look for genre-specific soundfonts
        patterns = [
            f"*{genre}*{track_name}*.sf2",
            f"*{track_name}*.sf2",
            f"*GeneralUser*.sf2",
            f"*FluidR3*.sf2",
            "*.sf2"
        ]
        
        for pattern in patterns:
            matches = list(soundfont_dir.glob(pattern))
            if matches:
                return str(matches[0])
        
        return None
    
    def get_available_soundfonts(self) -> List[Dict[str, str]]:
        """List available soundfont files."""
        soundfont_dir = Path(self.soundfont_path)
        
        if not soundfont_dir.exists():
            return []
        
        soundfonts = []
        for sf2_file in soundfont_dir.glob("*.sf2"):
            soundfonts.append({
                "name": sf2_file.stem,
                "path": str(sf2_file),
                "size_mb": round(sf2_file.stat().st_size / (1024 * 1024), 2)
            })
        
        return soundfonts
    
    def preview_sound(self, soundfont_path: str, program: int, note: int = 60) -> str:
        """Generate a preview of a sound."""
        # TODO: Render a short preview using FluidSynth
        pass
