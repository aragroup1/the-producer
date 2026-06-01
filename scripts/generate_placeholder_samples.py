#!/usr/bin/env python3
"""Generate placeholder WAV samples for testing the SampleEngine.

These are synthetic sounds — not production quality — but let us test
the rendering pipeline immediately across ALL 20 genres. Replace with
real sample packs for commercial output.

Usage:
    python scripts/generate_placeholder_samples.py
"""

import os
import numpy as np
import soundfile as sf
from scipy import signal

SAMPLE_RATE = 44100


def generate_kick(duration=0.5, pitch_drop=True, soft=False) -> np.ndarray:
    """Generate a synthetic kick drum."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
    
    if soft:
        # Softer kick for lofi/rnb
        freq = 50 * np.exp(-t * 10)
        amp = np.exp(-t * 5)
    else:
        freq = 60 * np.exp(-t * 15) if pitch_drop else np.full_like(t, 50)
        amp = np.exp(-t * 8)
    
    kick = amp * np.sin(2 * np.pi * freq * t)
    
    # Click at start
    click = np.zeros_like(t)
    click[:100] = np.random.randn(100) * 0.3 * np.exp(-np.linspace(0, 5, 100))
    
    return kick + click


def generate_snare(duration=0.3, tight=False) -> np.ndarray:
    """Generate a synthetic snare."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
    
    body = np.sin(2 * np.pi * (180 if tight else 200) * t) * np.exp(-t * (25 if tight else 20))
    noise = np.random.randn(len(t)) * np.exp(-t * (20 if tight else 15)) * 0.5
    crack = np.random.randn(len(t)) * np.exp(-t * 50) * 0.3
    
    return body + noise + crack


def generate_hihat(duration=0.1, closed=True, metallic=True) -> np.ndarray:
    """Generate a synthetic hi-hat."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
    noise = np.random.randn(len(t))
    
    if metallic:
        sos = signal.butter(4, [8000, 12000], btype='band', fs=SAMPLE_RATE, output='sos')
        filtered = signal.sosfilt(sos, noise)
    else:
        # Softer, less metallic for lofi/rnb
        sos = signal.butter(4, [6000, 10000], btype='band', fs=SAMPLE_RATE, output='sos')
        filtered = signal.sosfilt(sos, noise) * 0.7
    
    env = np.exp(-t * (80 if closed else 15))
    return filtered * env * 0.5


def generate_808(note='C', duration=2.0, distorted=False) -> np.ndarray:
    """Generate a synthetic 808 bass."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
    
    note_freqs = {
        'C': 32.70, 'C#': 34.65, 'D': 36.71, 'D#': 38.89,
        'E': 41.20, 'F': 43.65, 'F#': 46.25, 'G': 49.00,
        'G#': 51.91, 'A': 55.00, 'A#': 58.27, 'B': 61.74
    }
    freq = note_freqs.get(note, 32.70)
    
    amp = np.exp(-t * 2)
    sine = amp * np.sin(2 * np.pi * freq * t)
    sine += 0.3 * amp * np.sin(2 * np.pi * freq * 2 * t)
    sine += 0.1 * amp * np.sin(2 * np.pi * freq * 3 * t)
    
    if distorted:
        sine = np.tanh(sine * 3) * 0.5
    
    return sine


