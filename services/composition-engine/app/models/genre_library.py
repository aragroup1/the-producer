"""Comprehensive genre library for beat generation.

Covers the most popular genres for beat selling in 2024-2025.
Each genre includes chord progressions, drum patterns, and arrangement templates.
"""

from typing import Dict, List, Tuple, Any


# ─── CHORD PROGRESSIONS ──────────────────────────────────────────────

CHORD_PROGRESSIONS = {
    # HIP-HOP
    "trap": {
        "dark": [
            ["Cm", "Gm", "Ab", "Eb"],
            ["Cm", "Ab", "Eb", "Bb"],
            ["Dm", "Am", "Bb", "F"],
            ["Fm", "Cm", "Db", "Ab"],
            ["Gm", "Eb", "Bb", "F"],
        ],
        "melodic": [
            ["Cm", "Eb", "Bb", "F"],
            ["Am", "F", "C", "G"],
            ["Dm", "Bb", "F", "C"],
            ["Em", "C", "G", "D"],
        ],
        "aggressive": [
            ["Cm", "Fm", "Gm", "Cm"],
            ["Dm", "Gm", "Am", "Dm"],
            ["Fm", "Bbm", "Cm", "Fm"],
        ],
        "emotional": [
            ["Am", "F", "C", "G"],
            ["Em", "G", "D", "A"],
            ["Cm", "Ab", "Eb", "Bb"],
        ]
    },
    "drill": {
        "dark": [
            ["Cm", "Fm", "Gm", "Cm"],
            ["Dm", "Gm", "Am", "Dm"],
            ["Fm", "Bbm", "Cm", "Fm"],
            ["Gm", "Cm", "Dm", "Gm"],
        ],
        "melodic": [
            ["Cm", "Ab", "Eb", "Bb"],
            ["Am", "F", "Dm", "E"],
            ["Gm", "Eb", "Bb", "F"],
        ],
        "uk": [
            ["Cm", "Gm", "Ab", "Eb"],
            ["Dm", "Am", "Bb", "F"],
            ["Fm", "Cm", "Db", "Ab"],
        ]
    },
    "boom_bap": {
        "classic": [
            ["Am", "Dm", "G", "C"],
            ["Fm", "Bbm", "Eb", "Ab"],
            ["Cm", "Fm", "Gm", "Cm"],
            ["Dm", "Gm", "C", "F"],
        ],
        "jazz": [
            ["Dm7", "G7", "Cm7", "F7"],
            ["Am7", "D7", "Gm7", "C7"],
            ["Fm7", "Bb7", "Ebmaj7", "Abmaj7"],
        ],
        "soulful": [
            ["Am", "F", "Dm", "E"],
            ["Cm", "Ab", "Fm", "G"],
            ["Gm", "Eb", "Cm", "D"],
        ]
    },
    "rage": {
        "hyper": [
            ["Cm", "Eb", "Fm", "Ab"],
            ["Dm", "F", "Gm", "Bb"],
            ["Em", "G", "Am", "C"],
        ],
        "dark": [
            ["Cm", "Fm", "Ab", "Eb"],
            ["Dm", "Gm", "Bb", "F"],
            ["Fm", "Bbm", "Db", "Ab"],
        ],
        "melodic": [
            ["Am", "F", "C", "G"],
            ["Em", "C", "G", "D"],
            ["Dm", "Bb", "F", "C"],
        ]
    },
    "phonk": {
        "memphis": [
            ["Cm", "Fm", "Gm", "Cm"],
            ["Am", "Dm", "Em", "Am"],
            ["Fm", "Bbm", "Cm", "Fm"],
        ],
        "drift": [
            ["Cm", "Ab", "Eb", "Bb"],
            ["Dm", "Bb", "F", "C"],
            ["Fm", "Db", "Ab", "Eb"],
        ],
        "dark": [
            ["Cm", "Fm", "Ab", "Eb"],
            ["Dm", "Gm", "Bb", "F"],
            ["Gm", "Cm", "Eb", "Bb"],
        ]
    },
    "jersey_club": {
        "bounce": [
            ["Cm", "Eb", "Bb", "F"],
            ["Dm", "F", "C", "G"],
            ["Fm", "Ab", "Eb", "Bb"],
        ],
        "vibe": [
            ["Am", "F", "C", "G"],
            ["Em", "C", "G", "D"],
            ["Gm", "Eb", "Bb", "F"],
        ]
    },
    "plugg": {
        "smooth": [
            ["Cm", "Ab", "Eb", "Bb"],
            ["Dm", "Bb", "F", "C"],
            ["Fm", "Db", "Ab", "Eb"],
        ],
        "wavy": [
            ["Am", "F", "C", "G"],
            ["Em", "C", "G", "D"],
            ["Gm", "Eb", "Bb", "F"],
        ]
    },
    "west_coast": {
        "g_funk": [
            ["Dm", "Gm", "C", "F"],
            ["Am", "Dm", "G", "C"],
            ["Fm", "Bbm", "Eb", "Ab"],
        ],
        "modern": [
            ["Cm", "Fm", "Gm", "Cm"],
            ["Dm", "Gm", "Am", "Dm"],
            ["Gm", "Cm", "Dm", "Gm"],
        ]
    },
    
    # R&B / SOUL
    "rnb": {
        "smooth": [
            ["Am7", "Dm7", "G7", "Cmaj7"],
            ["Fm7", "Bbm7", "Eb7", "Abmaj7"],
            ["Cm7", "Fm7", "Bb7", "Ebmaj7"],
        ],
        "trap_soul": [
            ["Cm", "Ab", "Eb", "Bb"],
            ["Am", "F", "C", "G"],
            ["Dm", "Bb", "F", "C"],
        ],
        "alternative": [
            ["Em", "C", "G", "D"],
            ["Am", "F", "Dm", "E"],
            ["Cm", "Ab", "Fm", "G"],
        ]
    },
    "neo_soul": {
        "jazzy": [
            ["Dm7", "G7", "Cm7", "F7"],
            ["Am7", "D7", "Gm7", "C7"],
            ["Fm7", "Bb7", "Ebmaj7", "Abmaj7"],
        ],
        "groovy": [
            ["Am7", "Fmaj7", "Cmaj7", "G7"],
            ["Cm7", "Abmaj7", "Ebmaj7", "Bb7"],
            ["Em7", "Cmaj7", "Gmaj7", "D7"],
        ]
    },
    
    # AFROBEATS / GLOBAL
    "afrobeats": {
        "upbeat": [
            ["C", "G", "Am", "F"],
            ["F", "C", "Dm", "Bb"],
            ["G", "D", "Em", "C"],
        ],
        "vibey": [
            ["Am", "F", "Dm", "E"],
            ["Cm", "Ab", "Fm", "G"],
            ["Dm", "Bb", "Gm", "A"],
        ],
        "romantic": [
            ["C", "Am", "F", "G"],
            ["G", "Em", "C", "D"],
            ["F", "Dm", "Bb", "C"],
        ]
    },
    "amapiano": {
        "log_drum": [
            ["Cm", "Fm", "Gm", "Cm"],
            ["Am", "Dm", "Em", "Am"],
            ["Fm", "Bbm", "Cm", "Fm"],
        ],
        "melodic": [
            ["Cm", "Ab", "Eb", "Bb"],
            ["Dm", "Bb", "F", "C"],
            ["Gm", "Eb", "Bb", "F"],
        ],
        "deep": [
            ["Cm", "Fm", "Ab", "Eb"],
            ["Am", "Dm", "F", "C"],
            ["Fm", "Bbm", "Db", "Ab"],
        ]
    },
    "dancehall": {
        "riddim": [
            ["Cm", "Fm", "Gm", "Cm"],
            ["Am", "Dm", "Em", "Am"],
            ["Dm", "Gm", "Am", "Dm"],
        ],
        "melodic": [
            ["C", "G", "Am", "F"],
            ["F", "C", "Dm", "Bb"],
            ["G", "D", "Em", "C"],
        ]
    },
    "reggaeton": {
        "dembow": [
            ["Cm", "Fm", "Gm", "Cm"],
            ["Am", "Dm", "Em", "Am"],
            ["Dm", "Gm", "Am", "Dm"],
        ],
        "moombahton": [
            ["Cm", "Ab", "Eb", "Bb"],
            ["Am", "F", "C", "G"],
            ["Dm", "Bb", "F", "C"],
        ],
        "latin_trap": [
            ["Cm", "Fm", "Ab", "Eb"],
            ["Dm", "Gm", "Bb", "F"],
            ["Gm", "Cm", "Eb", "Bb"],
        ]
    },
    
    # ELECTRONIC / POP
    "hyperpop": {
        "glitch": [
            ["Cm", "Eb", "Bb", "F"],
            ["Am", "C", "G", "D"],
            ["Dm", "F", "C", "G"],
        ],
        "emotional": [
            ["Am", "F", "C", "G"],
            ["Em", "C", "G", "D"],
            ["Cm", "Ab", "Eb", "Bb"],
        ],
        "bouncy": [
            ["Cm", "Fm", "Gm", "Cm"],
            ["Dm", "Gm", "Am", "Dm"],
            ["Fm", "Bbm", "Cm", "Fm"],
        ]
    },
    "edm_trap": {
        "festival": [
            ["Cm", "Eb", "Bb", "F"],
            ["Dm", "F", "C", "G"],
            ["Am", "C", "G", "D"],
        ],
        "dark": [
            ["Cm", "Fm", "Ab", "Eb"],
            ["Dm", "Gm", "Bb", "F"],
            ["Fm", "Bbm", "Db", "Ab"],
        ]
    },
    "future_bass": {
        "melodic": [
            ["Cm", "Ab", "Eb", "Bb"],
            ["Am", "F", "C", "G"],
            ["Dm", "Bb", "F", "C"],
        ],
        "chords": [
            ["Cmaj7", "Gmaj7", "Am7", "Fmaj7"],
            ["Fmaj7", "Cmaj7", "Dm7", "Bbmaj7"],
            ["Gmaj7", "Dmaj7", "Em7", "Cmaj7"],
        ]
    },
    
    # LO-FI / AMBIENT
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
            ["Dm", "Gm", "Am", "Dm"],
        ],
        "dreamy": [
            ["C", "G/B", "Am", "G"],
            ["F", "C/E", "Dm", "G"],
            ["C", "Am", "F", "G"],
        ],
        "jazzhop": [
            ["Dm7", "G7", "Cm7", "F7"],
            ["Am7", "D7", "Gm7", "C7"],
            ["Fm7", "Bb7", "Ebmaj7", "Abmaj7"],
        ]
    },
    "ambient": {
        "ethereal": [
            ["C", "Am", "F", "G"],
            ["F", "Dm", "Bb", "C"],
            ["Am", "F", "C", "G"],
        ],
        "cinematic": [
            ["Cm", "Ab", "Eb", "Bb"],
            ["Fm", "Db", "Ab", "Eb"],
            ["Gm", "Eb", "Bb", "F"],
        ]
    }
}


