"""Genre-specific mix chain definitions."""

from typing import Dict, Any, List


MIX_CHAINS = {
    "trap": {
        "drums": {
            "gain": 0.0,
            "eq": [
                {"type": "high_pass", "freq": 30, "order": 2},
                {"type": "bell", "freq": 100, "gain": 2.0, "q": 1.0},
                {"type": "bell", "freq": 3000, "gain": 2.5, "q": 1.5},
                {"type": "high_shelf", "freq": 8000, "gain": 1.5}
            ],
            "compression": {
                "threshold_db": -12,
                "ratio": 4.0,
                "attack_ms": 5,
                "release_ms": 50,
                "makeup_db": 2.0
            },
            "saturation": {
                "amount": 0.2,
                "type": "soft_clip"
            },
            "stereo_width": 1.0
        },
        "bass": {
            "gain": 0.0,
            "eq": [
                {"type": "high_pass", "freq": 20, "order": 2},
                {"type": "bell", "freq": 60, "gain": 3.0, "q": 1.5},
                {"type": "low_pass", "freq": 200, "order": 2}
            ],
            "compression": {
                "threshold_db": -8,
                "ratio": 6.0,
                "attack_ms": 2,
                "release_ms": 100,
                "makeup_db": 1.0
            },
            "distortion": {
                "amount": 0.1,
                "type": "soft_clip"
            },
            "sidechain": {
                "enabled": True,
                "source": "drums",
                "amount": 0.6,
                "attack_ms": 1,
                "release_ms": 80
            }
        },
        "synth_lead": {
            "gain": -1.0,
            "eq": [
                {"type": "high_pass", "freq": 200, "order": 2},
                {"type": "bell", "freq": 2500, "gain": 2.0, "q": 1.2},
                {"type": "high_shelf", "freq": 6000, "gain": 2.0}
            ],
            "compression": {
                "threshold_db": -15,
                "ratio": 3.0,
                "attack_ms": 10,
                "release_ms": 100,
                "makeup_db": 1.5
            },
            "stereo_width": 1.2,
            "reverb_send": 0.3
        },
        "synth_pad": {
            "gain": -3.0,
            "eq": [
                {"type": "high_pass", "freq": 150, "order": 2},
                {"type": "low_shelf", "freq": 300, "gain": -2.0},
                {"type": "high_shelf", "freq": 4000, "gain": 1.0}
            ],
            "compression": {
                "threshold_db": -18,
                "ratio": 2.5,
                "attack_ms": 20,
                "release_ms": 200,
                "makeup_db": 1.0
            },
            "stereo_width": 1.4,
            "reverb_send": 0.5
        },
        "master_bus": {
            "eq": [
                {"type": "high_pass", "freq": 25, "order": 2},
                {"type": "bell", "freq": 120, "gain": 0.5, "q": 2.0},
                {"type": "bell", "freq": 3000, "gain": 0.5, "q": 1.0}
            ],
            "compression": {
                "threshold_db": -18,
                "ratio": 2.0,
                "attack_ms": 30,
                "release_ms": 200,
                "makeup_db": 1.0
            },
            "limiter": {
                "threshold_db": -1.0,
                "ceiling_db": -0.1
            }
        }
    },
    "drill": {
        "drums": {
            "gain": 0.5,
            "eq": [
                {"type": "high_pass", "freq": 30, "order": 2},
                {"type": "bell", "freq": 80, "gain": 3.0, "q": 1.2},
                {"type": "bell", "freq": 4000, "gain": 3.0, "q": 1.5},
                {"type": "high_shelf", "freq": 8000, "gain": 2.0}
            ],
            "compression": {
                "threshold_db": -10,
                "ratio": 5.0,
                "attack_ms": 3,
                "release_ms": 40,
                "makeup_db": 2.5
            },
            "saturation": {
                "amount": 0.3,
                "type": "hard_clip"
            },
            "stereo_width": 1.0
        },
        "bass": {
            "gain": 0.0,
            "eq": [
                {"type": "high_pass", "freq": 25, "order": 2},
                {"type": "bell", "freq": 50, "gain": 4.0, "q": 1.8},
                {"type": "low_pass", "freq": 150, "order": 2}
            ],
            "compression": {
                "threshold_db": -6,
                "ratio": 8.0,
                "attack_ms": 1,
                "release_ms": 120,
                "makeup_db": 0.5
            },
            "distortion": {
                "amount": 0.15,
                "type": "soft_clip"
            },
            "sidechain": {
                "enabled": True,
                "source": "drums",
                "amount": 0.8,
                "attack_ms": 1,
                "release_ms": 60
            }
        },
        "synth_lead": {
            "gain": -1.5,
            "eq": [
                {"type": "high_pass", "freq": 250, "order": 2},
                {"type": "bell", "freq": 2000, "gain": 1.5, "q": 1.5},
                {"type": "high_shelf", "freq": 5000, "gain": 1.5}
            ],
            "compression": {
                "threshold_db": -14,
                "ratio": 3.5,
                "attack_ms": 8,
                "release_ms": 80,
                "makeup_db": 1.5
            },
            "stereo_width": 1.1,
            "reverb_send": 0.25
        },
        "master_bus": {
            "eq": [
                {"type": "high_pass", "freq": 20, "order": 2},
                {"type": "bell", "freq": 100, "gain": 1.0, "q": 1.5},
                {"type": "bell", "freq": 2500, "gain": 0.5, "q": 1.0}
            ],
            "compression": {
                "threshold_db": -16,
                "ratio": 2.5,
                "attack_ms": 20,
                "release_ms": 150,
                "makeup_db": 1.0
            },
            "limiter": {
                "threshold_db": -1.0,
                "ceiling_db": -0.1
            }
        }
    },
    "lofi": {
        "drums": {
            "gain": -1.0,
            "eq": [
                {"type": "high_pass", "freq": 40, "order": 2},
                {"type": "bell", "freq": 200, "gain": -2.0, "q": 1.5},
                {"type": "low_pass", "freq": 8000, "order": 2}
            ],
            "compression": {
                "threshold_db": -14,
                "ratio": 3.0,
                "attack_ms": 10,
                "release_ms": 80,
                "makeup_db": 1.0
            },
            "saturation": {
                "amount": 0.4,
                "type": "tape"
            },
            "stereo_width": 0.9
        },
        "bass": {
            "gain": -0.5,
            "eq": [
                {"type": "high_pass", "freq": 30, "order": 2},
                {"type": "bell", "freq": 80, "gain": 2.0, "q": 1.5},
                {"type": "low_pass", "freq": 300, "order": 2}
            ],
            "compression": {
                "threshold_db": -10,
                "ratio": 4.0,
                "attack_ms": 5,
                "release_ms": 100,
                "makeup_db": 1.0
            },
            "sidechain": {
                "enabled": True,
                "source": "drums",
                "amount": 0.4,
                "attack_ms": 5,
                "release_ms": 120
            }
        },
        "synth_lead": {
            "gain": -2.0,
            "eq": [
                {"type": "high_pass", "freq": 300, "order": 2},
                {"type": "low_pass", "freq": 6000, "order": 2}
            ],
            "compression": {
                "threshold_db": -16,
                "ratio": 2.0,
                "attack_ms": 15,
                "release_ms": 150,
                "makeup_db": 1.0
            },
            "stereo_width": 1.3,
            "reverb_send": 0.6
        },
        "master_bus": {
            "eq": [
                {"type": "high_pass", "freq": 30, "order": 2},
                {"type": "bell", "freq": 200, "gain": -1.0, "q": 2.0},
                {"type": "low_pass", "freq": 12000, "order": 2}
            ],
            "compression": {
                "threshold_db": -20,
                "ratio": 1.5,
                "attack_ms": 40,
                "release_ms": 300,
                "makeup_db": 0.5
            },
            "saturation": {
                "amount": 0.2,
                "type": "tape"
            },
            "limiter": {
                "threshold_db": -2.0,
                "ceiling_db": -0.3
            }
        }
    }
}


def get_mix_chain(genre: str, track_type: str = None) -> Dict[str, Any]:
    """Get mix chain for a genre and track type."""
    genre_chain = MIX_CHAINS.get(genre, MIX_CHAINS["trap"])
    
    if track_type:
        return genre_chain.get(track_type, {})
    
    return genre_chain


def list_available_chains() -> Dict[str, List[str]]:
    """List all available mix chains."""
    return {
        genre: list(chain.keys())
        for genre, chain in MIX_CHAINS.items()
    }