def generate_synth_lead(note='C', duration=1.0, waveform='saw', bright=True) -> np.ndarray:
    """Generate a synthetic synth lead."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
    
    note_freqs = {
        'C': 261.63, 'C#': 277.18, 'D': 293.66, 'D#': 311.13,
        'E': 329.63, 'F': 349.23, 'F#': 369.99, 'G': 392.00,
        'G#': 415.30, 'A': 440.00, 'A#': 466.16, 'B': 493.88
    }
    freq = note_freqs.get(note, 261.63)
    
    if waveform == 'saw':
        wave = np.zeros_like(t)
        for n in range(1, 20):
            wave += ((-1)**(n+1)) * np.sin(2 * np.pi * freq * n * t) / n
        wave *= 0.3
    elif waveform == 'square':
        wave = np.zeros_like(t)
        for n in range(1, 20, 2):
            wave += np.sin(2 * np.pi * freq * n * t) / n
        wave *= 0.3
    elif waveform == 'sine':
        wave = np.sin(2 * np.pi * freq * t) * 0.5
    else:
        wave = np.sin(2 * np.pi * freq * t) * 0.5
    
    env = np.ones_like(t)
    attack = int(0.01 * SAMPLE_RATE)
    release = int(0.1 * SAMPLE_RATE)
    env[:attack] = np.linspace(0, 1, attack)
    env[-release:] = np.linspace(1, 0, release)
    
    return wave * env * (0.6 if bright else 0.4)


def generate_pad(note='C', duration=2.0, warm=False) -> np.ndarray:
    """Generate a synthetic pad."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
    
    note_freqs = {
        'C': 261.63, 'C#': 277.18, 'D': 293.66, 'D#': 311.13,
        'E': 329.63, 'F': 349.23, 'F#': 369.99, 'G': 392.00,
        'G#': 415.30, 'A': 440.00, 'A#': 466.16, 'B': 493.88
    }
    freq = note_freqs.get(note, 261.63)
    
    pad = np.zeros_like(t)
    detunes = [0, 0.3, -0.2, 0.5] if warm else [0, 0.5, -0.3, 0.8]
    for detune in detunes:
        f = freq * (1 + detune / 100)
        pad += np.sin(2 * np.pi * f * t) * 0.15
    
    env = np.ones_like(t)
    attack = int(0.5 * SAMPLE_RATE)
    release = int(1.0 * SAMPLE_RATE)
    env[:attack] = np.linspace(0, 1, attack)
    env[-release:] = np.linspace(1, 0, release)
    
    return pad * env


def generate_pluck(note='C', duration=0.8, soft=False) -> np.ndarray:
    """Generate a synthetic pluck."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
    
    note_freqs = {
        'C': 261.63, 'C#': 277.18, 'D': 293.66, 'D#': 311.13,
        'E': 329.63, 'F': 349.23, 'F#': 369.99, 'G': 392.00,
        'G#': 415.30, 'A': 440.00, 'A#': 466.16, 'B': 493.88
    }
    freq = note_freqs.get(note, 261.63)
    
    wave = np.sin(2 * np.pi * freq * t)
    wave += 0.3 * np.sin(2 * np.pi * freq * 2 * t)
    
    decay = 4 if soft else 6
    env = np.exp(-t * decay)
    
    return wave * env * 0.5


def generate_piano(note='C', duration=1.5) -> np.ndarray:
    """Generate a synthetic piano one-shot."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
    
    note_freqs = {
        'C': 261.63, 'C#': 277.18, 'D': 293.66, 'D#': 311.13,
        'E': 329.63, 'F': 349.23, 'F#': 369.99, 'G': 392.00,
        'G#': 415.30, 'A': 440.00, 'A#': 466.16, 'B': 493.88
    }
    freq = note_freqs.get(note, 261.63)
    
    # Multiple harmonics for piano-like timbre
    wave = np.zeros_like(t)
    for n, amp in [(1, 1.0), (2, 0.5), (3, 0.25), (4, 0.15), (5, 0.1)]:
        wave += amp * np.sin(2 * np.pi * freq * n * t)
    
    # Piano envelope: sharp attack, exponential decay
    env = np.exp(-t * 3)
    env[:int(0.005 * SAMPLE_RATE)] = np.linspace(0, 1, int(0.005 * SAMPLE_RATE))
    
    return wave * env * 0.4


