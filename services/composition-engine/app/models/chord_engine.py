"""Chord progression and harmony engine."""

import numpy as np
from typing import List, Dict, Any, Tuple
import structlog

logger = structlog.get_logger()


class ChordEngine:
    """Generate chord progressions and harmonic content."""
    
    # Extended chord progressions by genre and mood
    PROGRESSIONS = {
        "trap": {
            "dark": [
                ["Cm", "Gm", "Ab", "Eb"],
                ["Cm", "Ab", "Eb", "Bb"],
                ["Dm", "Am", "Bb", "F"],
                ["Fm", "Cm", "Db", "Ab"],
            ],
            "melodic": [
                ["Cm", "Eb", "Bb", "F"],
                ["Am", "F", "C", "G"],
                ["Dm", "Bb", "F", "C"],
            ],
            "aggressive": [
                ["Cm", "Fm", "Gm", "Cm"],
                ["Dm", "Gm", "Am", "Dm"],
            ]
        },
        "drill": {
            "dark": [
                ["Cm", "Fm", "Gm", "Cm"],
                ["Dm", "Gm", "Am", "Dm"],
                ["Fm", "Bbm", "Cm", "Fm"],
            ],
            "melodic": [
                ["Cm", "Ab", "Eb", "Bb"],
                ["Am", "F", "Dm", "E"],
            ]
        },
        "lofi": {
            "chill": [
                ["Am", "F", "C", "G"],
                ["Dm", "G", "C", "Am"],
                ["Em", "C", "G", "D"],
                ["Am", "Em", "F", "C"],
            ],
            "sad": [
                ["Am", "Dm", "Em", "Am"],
                ["Cm", "Fm", "Gm", "Cm"],
            ],
            "dreamy": [
                ["C", "G/B", "Am", "G"],
                ["F", "C/E", "Dm", "G"],
            ]
        },
        "afrobeats": {
            "upbeat": [
                ["C", "G", "Am", "F"],
                ["F", "C", "Dm", "Bb"],
                ["G", "D", "Em", "C"],
            ],
            "vibey": [
                ["Am", "F", "Dm", "E"],
                ["Cm", "Ab", "Fm", "G"],
            ]
        },
        "rage": {
            "hyper": [
                ["Cm", "Eb", "Fm", "Ab"],
                ["Dm", "F", "Gm", "Bb"],
            ],
            "dark": [
                ["Cm", "Fm", "Ab", "Eb"],
                ["Dm", "Gm", "Bb", "F"],
            ]
        }
    }
    
    # Chord voicings for different instruments
    VOICINGS = {
        "piano": {
            "triad": [0, 4, 7],
            "triad_inv1": [4, 7, 12],
            "triad_inv2": [7, 12, 16],
            "seventh": [0, 4, 7, 10],
            "add9": [0, 4, 7, 14],
        },
        "pad": {
            "wide": [0, 7, 12, 16],
            "cluster": [0, 4, 7, 10, 14],
        },
        "pluck": {
            "simple": [0, 7],
            "triad": [0, 4, 7],
        }
    }
    
    def __init__(self):
        pass
    
    def generate_progression(
        self,
        genre: str = "trap",
        mood: str = "dark",
        key: str = "C",
        length: int = 4,
        variation: int = 0
    ) -> List[Dict[str, Any]]:
        """Generate a chord progression."""
        genre_progressions = self.PROGRESSIONS.get(genre, self.PROGRESSIONS["trap"])
        mood_progressions = genre_progressions.get(mood, list(genre_progressions.values())[0])
        
        # Select progression
        prog_idx = variation % len(mood_progressions)
        progression = mood_progressions[prog_idx][:length]
        
        # Convert to structured format
        result = []
        for chord_name in progression:
            chord_data = self._parse_chord(chord_name)
            result.append({
                "name": chord_name,
                "root": chord_data["root"],
                "quality": chord_data["quality"],
                "notes": chord_data["notes"],
                "duration_beats": 4  # One bar per chord
            })
        
        logger.info(
            "progression_generated",
            genre=genre,
            mood=mood,
            key=key,
            chords=[c["name"] for c in result]
        )
        
        return result
    
    def _parse_chord(self, chord_name: str) -> Dict[str, Any]:
        """Parse chord name into components."""
        from shared.utils.midi import parse_chord, chord_to_notes
        
        root, quality = parse_chord(chord_name)
        notes = chord_to_notes(chord_name, octave=4)
        
        return {
            "root": root,
            "quality": quality,
            "notes": notes
        }
    
    def generate_arpeggio(
        self,
        chord: Dict[str, Any],
        pattern: str = "up",
        octaves: int = 1,
        note_duration: float = 0.5
    ) -> List[Dict[str, Any]]:
        """Generate an arpeggio pattern from a chord."""
        base_notes = chord["notes"]
        notes = []
        
        if pattern == "up":
            seq = base_notes
        elif pattern == "down":
            seq = base_notes[::-1]
        elif pattern == "up_down":
            seq = base_notes + base_notes[-2::-1]
        elif pattern == "random":
            seq = [base_notes[i] for i in np.random.permutation(len(base_notes))]
        else:
            seq = base_notes
        
        current_time = 0
        for octave in range(octaves):
            for note in seq:
                notes.append({
                    "pitch": note + (octave * 12),
                    "velocity": np.random.randint(70, 100),
                    "start_time": current_time,
                    "duration": note_duration
                })
                current_time += note_duration
        
        return notes
    
    def generate_bass_notes(
        self,
        progression: List[Dict[str, Any]],
        style: str = "root_fifth"
    ) -> List[Dict[str, Any]]:
        """Generate bass line from chord progression."""
        notes = []
        current_time = 0
        
        for chord in progression:
            root = chord["notes"][0] - 12  # Bass octave
            
            if style == "root":
                notes.append({
                    "pitch": root,
                    "velocity": 100,
                    "start_time": current_time,
                    "duration": chord["duration_beats"]
                })
            elif style == "root_fifth":
                fifth = root + 7
                notes.append({
                    "pitch": root,
                    "velocity": 100,
                    "start_time": current_time,
                    "duration": chord["duration_beats"] / 2
                })
                notes.append({
                    "pitch": fifth,
                    "velocity": 90,
                    "start_time": current_time + chord["duration_beats"] / 2,
                    "duration": chord["duration_beats"] / 2
                })
            elif style == "walking":
                for i in range(4):
                    interval = [0, 3, 5, 7][i]
                    notes.append({
                        "pitch": root + interval,
                        "velocity": 85,
                        "start_time": current_time + i,
                        "duration": 0.75
                    })
            
            current_time += chord["duration_beats"]
        
        return notes
    
    def generate_pad_chords(
        self,
        progression: List[Dict[str, Any]],
        voicing: str = "wide"
    ) -> List[Dict[str, Any]]:
        """Generate pad-style chord voicings."""
        notes = []
        current_time = 0
        
        voicing_intervals = self.VOICINGS["pad"].get(voicing, [0, 7, 12, 16])
        
        for chord in progression:
            root = chord["notes"][0]
            
            # Build voicing
            chord_notes = [root + interval for interval in voicing_intervals]
            
            notes.append({
                "pitches": chord_notes,
                "velocity": np.random.randint(50, 70),
                "start_time": current_time,
                "duration": chord["duration_beats"]
            })
            
            current_time += chord["duration_beats"]
        
        return notes
    
    def suggest_key(self, genre: str = "trap", mood: str = "dark") -> str:
        """Suggest a key based on genre and mood."""
        keys = {
            "trap": {
                "dark": ["C", "D", "F", "G"],
                "melodic": ["A", "C", "D", "E"],
                "aggressive": ["C", "D", "F"]
            },
            "drill": {
                "dark": ["C", "D", "F"],
                "melodic": ["A", "C", "E"]
            },
            "lofi": {
                "chill": ["A", "C", "D", "E", "G"],
                "sad": ["A", "C", "D", "E"],
                "dreamy": ["C", "F", "G"]
            }
        }
        
        genre_keys = keys.get(genre, keys["trap"])
        mood_keys = genre_keys.get(mood, list(genre_keys.values())[0])
        
        return np.random.choice(mood_keys)
    
    def transpose_progression(
        self,
        progression: List[Dict[str, Any]],
        semitones: int
    ) -> List[Dict[str, Any]]:
        """Transpose a chord progression."""
        transposed = []
        
        for chord in progression:
            new_chord = chord.copy()
            new_chord["notes"] = [n + semitones for n in chord["notes"]]
            transposed.append(new_chord)
        
        return transposed
