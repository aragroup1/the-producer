"""Test full beat generation with effects processing."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'services', 'sound-engine', 'app'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'services', 'composition-engine', 'app', 'models'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'shared'))

import numpy as np
import soundfile as sf
from sample_engine import SampleEngine
from drum_generator import DrumPatternGenerator
from beat_knowledge_base import get_optimal_params

print("=" * 60)
print("THE PRODUCER -- Full Pipeline Test (with Effects)")
print("=" * 60)

# Generate beat parameters
params = get_optimal_params()
print(f"\nBPM: {params['bpm']}, Key: {params['key']}, Mood: {params['mood']}")

# Generate drums
gen = DrumPatternGenerator(genre="trap", use_hit_profile=True)
pattern = gen.generate(bars=4)

# Generate simple melodic content
chord_notes = {"Cm": [48, 51, 55], "Gm": [43, 46, 50], "Ab": [44, 48, 51], "Eb": [51, 55, 58]}
progression = params['progression']

bass_notes = []
pad_notes = []
melody_notes = []

current_time = 0
for chord_name in progression:
    notes = chord_notes.get(chord_name, [48, 52, 55])
    root = notes[0]
    
    bass_notes.append({"pitch": root - 24, "velocity": 110, "start_time": current_time, "duration": 2.0})
    bass_notes.append({"pitch": root - 24, "velocity": 100, "start_time": current_time + 2, "duration": 2.0})
    
    for note in notes:
        pad_notes.append({"pitch": note + 12, "velocity": 55, "start_time": current_time, "duration": 4.0})
    
    melody_notes.append({"pitch": root + 24, "velocity": 80, "start_time": current_time, "duration": 0.8})
    melody_notes.append({"pitch": notes[2] + 24, "velocity": 75, "start_time": current_time + 1.0, "duration": 0.8})
    
    current_time += 4.0

# Render with effects enabled
print("\nRendering with effects processing...")
engine = SampleEngine(use_effects=True)

composition = {
    "tracks": {
        "drums": pattern,
        "bass": bass_notes,
        "pads": pad_notes,
        "melody": melody_notes,
    },
    "duration_bars": len(progression) * 4
}

stems = engine.render_beat(composition, genre="trap", bpm=params['bpm'])

print("\nStem levels (raw):")
for name, audio in stems.items():
    peak = np.max(np.abs(audio))
    rms = np.sqrt(np.mean(audio**2))
    print(f"  {name}: peak={peak:.4f}, rms={rms:.4f}")

# Mix WITH effects
print("\nMixing with effects processing...")
mix_with_effects = engine.mix_stems(stems, apply_effects=True, genre='trap')
print(f"  Final mix (with effects): peak={np.max(np.abs(mix_with_effects)):.4f}, rms={np.sqrt(np.mean(mix_with_effects**2)):.4f}")

# Mix WITHOUT effects for comparison
print("\nMixing WITHOUT effects (dry)...")
mix_dry = engine.mix_stems(stems, apply_effects=False)
print(f"  Final mix (dry): peak={np.max(np.abs(mix_dry)):.4f}, rms={np.sqrt(np.mean(mix_dry**2)):.4f}")

# Save both versions
os.makedirs("output", exist_ok=True)
sf.write("output/test_with_effects.wav", mix_with_effects.T, 44100)
sf.write("output/test_dry.wav", mix_dry.T, 44100)

print("\nSaved:")
print("  output/test_with_effects.wav")
print("  output/test_dry.wav")

# Compare loudness
from scipy import signal
f, t, Sxx_dry = signal.spectrogram(mix_dry[0], 44100, nperseg=2048)
f, t, Sxx_wet = signal.spectrogram(mix_with_effects[0], 44100, nperseg=2048)

print("\nSpectral comparison (dry vs wet):")
print(f"  Low (<100Hz): {np.mean(Sxx_dry[f<100]):.2e} vs {np.mean(Sxx_wet[f<100]):.2e}")
print(f"  Mids (200-2kHz): {np.mean(Sxx_dry[(f>=200)&(f<2000)]):.2e} vs {np.mean(Sxx_wet[(f>=200)&(f<2000)]):.2e}")
print(f"  High (>5kHz): {np.mean(Sxx_dry[f>=5000]):.2e} vs {np.mean(Sxx_wet[f>=5000]):.2e}")

print("\n" + "=" * 60)
print("Test complete! Compare the two files to hear the difference.")
print("=" * 60)