def generate_guitar(note='C', duration=1.2, nylon=False) -> np.ndarray:
    """Generate a synthetic guitar one-shot."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
    
    note_freqs = {
        'C': 261.63, 'C#': 277.18, 'D': 293.66, 'D#': 311.13,
        'E': 329.63, 'F': 349.23, 'F#': 369.99, 'G': 392.00,
        'G#': 415.30, 'A': 440.00, 'A#': 466.16, 'B': 493.88
    }
    freq = note_freqs.get(note, 261.63)
    
    # String-like with harmonics
    wave = np.zeros_like(t)
    harmonics = [1, 2, 3, 4, 5] if nylon else [1, 2, 3, 4, 5, 6]
    for n in harmonics:
        amp = 1.0 / n if nylon else 1.0 / (n ** 0.8)
        wave += amp * np.sin(2 * np.pi * freq * n * t)
    
    # String envelope
    env = np.exp(-t * (2.5 if nylon else 3.5))
    
    return wave * env * 0.35


def generate_perc(variation='shaker', duration=0.3) -> np.ndarray:
    """Generate synthetic percussion."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
    
    if variation == 'shaker':
        noise = np.random.randn(len(t))
        sos = signal.butter(4, [3000, 8000], btype='band', fs=SAMPLE_RATE, output='sos')
        filtered = signal.sosfilt(sos, noise)
        env = np.exp(-t * 20)
        return filtered * env * 0.4
    elif variation == 'conga':
        freq = 150
        wave = np.sin(2 * np.pi * freq * t) * np.exp(-t * 10)
        return wave * 0.5
    elif variation == 'tambourine':
        noise = np.random.randn(len(t))
        sos = signal.butter(4, [5000, 10000], btype='band', fs=SAMPLE_RATE, output='sos')
        filtered = signal.sosfilt(sos, noise)
        env = np.exp(-t * 30)
        return filtered * env * 0.35
    else:
        noise = np.random.randn(len(t)) * np.exp(-t * 15) * 0.3
        return noise


def generate_fx(variation='riser', duration=2.0) -> np.ndarray:
    """Generate synthetic FX sounds."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
    
    if variation == 'riser':
        # Frequency sweep up
        freq = np.linspace(100, 5000, len(t))
        phase = np.cumsum(2 * np.pi * freq / SAMPLE_RATE)
        wave = np.sin(phase) * np.linspace(0, 0.5, len(t))
        return wave
    elif variation == 'impact':
        # Low frequency thud
        freq = 80
        wave = np.sin(2 * np.pi * freq * t) * np.exp(-t * 8)
        noise = np.random.randn(len(t)) * np.exp(-t * 20) * 0.3
        return (wave + noise) * 0.6
    elif variation == 'sweep':
        # Filter sweep
        noise = np.random.randn(len(t))
        wave = np.zeros_like(t)
        for i in range(len(t)):
            cutoff = int(100 + (t[i] / duration) * 8000)
            if i > 10:
                wave[i] = noise[i] * 0.3 * (t[i] / duration)
        return wave
    else:
        # Ambient texture
        noise = np.random.randn(len(t))
        sos = signal.butter(4, [200, 2000], btype='band', fs=SAMPLE_RATE, output='sos')
        filtered = signal.sosfilt(sos, noise)
        env = np.ones_like(t)
        env[:int(0.5*SAMPLE_RATE)] = np.linspace(0, 1, int(0.5*SAMPLE_RATE))
        env[-int(0.5*SAMPLE_RATE):] = np.linspace(1, 0, int(0.5*SAMPLE_RATE))
        return filtered * env * 0.2


def save_sample(audio: np.ndarray, path: str):
    """Save mono sample as stereo WAV."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    stereo = np.stack([audio, audio])
    sf.write(path, stereo.T, SAMPLE_RATE, subtype='PCM_24')