# ─── DRUM PATTERNS ───────────────────────────────────────────────────

DRUM_PATTERNS = {
    "trap": {
        "kick": [(0, 100), (1.5, 90), (2.5, 95), (3.25, 85)],
        "snare": [(1, 110), (3, 110)],
        "hihat_closed": [(0, 70), (0.5, 65), (1, 70), (1.5, 75), (2, 70), (2.5, 80), (3, 70), (3.5, 65)],
        "clap": [(1, 100), (3, 100)],
        "808": [(0, 110), (1.5, 100), (2.5, 105)]
    },
    "drill": {
        "kick": [(0, 100), (1.75, 90), (2.5, 95)],
        "snare": [(1, 110), (3, 110)],
        "hihat_closed": [(0, 70), (0.5, 65), (1, 70), (1.5, 75), (2, 70), (2.5, 80), (3, 70), (3.5, 65)],
        "clap": [(1, 100), (3, 100)],
        "808": [(0, 110), (1.75, 100), (2.5, 105), (3.25, 95)]
    },
    "boom_bap": {
        "kick": [(0, 100), (2, 90), (2.75, 85)],
        "snare": [(1, 100), (3, 100)],
        "hihat_closed": [(0, 60), (0.5, 55), (1, 60), (1.5, 55), (2, 60), (2.5, 55), (3, 60), (3.5, 55)],
        "open_hihat": [(1.75, 70)],
        "kick_double": [(0, 100), (0.5, 85), (2, 90), (2.5, 85)]
    },
    "rage": {
        "kick": [(0, 110), (0.75, 100), (1.5, 105), (2.5, 100)],
        "snare": [(1, 115), (3, 115)],
        "hihat_closed": [(0, 75), (0.25, 70), (0.5, 75), (0.75, 70), (1, 75), (1.25, 80), (1.5, 75), (1.75, 70), (2, 75), (2.25, 70), (2.5, 75), (2.75, 80), (3, 75), (3.25, 70), (3.5, 75), (3.75, 70)],
        "crash": [(0, 90)],
        "808": [(0, 115), (1.5, 105), (2.5, 110)]
    },
    "phonk": {
        "kick": [(0, 100), (1.5, 90), (2.5, 95)],
        "snare": [(1, 100), (3, 100)],
        "hihat_closed": [(0, 60), (0.5, 55), (1, 60), (1.5, 55), (2, 60), (2.5, 55), (3, 60), (3.5, 55)],
        "cowbell": [(0.75, 80), (1.75, 80), (2.75, 80)],
        "808": [(0, 110), (1.5, 100), (2.5, 105)]
    },
    "jersey_club": {
        "kick": [(0, 100), (0.75, 90), (1.5, 95), (2.25, 90), (3, 95)],
        "snare": [(0.5, 100), (1.25, 100), (2, 100), (2.75, 100)],
        "hihat_closed": [(0, 70), (0.5, 65), (1, 70), (1.5, 65), (2, 70), (2.5, 65), (3, 70), (3.5, 65)],
        "clap": [(0.5, 100), (1.25, 100), (2, 100), (2.75, 100)],
        "808": [(0, 110), (1.5, 100), (2.5, 105)]
    },
    "plugg": {
        "kick": [(0, 95), (2, 90)],
        "snare": [(1, 100), (3, 100)],
        "hihat_closed": [(0, 60), (0.5, 55), (1, 60), (1.5, 55), (2, 60), (2.5, 55), (3, 60), (3.5, 55)],
        "open_hihat": [(1.75, 65), (3.75, 65)],
        "808": [(0, 105), (1.5, 100), (2.5, 105)]
    },
    "west_coast": {
        "kick": [(0, 100), (1.5, 90), (2.5, 95)],
        "snare": [(1, 105), (3, 105)],
        "hihat_closed": [(0, 65), (0.5, 60), (1, 65), (1.5, 60), (2, 65), (2.5, 60), (3, 65), (3.5, 60)],
        "clap": [(1, 100), (3, 100)],
        "808": [(0, 110), (1.5, 100), (2.5, 105)]
    },
    "rnb": {
        "kick": [(0, 85), (2, 80)],
        "snare": [(1, 90), (3, 90)],
        "hihat_closed": [(0, 50), (0.5, 45), (1, 50), (1.5, 45), (2, 50), (2.5, 45), (3, 50), (3.5, 45)],
        "rim": [(0.75, 60), (1.75, 60), (2.75, 60)],
        "kick_soft": [(0, 70), (2.5, 65)]
    },
    "neo_soul": {
        "kick": [(0, 80), (2, 75)],
        "snare": [(1, 85), (3, 85)],
        "hihat_closed": [(0, 45), (0.5, 40), (1, 45), (1.5, 40), (2, 45), (2.5, 40), (3, 45), (3.5, 40)],
        "ride": [(0, 55), (0.5, 50), (1, 55), (1.5, 50), (2, 55), (2.5, 50), (3, 55), (3.5, 50)],
        "kick_brush": [(0, 60), (2.5, 55)]
    },
    "afrobeats": {
        "kick": [(0, 100), (1.5, 90), (2.75, 85)],
        "snare": [(1, 95), (3, 95)],
        "hihat_closed": [(0, 60), (1, 60), (2, 60), (3, 60)],
        "shaker": [(0, 55), (0.25, 50), (0.5, 55), (0.75, 50), (1, 55), (1.25, 50), (1.5, 55), (1.75, 50), (2, 55), (2.25, 50), (2.5, 55), (2.75, 50), (3, 55), (3.25, 50), (3.5, 55), (3.75, 50)],
        "perc": [(0.5, 70), (1.5, 70), (2.5, 70), (3.5, 70)]
    },
    "amapiano": {
        "kick": [(0, 100), (1.5, 90), (2.5, 95)],
        "snare": [(1, 90), (3, 90)],
        "hihat_closed": [(0, 55), (0.5, 50), (1, 55), (1.5, 50), (2, 55), (2.5, 50), (3, 55), (3.5, 50)],
        "shaker": [(0, 50), (0.25, 45), (0.5, 50), (0.75, 45), (1, 50), (1.25, 45), (1.5, 50), (1.75, 45), (2, 50), (2.25, 45), (2.5, 50), (2.75, 45), (3, 50), (3.25, 45), (3.5, 50), (3.75, 45)],
        "log_drum": [(0, 110), (0.75, 100), (1.5, 105), (2.25, 100), (3, 105)]
    },
    "dancehall": {
        "kick": [(0, 100), (1.5, 90), (2.5, 95)],
        "snare": [(1, 100), (3, 100)],
        "hihat_closed": [(0, 60), (0.5, 55), (1, 60), (1.5, 55), (2, 60), (2.5, 55), (3, 60), (3.5, 55)],
        "kick_dembow": [(0, 100), (0.5, 85), (1.5, 90), (2.5, 95), (3, 85)],
        "perc": [(0.75, 70), (1.75, 70), (2.75, 70)]
    },
    "reggaeton": {
        "kick": [(0, 100), (1.5, 90), (2.5, 95)],
        "snare": [(1, 100), (3, 100)],
        "hihat_closed": [(0, 60), (0.5, 55), (1, 60), (1.5, 55), (2, 60), (2.5, 55), (3, 60), (3.5, 55)],
        "kick_dembow": [(0, 100), (0.5, 85), (1.5, 90), (2.5, 95), (3, 85)],
        "rim": [(0.75, 65), (1.75, 65), (2.75, 65)]
    },
    "hyperpop": {
        "kick": [(0, 110), (0.75, 100), (1.5, 105), (2.25, 100), (3, 105)],
        "snare": [(1, 115), (3, 115)],
        "hihat_closed": [(0, 75), (0.25, 70), (0.5, 75), (0.75, 70), (1, 75), (1.25, 80), (1.5, 75), (1.75, 70), (2, 75), (2.25, 70), (2.5, 75), (2.75, 80), (3, 75), (3.25, 70), (3.5, 75), (3.75, 70)],
        "crash": [(0, 90), (2, 85)],
        "808": [(0, 115), (1.5, 105), (2.5, 110)]
    },
    "edm_trap": {
        "kick": [(0, 110), (1.5, 100), (2.5, 105)],
        "snare": [(1, 115), (3, 115)],
        "hihat_closed": [(0, 70), (0.25, 65), (0.5, 70), (0.75, 65), (1, 70), (1.25, 75), (1.5, 70), (1.75, 65), (2, 70), (2.25, 65), (2.5, 70), (2.75, 75), (3, 70), (3.25, 65), (3.5, 70), (3.75, 65)],
        "crash": [(0, 95)],
        "808": [(0, 115), (1.5, 105), (2.5, 110)]
    },
    "future_bass": {
        "kick": [(0, 100), (2, 95)],
        "snare": [(1, 105), (3, 105)],
        "hihat_closed": [(0, 60), (0.5, 55), (1, 60), (1.5, 55), (2, 60), (2.5, 55), (3, 60), (3.5, 55)],
        "kick_build": [(0, 100), (0.5, 85), (1, 90), (1.5, 85), (2, 95), (2.5, 90), (3, 95)],
        "snare_roll": [(3, 100), (3.25, 90), (3.5, 95), (3.75, 85)]
    },
    "lofi": {
        "kick": [(0, 75), (2.5, 70)],
        "snare": [(1, 80), (3, 80)],
        "hihat_closed": [(0, 50), (1, 55), (2, 50), (3, 55)],
        "rim": [(0.5, 45), (2.5, 45)],
        "shaker": [(0, 40), (0.5, 35), (1, 40), (1.5, 35), (2, 40), (2.5, 35), (3, 40), (3.5, 35)]
    },
    "ambient": {
        "kick": [(0, 60), (4, 55)],
        "snare": [(2, 65), (6, 65)],
        "hihat_closed": [(0, 40), (1, 35), (2, 40), (3, 35)],
        "ride": [(0, 45), (0.5, 40), (1, 45), (1.5, 40)],
        "kick_sparse": [(0, 50), (8, 45)]
    }
}


