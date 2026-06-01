"""Full song structure generator for commercial-length beats.

Generates 2-3 minute beats with proper arrangement:
Intro → Verse → Hook → Verse → Hook → Bridge → Hook → Outro

Each section has different instrumentation, intensity, and variation.
"""

import random
import copy
from typing import Dict, List, Any, Optional
import numpy as np
import structlog

import sys
import os
import importlib.util

# Load genre_library directly (hyphen in path prevents normal import)
_genre_lib_path = os.path.join(os.path.dirname(__file__), 'genre_library.py')
spec = importlib.util.spec_from_file_location('genre_library', _genre_lib_path)
_genre_lib = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_genre_lib)

CHORD_PROGRESSIONS = _genre_lib.CHORD_PROGRESSIONS
DRUM_PATTERNS = _genre_lib.DRUM_PATTERNS
GENRE_CONFIG = _genre_lib.GENRE_CONFIG
SECTION_TEMPLATES = _genre_lib.SECTION_TEMPLATES
ARRANGEMENT_INTENSITY = _genre_lib.ARRANGEMENT_INTENSITY
SECTION_INSTRUMENTS = _genre_lib.SECTION_INSTRUMENTS
get_genre_config = _genre_lib.get_genre_config

# Load other modules
_mt_path = os.path.join(os.path.dirname(__file__), 'music_transformer.py')
spec = importlib.util.spec_from_file_location('music_transformer', _mt_path)
_mt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_mt)
CompositionEngine = _mt.CompositionEngine

_dg_path = os.path.join(os.path.dirname(__file__), 'drum_generator.py')
spec = importlib.util.spec_from_file_location('drum_generator', _dg_path)
_dg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_dg)
DrumPatternGenerator = _dg.DrumPatternGenerator

logger = structlog.get_logger()