# Genre configurations for sample generation
GENRE_CONFIGS = {
    'trap': {
        'kick': {'pitch_drop': True, 'soft': False},
        'snare': {'tight': False},
        'hihat': {'metallic': True},
        '808': {'distorted': True},
        'lead_waveform': 'saw',
        'lead_bright': True,
        'pad_warm': False,
        'pluck_soft': False,
    },
    'drill': {
        'kick': {'pitch_drop': True, 'soft': False},
        'snare': {'tight': True},
        'hihat': {'metallic': True},
        '808': {'distorted': False},
        'lead_waveform': 'saw',
        'lead_bright': False,
        'pad_warm': False,
        'pluck_soft': False,
    },
    'boom_bap': {
        'kick': {'pitch_drop': False, 'soft': False},
        'snare': {'tight': False},
        'hihat': {'metallic': False},
        '808': {'distorted': False},
        'lead_waveform': 'square',
        'lead_bright': False,
        'pad_warm': True,
        'pluck_soft': True,
    },
    'rage': {
        'kick': {'pitch_drop': True, 'soft': False},
        'snare': {'tight': True},
        'hihat': {'metallic': True},
        '808': {'distorted': True},
        'lead_waveform': 'saw',
        'lead_bright': True,
        'pad_warm': False,
        'pluck_soft': False,
    },
    'phonk': {
        'kick': {'pitch_drop': False, 'soft': False},
        'snare': {'tight': False},
        'hihat': {'metallic': False},
        '808': {'distorted': True},
        'lead_waveform': 'saw',
        'lead_bright': False,
        'pad_warm': True,
        'pluck_soft': True,
    },
    'jersey_club': {
        'kick': {'pitch_drop': True, 'soft': False},
        'snare': {'tight': True},
        'hihat': {'metallic': True},
        '808': {'distorted': False},
        'lead_waveform': 'saw',
        'lead_bright': True,
        'pad_warm': False,
        'pluck_soft': False,
    },
    'plugg': {
        'kick': {'pitch_drop': False, 'soft': True},
        'snare': {'tight': True},
        'hihat': {'metallic': True},
        '808': {'distorted': False},
        'lead_waveform': 'sine',
        'lead_bright': False,
        'pad_warm': True,
        'pluck_soft': True,
    },
    'west_coast': {
        'kick': {'pitch_drop': False, 'soft': False},
        'snare': {'tight': False},
        'hihat': {'metallic': False},
        '808': {'distorted': False},
        'lead_waveform': 'square',
        'lead_bright': False,
        'pad_warm': True,
        'pluck_soft': False,
    },
    'rnb': {
        'kick': {'pitch_drop': False, 'soft': True},
        'snare': {'tight': True},
        'hihat': {'metallic': False},
        '808': {'distorted': False},
        'lead_waveform': 'sine',
        'lead_bright': False,
        'pad_warm': True,
        'pluck_soft': True,
    },
    'neo_soul': {
        'kick': {'pitch_drop': False, 'soft': True},
        'snare': {'tight': False},
        'hihat': {'metallic': False},
        '808': {'distorted': False},
        'lead_waveform': 'sine',
        'lead_bright': False,
        'pad_warm': True,
        'pluck_soft': True,
    },
    'afrobeats': {
        'kick': {'pitch_drop': False, 'soft': False},
        'snare': {'tight': False},
        'hihat': {'metallic': True},
        '808': {'distorted': False},
        'lead_waveform': 'saw',
        'lead_bright': True,
        'pad_warm': True,
        'pluck_soft': False,
    },
    'amapiano': {
        'kick': {'pitch_drop': False, 'soft': True},
        'snare': {'tight': True},
        'hihat': {'metallic': True},
        '808': {'distorted': False},
        'lead_waveform': 'sine',
        'lead_bright': False,
        'pad_warm': True,
        'pluck_soft': True,
    },
    'dancehall': {
        'kick': {'pitch_drop': False, 'soft': False},
        'snare': {'tight': False},
        'hihat': {'metallic': True},
        '808': {'distorted': False},
        'lead_waveform': 'saw',
        'lead_bright': True,
        'pad_warm': False,
        'pluck_soft': False,
    },
    'reggaeton': {
        'kick': {'pitch_drop': False, 'soft': False},
        'snare': {'tight': True},
        'hihat': {'metallic': True},
        '808': {'distorted': False},
        'lead_waveform': 'saw',
        'lead_bright': True,
        'pad_warm': False,
        'pluck_soft': False,
    },
    'hyperpop': {
        'kick': {'pitch_drop': True, 'soft': False},
        'snare': {'tight': True},
        'hihat': {'metallic': True},
        '808': {'distorted': True},
        'lead_waveform': 'saw',
        'lead_bright': True,
        'pad_warm': False,
        'pluck_soft': False,
    },
    'edm_trap': {
        'kick': {'pitch_drop': True, 'soft': False},
        'snare': {'tight': True},
        'hihat': {'metallic': True},
        '808': {'distorted': True},
        'lead_waveform': 'saw',
        'lead_bright': True,
        'pad_warm': False,
        'pluck_soft': False,
    },
    'future_bass': {
        'kick': {'pitch_drop': True, 'soft': False},
        'snare': {'tight': True},
        'hihat': {'metallic': True},
        '808': {'distorted': False},
        'lead_waveform': 'saw',
        'lead_bright': True,
        'pad_warm': True,
        'pluck_soft': True,
    },
    'lofi': {
        'kick': {'pitch_drop': False, 'soft': True},
        'snare': {'tight': False},
        'hihat': {'metallic': False},
        '808': {'distorted': False},
        'lead_waveform': 'sine',
        'lead_bright': False,
        'pad_warm': True,
        'pluck_soft': True,
    },
    'ambient': {
        'kick': {'pitch_drop': False, 'soft': True},
        'snare': {'tight': False},
        'hihat': {'metallic': False},
        '808': {'distorted': False},
        'lead_waveform': 'sine',
        'lead_bright': False,
        'pad_warm': True,
        'pluck_soft': True,
    },
}