# ─── GENRE CONFIGURATION ─────────────────────────────────────────────

GENRE_CONFIG = {
    "trap": {
        "bpms": [130, 140, 150, 160],
        "moods": ["dark", "melodic", "aggressive", "emotional"],
        "keys": ["C", "D", "F", "G", "A"],
        "scales": ["minor", "major"],
        "description": "Hard-hitting 808s, fast hi-hats, dark melodies"
    },
    "drill": {
        "bpms": [140, 150, 160],
        "moods": ["dark", "melodic", "uk"],
        "keys": ["C", "D", "F", "G"],
        "scales": ["minor"],
        "description": "Sliding 808s, sparse drums, ominous pads"
    },
    "boom_bap": {
        "bpms": [85, 90, 95],
        "moods": ["classic", "jazz", "soulful"],
        "keys": ["C", "D", "F", "G", "A", "Bb"],
        "scales": ["minor", "major"],
        "description": "Dusty drums, soul samples, laid-back grooves"
    },
    "rage": {
        "bpms": [140, 150, 160],
        "moods": ["hyper", "dark", "melodic"],
        "keys": ["C", "D", "E", "F", "G"],
        "scales": ["minor", "major"],
        "description": "Distorted 808s, fast tempos, chaotic energy"
    },
    "phonk": {
        "bpms": [130, 140, 150],
        "moods": ["memphis", "drift", "dark"],
        "keys": ["C", "D", "F", "G", "A"],
        "scales": ["minor"],
        "description": "Cowbells, distorted samples, Memphis influence"
    },
    "jersey_club": {
        "bpms": [135, 140, 145],
        "moods": ["bounce", "vibe"],
        "keys": ["C", "D", "F", "G"],
        "scales": ["minor", "major"],
        "description": "Four-on-floor bounce, bed squeaks, club energy"
    },
    "plugg": {
        "bpms": [130, 140, 150],
        "moods": ["smooth", "wavy"],
        "keys": ["C", "D", "F", "G", "A"],
        "scales": ["minor", "major"],
        "description": "Smooth synths, minimal drums, spacey vibes"
    },
    "west_coast": {
        "bpms": [90, 95, 100],
        "moods": ["g_funk", "modern"],
        "keys": ["C", "D", "F", "G", "A"],
        "scales": ["minor", "major"],
        "description": "Funky bass, G-funk whistles, laid-back bounce"
    },
    "rnb": {
        "bpms": [65, 70, 75, 80],
        "moods": ["smooth", "trap_soul", "alternative"],
        "keys": ["C", "D", "E", "F", "G", "A", "Bb"],
        "scales": ["minor", "major"],
        "description": "Smooth chords, sensual grooves, vocal-focused"
    },
    "neo_soul": {
        "bpms": [70, 75, 80, 85],
        "moods": ["jazzy", "groovy"],
        "keys": ["C", "D", "F", "G", "A", "Bb"],
        "scales": ["minor", "major"],
        "description": "Jazz chords, live drums, organic feel"
    },
    "afrobeats": {
        "bpms": [100, 110, 120],
        "moods": ["upbeat", "vibey", "romantic"],
        "keys": ["C", "D", "F", "G", "A"],
        "scales": ["major", "minor"],
        "description": "Shakers, percussion, bouncy rhythms"
    },
    "amapiano": {
        "bpms": [110, 115, 120],
        "moods": ["log_drum", "melodic", "deep"],
        "keys": ["C", "D", "F", "G", "A"],
        "scales": ["minor", "major"],
        "description": "Log drums, jazzy chords, South African house"
    },
    "dancehall": {
        "bpms": [95, 100, 105],
        "moods": ["riddim", "melodic"],
        "keys": ["C", "D", "F", "G", "A"],
        "scales": ["minor", "major"],
        "description": "Dembow rhythm, brass stabs, Caribbean energy"
    },
    "reggaeton": {
        "bpms": [90, 95, 100],
        "moods": ["dembow", "moombahton", "latin_trap"],
        "keys": ["C", "D", "F", "G", "A", "Bb"],
        "scales": ["minor", "major"],
        "description": "Dembow kick, reggaeton snare, Latin flavor"
    },
    "hyperpop": {
        "bpms": [140, 150, 160],
        "moods": ["glitch", "emotional", "bouncy"],
        "keys": ["C", "D", "E", "F", "G"],
        "scales": ["major", "minor"],
        "description": "Maximalist, glitchy, pop-meets-experimental"
    },
    "edm_trap": {
        "bpms": [140, 150, 160],
        "moods": ["festival", "dark"],
        "keys": ["C", "D", "F", "G", "A"],
        "scales": ["minor", "major"],
        "description": "Festival drops, huge synths, trap drums"
    },
    "future_bass": {
        "bpms": [140, 150, 160],
        "moods": ["melodic", "chords"],
        "keys": ["C", "D", "F", "G", "A"],
        "scales": ["major", "minor"],
        "description": "Supersaw chords, pitched vocals, emotional drops"
    },
    "lofi": {
        "bpms": [70, 75, 80, 85],
        "moods": ["chill", "sad", "dreamy", "jazzhop"],
        "keys": ["C", "D", "F", "G", "A"],
        "scales": ["minor", "major"],
        "description": "Dusty textures, jazz chords, relaxed grooves"
    },
    "ambient": {
        "bpms": [60, 70, 80],
        "moods": ["ethereal", "cinematic"],
        "keys": ["C", "D", "F", "G", "A"],
        "scales": ["major", "minor"],
        "description": "Sparse, atmospheric, texture-focused"
    }
}


