"""AI-powered drum pattern generator."""

import numpy as np
from typing import Dict, List, Tuple, Any
import structlog

logger = structlog.get_logger()


class DrumPatternGenerator:
    """Generate genre-specific drum patterns with variation."""
    
    # Standard GM drum mapping
    DRUM_NOTES = {
        "kick": 36,
        "snare": 38,
        "hihat_closed": 42,
        "hihat_open": 46,
        "clap": 39,
        "rim": 37,
        "tom_low": 45,
        "tom_mid": 47,
        "tom_high": 50,
        "crash": 49,
        "ride": 51,
        "shaker": 82,
        "perc": 87,
        "808": 35,
    }
    
    # Genre-specific pattern templates
    PATTERNS = {
        "trap": {
            "kick": [
                (0, 100), (1.5, 90), (2.5, 95), (3.25, 85)
            ],
            "snare": [
                (1, 110), (3, 110)
            ],
            "hihat_closed": [
                (0, 70), (0.5, 65), (1, 70), (1.5, 75),
                (2, 70), (2.5, 80), (3, 70), (3.5, 65)
            ],
            "clap": [
                (1, 100), (3, 100)
            ],
            "808": [
                (0, 110), (1.5, 100), (2.5, 105)
            ]
        },
        "drill": {
            "kick": [
                (0, 100), (1.75, 90), (2.5, 95)
            ],
            "snare": [
                (1, 110), (3, 110)
            ],
            "hihat_closed": [
                (0, 70), (0.5, 65), (1, 70), (1.5, 75),
                (2, 70), (2.5, 80), (3, 70), (3.5, 65)
            ],
            "clap": [
                (1, 100), (3, 100)
            ],
            "808": [
                (0, 110), (1.75, 100), (2.5, 105), (3.25, 95)
            ]
        },
        "lofi": {
            "kick": [
                (0, 75), (2.5, 70)
            ],
            "snare": [
                (1, 80), (3, 80)
            ],
            "hihat_closed": [
                (0, 50), (1, 55), (2, 50), (3, 55)
            ],
            "rim": [
                (0.5, 45), (2.5, 45)
            ],
            "shaker": [
                (0, 40), (0.5, 35), (1, 40), (1.5, 35),
                (2, 40), (2.5, 35), (3, 40), (3.5, 35)
            ]
        },
        "afrobeats": {
            "kick": [
                (0, 100), (1.5, 90), (2.75, 85)
            ],
            "snare": [
                (1, 95), (3, 95)
            ],
            "hihat_closed": [
                (0, 60), (1, 60), (2, 60), (3, 60)
            ],
            "shaker": [
                (0, 55), (0.25, 50), (0.5, 55), (0.75, 50),
                (1, 55), (1.25, 50), (1.5, 55), (1.75, 50),
                (2, 55), (2.25, 50), (2.5, 55), (2.75, 50),
                (3, 55), (3.25, 50), (3.5, 55), (3.75, 50)
            ],
            "perc": [
                (0.5, 70), (1.5, 70), (2.5, 70), (3.5, 70)
            ]
        }
    }
    
    def __init__(self, genre: str = "trap"):
        self.genre = genre
        self.pattern = self.PATTERNS.get(genre, self.PATTERNS["trap"])
    
    def generate(self, bars: int = 4, variation_seed: int = None) -> Dict[str, List[Tuple[float, int]]]:
        """Generate a drum pattern with variation."""
        if variation_seed is not None:
            np.random.seed(variation_seed)
        
        result = {}
        
        for drum_name, template in self.pattern.items():
            hits = []
            
            for bar in range(bars):
                bar_offset = bar * 4
                
                for beat_pos, velocity in template:
                    # Add humanization
                    time_jitter = np.random.normal(0, 0.02)  # Small timing variation
                    vel_jitter = np.random.randint(-8, 8)
                    
                    hits.append((
                        bar_offset + beat_pos + time_jitter,
                        max(1, min(127, velocity + vel_jitter))
                    ))
                
                # Add occasional extra hits for variation
                if np.random.random() < 0.1:
                    extra_pos = bar_offset + np.random.choice([0.25, 0.75, 1.25, 2.25, 3.25])
                    extra_vel = np.random.randint(60, 90)
                    hits.append((extra_pos, extra_vel))
            
            result[drum_name] = hits
        
        return result
    
    def generate_fill(self, bar: int = 0, intensity: str = "medium") -> Dict[str, List[Tuple[float, int]]]:
        """Generate a drum fill."""
        fills = {
            "light": {
                "snare": [(0, 80), (0.5, 70), (1, 85)],
                "hihat_open": [(0, 70)]
            },
            "medium": {
                "snare": [(0, 90), (0.5, 80), (1, 95), (1.5, 85), (2, 100)],
                "tom_high": [(2.5, 85)],
                "tom_mid": [(3, 80)],
                "crash": [(3.5, 90)]
            },
            "heavy": {
                "snare": [(0, 100), (0.33, 90), (0.66, 95), (1, 110), (1.33, 100), (1.66, 105)],
                "tom_high": [(2, 90), (2.5, 85)],
                "tom_mid": [(2.66, 85), (3, 90)],
                "tom_low": [(3.33, 85), (3.66, 90)],
                "crash": [(3.5, 100)]
            }
        }
        
        return fills.get(intensity, fills["medium"])
    
    def generate_808_pattern(
        self,
        chord_progression: List[List[int]],
        bpm: int = 140,
        style: str = "trap"
    ) -> List[Dict[str, Any]]:
        """Generate 808/bass pattern following chord roots."""
        notes = []
        current_time = 0
        
        for chord in chord_progression:
            root = chord[0] - 24  # Very low octave for 808
            
            if style in ["trap", "drill"]:
                # Long sustained 808s with slides
                notes.append({
                    "pitch": root,
                    "velocity": 110,
                    "start_time": current_time,
                    "duration": 1.5,
                    "slide_to": root + np.random.choice([0, 3, 5, 7])
                })
                
                notes.append({
                    "pitch": root,
                    "velocity": 100,
                    "start_time": current_time + 2,
                    "duration": 2,
                    "slide_to": None
                })
            else:
                # Shorter, punchier 808s
                for i in range(4):
                    notes.append({
                        "pitch": root,
                        "velocity": 100,
                        "start_time": current_time + i,
                        "duration": 0.5,
                        "slide_to": None
                    })
            
            current_time += 4.0
        
        return notes
