"""Generate placeholder WAV samples for testing the SampleEngine.

These are synthetic sounds — not production quality — but let us test
the rendering pipeline immediately. Replace with real sample packs later.
"""

import os
import numpy as np
import soundfile as sf
from scipy import signal

SAMPLE_RATE = 44100


def generate_kick(duration=0.5, pitch_drop=True) -> np.ndarray:
    """Generate a synthetic kick drum."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
    
    # Pitch drop from 60Hz to 30Hz
    if pitch_drop:
        freq = 60 * np.exp(-t * 15)
    else:
        freq = np.full_like(t, 50)
    
    # Sine with amplitude envelope
    amp = np.exp(-t * 8)
    kick = amp * np.sin(2 * np.pi * freq * t)
    
    # Add click at start
    click = np.zeros_like(t)
    click[:100] = np.random.randn(100) * 0.3 * np.exp(-np.linspace(0, 5, 100))
    
    return kick + click


def generate_snare(duration=0.3) -> np.ndarray:
    """Generate a synthetic snare."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
    
    # Body (tuned noise)
    body = np.sin(2 * np.pi * 200 * t) * np.exp(-t * 20)
    
    # Noise (snares)
    noise = np.random.randn(len(t)) * np.exp(-t * 15) * 0.5
    
    # High-frequency crack
    crack = np.random.randn(len(t)) * np.exp(-t * 50) * 0.3
    
    return body + noise + crack


def generate_hihat(duration=0.1, closed=True) -> np.ndarray:
    """Generate a synthetic hi-hat."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
    
    # White noise with metallic filter
    noise = np.random.randn(len(t))
    
    # Bandpass around 8-12kHz
    sos = signal.butter(4, [8000, 12000], btype='band', fs=SAMPLE_RATE, output='sos')
    filtered = signal.sosfilt(sos, noise)
    
    # Envelope
    if closed:
        env = np.exp(-t * 80)
    else:
        env = np.exp(-t * 15)
    
    return filtered * env * 0.5


def generate_808(note='C', duration=2.0, distorted=False) -> np.ndarray:
    """Generate a synthetic 808 bass."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
    
    # Note frequencies
    note_freqs = {
        'C': 32.70, 'C#': 34.65, 'D': 36.71, 'D#': 38.89,
        'E': 41.20, 'F': 43.65, 'F#': 46.25, 'G': 49.00,
        'G#': 51.91, 'A': 55.00, 'A#': 58.27, 'B': 61.74
    }
    freq = note_freqs.get(note, 32.70)
    
    # Sine with long decay
    amp = np.exp(-t * 2)
    sine = amp * np.sin(2 * np.pi * freq * t)
    
    # Add harmonics for richness
    sine += 0.3 * amp * np.sin(2 * np.pi * freq * 2 * t)
    sine += 0.1 * amp * np.sin(2 * np.pi * freq * 3 * t)
    
    if distorted:
        # Soft clip for distortion
        sine = np.tanh(sine * 3) * 0.5
    
    return sine


def generate_synth_lead(note='C', duration=1.0, waveform='saw') -> np.ndarray:
    """Generate a synthetic synth lead."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
    
    note_freqs = {
        'C': 261.63, 'C#': 277.18, 'D': 293.66, 'D#': 311.13,
        'E': 329.63, 'F': 349.23, 'F#': 369.99, 'G': 392.00,
        'G#': 415.30, 'A': 440.00, 'A#': 466.16, 'B': 493.88
    }
    freq = note_freqs.get(note, 261.63)
    
    if waveform == 'saw':
        # Sawtooth approximation
        wave = np.zeros_like(t)
        for n in range(1, 20):
            wave += ((-1)**(n+1)) * np.sin(2 * np.pi * freq * n * t) / n
        wave *= 0.3
    elif waveform == 'square':
        wave = np.zeros_like(t)
        for n in range(1, 20, 2):
            wave += np.sin(2 * np.pi * freq * n * t) / n
        wave *= 0.3
    else:
        wave = np.sin(2 * np.pi * freq * t) * 0.5
    
    # Envelope
    env = np.ones_like(t)
    attack = int(0.01 * SAMPLE_RATE)
    release = int(0.1 * SAMPLE_RATE)
    env[:attack] = np.linspace(0, 1, attack)
    env[-release:] = np.linspace(1, 0, release)
    
    return wave * env


def generate_pad(note='C', duration=2.0) -> np.ndarray:
    """Generate a synthetic pad."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
    
    note_freqs = {
        'C': 261.63, 'D': 293.66, 'E': 329.63, 'F': 349.23,
        'G': 392.00, 'A': 440.00, 'B': 493.88
    }
    freq = note_freqs.get(note, 261.63)
    
    # Multiple detuned oscillators
    pad = np.zeros_like(t)
    for detune in [0, 0.5, -0.3, 0.8]:
        f = freq * (1 + detune / 100)
        pad += np.sin(2 * np.pi * f * t) * 0.15
    
    # Slow attack/release
    env = np.ones_like(t)
    attack = int(0.5 * SAMPLE_RATE)
    release = int(1.0 * SAMPLE_RATE)
    env[:attack] = np.linspace(0, 1, attack)
    env[-release:] = np.linspace(1, 0, release)
    
    return pad * env