class SongStructureGenerator:
    """Generate full song structures with arrangement variation."""
    
    def __init__(self):
        self.composition_engine = CompositionEngine()
    
    def generate_full_beat(self, genre: str = "trap", bpm: int = 140,
                           key: str = "C", scale: str = "minor",
                           mood: str = "dark",
                           structure: str = "standard") -> Dict[str, Any]:
        """Generate a complete 2-3 minute beat with full song structure.
        
        Args:
            genre: Musical genre
            bpm: Tempo in BPM
            key: Musical key
            scale: major or minor
            mood: Sub-genre mood
            structure: short (1:30), standard (2:00), extended (2:30+)
        
        Returns:
            Complete beat data with sections, stems, and arrangement
        """
        logger.info("generating_full_beat", genre=genre, bpm=bpm, key=key, 
                   structure=structure)
        
        # Get template
        template = SECTION_TEMPLATES.get(structure, SECTION_TEMPLATES["standard"])
        
        # Generate base chord progression
        base_progression = self._generate_progression(genre, mood, key)
        
        # Generate sections
        sections = []
        section_data = {}
        current_bar = 0
        
        for section_name, bar_count in template.items():
            logger.debug("generating_section", section=section_name, bars=bar_count)
            
            # Generate section-specific content
            section = self._generate_section(
                section_name=section_name,
                bar_count=bar_count,
                start_bar=current_bar,
                genre=genre,
                bpm=bpm,
                key=key,
                scale=scale,
                base_progression=base_progression,
                intensity=ARRANGEMENT_INTENSITY.get(section_name, 0.5)
            )
            
            sections.append(section)
            section_data[section_name] = section
            current_bar += bar_count
        
        # Calculate total duration
        total_bars = sum(template.values())
        total_duration = total_bars * 4 * 60 / bpm
        
        beat_data = {
            "genre": genre,
            "bpm": bpm,
            "key": key,
            "scale": scale,
            "mood": mood,
            "structure": structure,
            "total_bars": total_bars,
            "total_duration_seconds": total_duration,
            "sections": section_data,
            "section_order": list(template.keys()),
            "chord_progression": base_progression,
            "tracks": self._compile_tracks(sections)
        }
        
        logger.info("full_beat_generated", 
                   duration=f"{total_duration:.1f}s",
                   bars=total_bars,
                   sections=len(sections))
        
        return beat_data
    
    def _generate_progression(self, genre: str, mood: str, key: str) -> List[Dict[str, Any]]:
        """Generate a chord progression for the beat."""
        import importlib.util
        _ce_path = os.path.join(os.path.dirname(__file__), 'chord_engine.py')
        spec = importlib.util.spec_from_file_location('chord_engine', _ce_path)
        _ce = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_ce)
        
        engine = _ce.ChordEngine()
        
        # Get genre progressions
        genre_progs = CHORD_PROGRESSIONS.get(genre, CHORD_PROGRESSIONS["trap"])
        mood_progs = genre_progs.get(mood, list(genre_progs.values())[0])
        
        # Pick a progression
        progression = random.choice(mood_progs)
        
        # Parse into structured format
        result = []
        for chord_name in progression:
            chord_data = engine._parse_chord(chord_name)
            result.append({
                "name": chord_name,
                "root": chord_data["root"],
                "quality": chord_data["quality"],
                "notes": chord_data["notes"],
                "duration_beats": 4
            })
        
        return result
    
    def _generate_section(self, section_name: str, bar_count: int,
                          start_bar: int, genre: str, bpm: int,
                          key: str, scale: str,
                          base_progression: List[Dict],
                          intensity: float) -> Dict[str, Any]:
        """Generate a single song section."""
        
        start_time = start_bar * 4  # 4 beats per bar
        
        # Determine which instruments play
        active_instruments = SECTION_INSTRUMENTS.get(section_name, ["drums", "bass", "lead"])
        
        # Generate drums (if active)
        drums = None
        if "drums" in active_instruments:
            drum_gen = DrumPatternGenerator(genre)
            drum_pattern = drum_gen.generate(bars=bar_count // 4)
            
            # Scale drum pattern to section timing
            drums = self._offset_drum_pattern(drum_pattern, start_time)
        
        # Generate bass (if active)
        bass = None
        if "bass" in active_instruments:
            bass = self._generate_bass_section(
                base_progression, bar_count, start_time, genre, intensity
            )
        
        # Generate melody/lead (if active)
        melody = None
        if "lead" in active_instruments:
            melody = self._generate_melody_section(
                key, scale, bar_count, start_time, genre, intensity
            )
        
        # Generate pads (if active)
        pads = None
        if "pads" in active_instruments:
            pads = self._generate_pad_section(
                base_progression, bar_count, start_time, intensity
            )
        
        # Generate pluck/counter (if active)
        pluck = None
        if "pluck" in active_instruments:
            pluck = self._generate_pluck_section(
                key, scale, bar_count, start_time, intensity
            )
        
        # Generate FX (if active)
        fx = None
        if "fx" in active_instruments:
            fx = self._generate_fx_section(section_name, bar_count, start_time)
        
        return {
            "name": section_name,
            "start_bar": start_bar,
            "bar_count": bar_count,
            "start_time": start_time,
            "intensity": intensity,
            "instruments": active_instruments,
            "tracks": {
                "drums": drums,
                "bass": bass,
                "melody": melody,
                "pads": pads,
                "pluck": pluck,
                "fx": fx
            }
        }
    
    def _offset_drum_pattern(self, pattern: Dict[str, Any], offset_beats: float) -> Dict[str, Any]:
        """Offset a drum pattern by a number of beats."""
        offset_pattern = {}
        for drum_name, hits in pattern.items():
            offset_hits = []
            for time, velocity in hits:
                offset_hits.append((time + offset_beats, velocity))
            offset_pattern[drum_name] = offset_hits
        return offset_pattern
    
    def _generate_bass_section(self, progression: List[Dict], bar_count: int,
                               start_time: float, genre: str, intensity: float) -> List[Dict]:
        """Generate bassline for a section."""
        notes = []
        current_time = start_time
        
        # Repeat progression to fill bars
        bars_per_cycle = len(progression)
        cycles_needed = bar_count // bars_per_cycle + 1
        full_progression = (progression * cycles_needed)[:bar_count]
        
        for chord in full_progression:
            root = chord["notes"][0] - 12  # Bass octave
            
            # Intensity affects complexity
            if intensity > 0.8 and genre in ["trap", "drill", "rage"]:
                # Busy trap bass
                notes.append({"pitch": root, "velocity": 100, "start_time": current_time, "duration": 1.5})
                notes.append({"pitch": root + 12, "velocity": 90, "start_time": current_time + 2, "duration": 2})
            elif intensity < 0.4:
                # Sparse bass
                notes.append({"pitch": root, "velocity": 80, "start_time": current_time, "duration": 4})
            else:
                # Standard bass
                notes.append({"pitch": root, "velocity": 100, "start_time": current_time, "duration": 2})
                notes.append({"pitch": root + 7, "velocity": 90, "start_time": current_time + 2, "duration": 2})
            
            current_time += 4
        
        return notes
    
    def _generate_melody_section(self, key: str, scale: str, bar_count: int,
                                 start_time: float, genre: str, intensity: float) -> List[Dict]:
        """Generate melody for a section."""
        from shared.utils.midi import SCALES, note_name_to_midi
        
        root_note = note_name_to_midi(key, octave=4)
        scale_intervals = SCALES.get(scale, SCALES["minor"])
        
        notes = []
        current_time = start_time
        beats_per_bar = 4
        
        # Higher intensity = more notes
        density = 0.5 + intensity * 0.4  # 0.5 to 0.9
        
        for bar in range(bar_count):
            for beat in range(beats_per_bar):
                if random.random() < density:
                    note_pitch = root_note + random.choice(scale_intervals) + random.choice([0, 12])
                    duration = random.choice([0.25, 0.5, 1.0])
                    velocity = int(60 + intensity * 50)  # 60-110
                    
                    notes.append({
                        "pitch": int(note_pitch),
                        "velocity": velocity,
                        "start_time": current_time,
                        "duration": duration
                    })
                
                current_time += 1.0
        
        return notes
    
    def _generate_pad_section(self, progression: List[Dict], bar_count: int,
                              start_time: float, intensity: float) -> List[Dict]:
        """Generate pad chords for a section."""
        notes = []
        current_time = start_time
        
        bars_per_cycle = len(progression)
        cycles_needed = bar_count // bars_per_cycle + 1
        full_progression = (progression * cycles_needed)[:bar_count]
        
        for chord in full_progression:
            root = chord["notes"][0]
            
            # Wide voicing
            chord_notes = [root, root + 7, root + 12, root + 16]
            
            velocity = int(40 + intensity * 30)  # 40-70
            
            notes.append({
                "pitches": chord_notes,
                "velocity": velocity,
                "start_time": current_time,
                "duration": 4
            })
            
            current_time += 4
        
        return notes
    
    def _generate_pluck_section(self, key: str, scale: str, bar_count: int,
                                start_time: float, intensity: float) -> List[Dict]:
        """Generate pluck/counter melody."""
        from shared.utils.midi import SCALES, note_name_to_midi
        
        root_note = note_name_to_midi(key, octave=5)
        scale_intervals = SCALES.get(scale, SCALES["minor"])
        
        notes = []
        current_time = start_time
        
        # Plucks are sparser than lead
        density = 0.3 + intensity * 0.2
        
        for bar in range(bar_count):
            for beat in range(4):
                if random.random() < density:
                    interval = random.choice([3, 4, 7, 8])
                    note_pitch = root_note + random.choice(scale_intervals)
                    
                    notes.append({
                        "pitch": int(note_pitch),
                        "velocity": int(50 + intensity * 30),
                        "start_time": current_time,
                        "duration": 0.5
                    })
                
                current_time += 1.0
        
        return notes
    
    def _generate_fx_section(self, section_name: str, bar_count: int,
                             start_time: float) -> List[Dict]:
        """Generate FX hits (risers, impacts, etc.)."""
        fx_events = []
        
        if section_name == "intro":
            # Build-up riser
            fx_events.append({"type": "riser", "start_time": start_time, "duration": bar_count * 4})
        
        elif section_name in ["hook", "hook2", "hook3"]:
            # Impact at start
            fx_events.append({"type": "impact", "start_time": start_time, "duration": 1})
        
        elif section_name == "bridge":
            # Transition sweep
            fx_events.append({"type": "sweep", "start_time": start_time, "duration": 2})
        
        elif section_name == "outro":
            # Fade out
            fx_events.append({"type": "fade_out", "start_time": start_time, "duration": bar_count * 4})
        
        return fx_events
    
    def _compile_tracks(self, sections: List[Dict]) -> Dict[str, Any]:
        """Compile all section tracks into full song tracks."""
        compiled = {
            "drums": {},
            "bass": [],
            "melody": [],
            "pads": [],
            "pluck": [],
            "fx": []
        }
        
        for section in sections:
            tracks = section["tracks"]
            
            # Drums (dict of drum_name -> hits)
            if tracks.get("drums"):
                for drum_name, hits in tracks["drums"].items():
                    if drum_name not in compiled["drums"]:
                        compiled["drums"][drum_name] = []
                    compiled["drums"][drum_name].extend(hits)
            
            # Other tracks (lists of notes)
            for track_name in ["bass", "melody", "pads", "pluck", "fx"]:
                if tracks.get(track_name):
                    compiled[track_name].extend(tracks[track_name])
        
        return compiled


def format_duration(seconds: float) -> str:
    """Format seconds as MM:SS."""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}:{secs:02d}"


# Example usage
if __name__ == "__main__":
    generator = SongStructureGenerator()
    
    # Generate a standard trap beat
    beat = generator.generate_full_beat(
        genre="trap",
        bpm=140,
        key="C",
        scale="minor",
        mood="dark",
        structure="standard"
    )
    
    print(f"\nGenerated {beat['genre']} beat")
    print(f"Duration: {format_duration(beat['total_duration_seconds'])}")
    print(f"BPM: {beat['bpm']}")
    print(f"Key: {beat['key']} {beat['scale']}")
    print(f"Bars: {beat['total_bars']}")
    print(f"\nStructure:")
    
    for section_name in beat["section_order"]:
        section = beat["sections"][section_name]
        start = section["start_time"]
        end = start + section["bar_count"] * 4
        print(f"  {section_name:12s} | {format_duration(start * 60 / beat['bpm'])} - {format_duration(end * 60 / beat['bpm'])} | intensity: {section['intensity']:.1f}")