# ─── SONG STRUCTURE TEMPLATES ────────────────────────────────────────

# Bar counts for each section type
SECTION_TEMPLATES = {
    "short": {
        "intro": 4,
        "verse": 8,
        "hook": 8,
        "verse2": 8,
        "hook2": 8,
        "bridge": 4,
        "outro": 4
    },
    "standard": {
        "intro": 8,
        "verse": 16,
        "hook": 8,
        "verse2": 16,
        "hook2": 8,
        "bridge": 8,
        "outro": 8
    },
    "extended": {
        "intro": 8,
        "verse": 16,
        "pre_hook": 4,
        "hook": 8,
        "verse2": 16,
        "pre_hook2": 4,
        "hook2": 8,
        "bridge": 8,
        "hook3": 8,
        "outro": 8
    }
}

# Arrangement intensity per section (0.0 = minimal, 1.0 = full)
ARRANGEMENT_INTENSITY = {
    "intro": 0.3,
    "verse": 0.6,
    "pre_hook": 0.7,
    "hook": 1.0,
    "verse2": 0.6,
    "pre_hook2": 0.7,
    "hook2": 1.0,
    "bridge": 0.5,
    "hook3": 1.0,
    "outro": 0.2
}

# Which instruments play in each section
SECTION_INSTRUMENTS = {
    "intro": ["pads", "fx"],
    "verse": ["drums", "bass", "pads", "pluck"],
    "pre_hook": ["drums", "bass", "pads", "lead", "pluck"],
    "hook": ["drums", "bass", "pads", "lead", "pluck", "fx"],
    "verse2": ["drums", "bass", "pads", "pluck"],
    "pre_hook2": ["drums", "bass", "pads", "lead", "pluck"],
    "hook2": ["drums", "bass", "pads", "lead", "pluck", "fx"],
    "bridge": ["pads", "lead", "fx"],
    "hook3": ["drums", "bass", "pads", "lead", "pluck", "fx"],
    "outro": ["pads", "fx"]
}


def get_all_genres() -> List[str]:
    """Return all supported genres."""
    return list(GENRE_CONFIG.keys())


def get_genre_config(genre: str) -> Dict[str, Any]:
    """Get configuration for a genre."""
    return GENRE_CONFIG.get(genre, GENRE_CONFIG["trap"])


def get_random_genre_params(genre: str = None) -> Dict[str, Any]:
    """Generate random but valid parameters for a genre."""
    import random
    
    if genre is None:
        genre = random.choice(get_all_genres())
    
    config = get_genre_config(genre)
    
    return {
        "genre": genre,
        "bpm": random.choice(config["bpms"]),
        "mood": random.choice(config["moods"]),
        "key": random.choice(config["keys"]),
        "scale": random.choice(config["scales"])
    }


def calculate_beat_duration(structure: str, bpm: int) -> float:
    """Calculate total duration in seconds for a song structure."""
    template = SECTION_TEMPLATES.get(structure, SECTION_TEMPLATES["standard"])
    total_bars = sum(template.values())
    seconds_per_bar = 4 * 60 / bpm
    return total_bars * seconds_per_bar