def generate_pluck(note='C', duration=0.8) -> np.ndarray:
    """Generate a synthetic pluck."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
    
    note_freqs = {
        'C': 261.63, 'D': 293.66, 'E': 329.63, 'F': 349.23,
        'G': 392.00, 'A': 440.00, 'B': 493.88
    }
    freq = note_freqs.get(note, 261.63)
    
    # Triangle-like with fast decay
    wave = np.sin(2 * np.pi * freq * t)
    wave += 0.3 * np.sin(2 * np.pi * freq * 2 * t)
    
    env = np.exp(-t * 6)
    
    return wave * env * 0.5


def save_sample(audio: np.ndarray, path: str):
    """Save mono sample as stereo WAV."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    stereo = np.stack([audio, audio])
    sf.write(path, stereo.T, SAMPLE_RATE, subtype='PCM_24')


def generate_all_samples(base_dir: str = 'samples'):
    """Generate complete placeholder sample library."""
    print("Generating placeholder samples...")
    
    genres = ['trap', 'drill', 'afrobeats', 'lofi']
    
    for genre in genres:
        print(f"  {genre}...")
        
        # Kicks
        for i in range(3):
            kick = generate_kick(duration=0.5, pitch_drop=(genre != 'lofi'))
            save_sample(kick, f'{base_dir}/drums/kicks/{genre}/kick_{i+1:02d}.wav')
        
        # Snares
        for i in range(3):
            snare = generate_snare(duration=0.3)
            save_sample(snare, f'{base_dir}/drums/snares/{genre}/snare_{i+1:02d}.wav')
        
        # Hi-hats
        for i in range(2):
            hihat = generate_hihat(duration=0.1, closed=True)
            save_sample(hihat, f'{base_dir}/drums/hihats/{genre}/hihat_closed_{i+1:02d}.wav')
        
        # Open hi-hats
        hihat_open = generate_hihat(duration=0.4, closed=False)
        save_sample(hihat_open, f'{base_dir}/drums/hihats/{genre}/hihat_open_01.wav')
        
        # Claps
        clap = generate_snare(duration=0.2) * 0.7  # Simpler for clap
        save_sample(clap, f'{base_dir}/drums/claps/{genre}/clap_01.wav')
        
        # 808s (keyed)
        notes = ['C', 'D', 'E', 'F', 'G', 'A']
        for note in notes:
            bass = generate_808(note, duration=2.0, distorted=(genre == 'trap'))
            save_sample(bass, f'{base_dir}/drums/808s/{genre}/808_{note}.wav')
        
        # Synth leads (keyed)
        for note in ['C', 'D', 'E', 'F', 'G']:
            lead = generate_synth_lead(note, duration=1.0, 
                                       waveform='saw' if genre in ['trap', 'drill'] else 'square')
            save_sample(lead, f'{base_dir}/melodic/synth_leads/{genre}/lead_{note}.wav')
        
        # Pads (keyed)
        for note in ['C', 'F', 'G']:
            pad = generate_pad(note, duration=2.0)
            save_sample(pad, f'{base_dir}/melodic/synth_pads/{genre}/pad_{note}.wav')
        
        # Plucks (keyed)
        for note in ['C', 'D', 'E', 'G', 'A']:
            pluck = generate_pluck(note, duration=0.8)
            save_sample(pluck, f'{base_dir}/melodic/plucks/{genre}/pluck_{note}.wav')
        
        # Bass (keyed)
        for note in ['C', 'D', 'E', 'F', 'G']:
            bass = generate_808(note, duration=1.5, distorted=False)
            save_sample(bass, f'{base_dir}/melodic/bass/{genre}/bass_{note}.wav')
    
    print(f"Done! Samples saved to {base_dir}/")


if __name__ == '__main__':
    generate_all_samples()