def generate_all_samples(base_dir: str = 'samples'):
    """Generate complete placeholder sample library for ALL 20 genres."""
    print("Generating placeholder samples for all 20 genres...")
    
    all_notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    lead_notes = ['C', 'D', 'E', 'F', 'G']
    pad_notes = ['C', 'F', 'G']
    pluck_notes = ['C', 'D', 'E', 'G', 'A']
    bass_notes = ['C', 'D', 'E', 'F', 'G']
    piano_notes = ['C', 'D', 'E', 'F', 'G', 'A']
    guitar_notes = ['C', 'D', 'E', 'F', 'G', 'A']
    
    total_files = 0
    
    for genre, config in GENRE_CONFIGS.items():
        print(f"  Generating {genre} samples...")
        
        # Kicks (3 variations)
        for i in range(3):
            kick = generate_kick(duration=0.5, **config['kick'])
            save_sample(kick, f'{base_dir}/drums/kicks/{genre}/kick_{i+1:02d}.wav')
            total_files += 1
        
        # Snares (3 variations)
        for i in range(3):
            snare = generate_snare(duration=0.3, **config['snare'])
            save_sample(snare, f'{base_dir}/drums/snares/{genre}/snare_{i+1:02d}.wav')
            total_files += 1
        
        # Hi-hats closed (2 variations)
        for i in range(2):
            hihat = generate_hihat(duration=0.1, closed=True, **config['hihat'])
            save_sample(hihat, f'{base_dir}/drums/hihats/{genre}/hihat_closed_{i+1:02d}.wav')
            total_files += 1
        
        # Open hi-hat
        hihat_open = generate_hihat(duration=0.4, closed=False, **config['hihat'])
        save_sample(hihat_open, f'{base_dir}/drums/hihats/{genre}/hihat_open_01.wav')
        total_files += 1
        
        # Claps
        clap = generate_snare(duration=0.2, tight=True) * 0.7
        save_sample(clap, f'{base_dir}/drums/claps/{genre}/clap_01.wav')
        total_files += 1
        
        # 808s (all 12 semitones)
        for note in all_notes:
            bass = generate_808(note, duration=2.0, **config['808'])
            save_sample(bass, f'{base_dir}/drums/808s/{genre}/808_{note}.wav')
            total_files += 1
        
        # Percussion (3 variations)
        for i, perc_type in enumerate(['shaker', 'conga', 'tambourine']):
            perc = generate_perc(variation=perc_type, duration=0.3)
            save_sample(perc, f'{base_dir}/drums/percs/{genre}/perc_{i+1:02d}.wav')
            total_files += 1
        
        # Cymbals (crash + ride)
        crash = generate_hihat(duration=0.8, closed=False, metallic=True)
        save_sample(crash * 0.8, f'{base_dir}/drums/cymbals/{genre}/crash_01.wav')
        ride = generate_hihat(duration=1.0, closed=False, metallic=False)
        save_sample(ride * 0.6, f'{base_dir}/drums/cymbals/{genre}/ride_01.wav')
        total_files += 2
        
        # Synth leads
        for note in lead_notes:
            lead = generate_synth_lead(note, duration=1.0, 
                                       waveform=config['lead_waveform'],
                                       bright=config['lead_bright'])
            save_sample(lead, f'{base_dir}/melodic/synth_leads/{genre}/lead_{note}.wav')
            total_files += 1
        
        # Pads
        for note in pad_notes:
            pad = generate_pad(note, duration=2.0, warm=config['pad_warm'])
            save_sample(pad, f'{base_dir}/melodic/synth_pads/{genre}/pad_{note}.wav')
            total_files += 1
        
        # Plucks
        for note in pluck_notes:
            pluck = generate_pluck(note, duration=0.8, soft=config['pluck_soft'])
            save_sample(pluck, f'{base_dir}/melodic/plucks/{genre}/pluck_{note}.wav')
            total_files += 1
        
        # Bass
        for note in bass_notes:
            bass = generate_808(note, duration=1.5, distorted=False)
            save_sample(bass, f'{base_dir}/melodic/bass/{genre}/bass_{note}.wav')
            total_files += 1
        
        # Pianos
        for note in piano_notes:
            piano = generate_piano(note, duration=1.5)
            save_sample(piano, f'{base_dir}/melodic/pianos/{genre}/piano_{note}.wav')
            total_files += 1
        
        # Guitars
        for note in guitar_notes:
            guitar = generate_guitar(note, duration=1.2, nylon=(genre in ['afrobeats', 'rnb']))
            save_sample(guitar, f'{base_dir}/melodic/guitars/{genre}/guitar_{note}.wav')
            total_files += 1
    
    # FX (genre-agnostic)
    print("  Generating FX samples...")
    for i in range(5):
        riser = generate_fx('riser', duration=2.0 + i * 0.5)
        save_sample(riser, f'{base_dir}/fx/risers/all/riser_{i+1:02d}.wav')
        total_files += 1
        
        impact = generate_fx('impact', duration=1.0)
        save_sample(impact, f'{base_dir}/fx/impacts/all/impact_{i+1:02d}.wav')
        total_files += 1
        
        sweep = generate_fx('sweep', duration=1.5)
        save_sample(sweep, f'{base_dir}/fx/transitions/all/transition_{i+1:02d}.wav')
        total_files += 1
        
        ambience = generate_fx('ambience', duration=3.0)
        save_sample(ambience, f'{base_dir}/fx/ambience/all/ambience_{i+1:02d}.wav')
        total_files += 1
    
    print(f"\nDone! Generated {total_files} placeholder samples in {base_dir}/")
    print("These are synthetic sounds for testing. Replace with real sample packs for commercial output.")


if __name__ == '__main__':
    generate_all_samples()
