"""Test beat generation with hit-profile knowledge base."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'services', 'sound-engine', 'app'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'services', 'composition-engine', 'app', 'models'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'shared'))

import numpy as np
import soundfile as sf
from sample_engine import SampleEngine
from drum_generator import DrumPatternGenerator
from beat_knowledge_base import get_optimal_params, score_beat_against_profile

print("=" * 60)
print("THE PRODUCER -- Hit-Profile Beat Generation Test")
print("=" * 60)

# 1. Get optimal params from hit knowledge base
print("\n[1] Generating parameters from hit-beat profile...")
params = get_optimal_params()
print(f"   BPM: {params['bpm']}")
print(f"   Key: {params['key']}")
print(f"   Mood: {params['mood']}")
print(f"   Progression: {' -> '.join(params['progression'])}")
print(f"   Drum patterns: {params['drum_patterns']}")

# 2. Generate drum pattern using hit-weighted variants
print("\n[2] Generating drum pattern with hit-weighted selection...")
gen = DrumPatternGenerator(genre="trap", use_hit_profile=True)
pattern = gen.generate(bars=4)

for drum, hits in pattern.items():
    print(f"   {drum}: {len(hits)} hits")
    if hits:
        print(f"      First hit: beat {hits[0][0]:.2f}, vel {hits[0][1]}")

# 3. Generate melodic content
print("\n[3] Generating melodic instruments...")

# Chord progression notes (simplified MIDI)
chord_notes = {
    "Cm": [48, 51, 55], "Gm": [43, 46, 50], "Ab": [44, 48, 51], "Eb": [51, 55, 58],
    "Dm": [50, 53, 57], "Am": [45, 48, 52], "Bb": [46, 50, 53], "F": [41, 45, 48],
    "Fm": [41, 44, 48], "Db": [37, 41, 44],
}

# Build progression
progression = params['progression']
melody_notes = []
counter_notes = []
pad_notes = []
bass_notes = []
guitar_notes = []
piano_notes = []

current_time = 0
for chord_name in progression:
    notes = chord_notes.get(chord_name, [48, 52, 55])
    root = notes[0]
    third = notes[1]
    fifth = notes[2]
    
    # Bass line (808-style low notes)
    bass_notes.append({
        "pitch": root - 24, "velocity": 110,
        "start_time": current_time, "duration": 2.0,
    })
    bass_notes.append({
        "pitch": root - 24, "velocity": 100,
        "start_time": current_time + 2, "duration": 2.0,
    })
    
    # Pad chords (long sustained)
    for note in notes:
        pad_notes.append({
            "pitch": note + 12, "velocity": 55,
            "start_time": current_time, "duration": 4.0,
        })
    
    # Melody line (arpeggio + passing notes)
    melody_pattern = [
        (root + 24, 0.0, 0.6, 85),
        (fifth + 24, 0.6, 0.6, 75),
        (third + 24, 1.2, 0.6, 80),
        (root + 24, 1.8, 0.6, 70),
        (root + 26, 2.4, 0.8, 80),  # Passing tone
        (fifth + 24, 3.2, 0.8, 75),
    ]
    for pitch, start, dur, vel in melody_pattern:
        melody_notes.append({
            "pitch": pitch, "velocity": vel,
            "start_time": current_time + start, "duration": dur,
        })
    
    # Counter melody (simpler, fills gaps)
    counter_notes.append({
        "pitch": third + 12, "velocity": 50,
        "start_time": current_time + 0.25, "duration": 1.5,
    })
    counter_notes.append({
        "pitch": fifth + 12, "velocity": 45,
        "start_time": current_time + 2.25, "duration": 1.5,
    })
    
    # Guitar strums (every other chord, chordal)
    if current_time % 8 == 0:
        for note in notes:
            guitar_notes.append({
                "pitch": note, "velocity": 65,
                "start_time": current_time + np.random.uniform(0, 0.05),
                "duration": 3.5,
            })
    
    # Piano (rhythmic chord stabs)
    if current_time % 4 == 0:
        for note in notes:
            piano_notes.append({
                "pitch": note + 12, "velocity": 70,
                "start_time": current_time, "duration": 0.8,
            })
    
    current_time += 4.0

print(f"   Bass notes: {len(bass_notes)}")
print(f"   Pad notes: {len(pad_notes)}")
print(f"   Melody notes: {len(melody_notes)}")
print(f"   Counter notes: {len(counter_notes)}")
print(f"   Guitar notes: {len(guitar_notes)}")
print(f"   Piano notes: {len(piano_notes)}")

# 4. Render with sample engine
print("\n[4] Rendering with real Cymatics samples...")
engine = SampleEngine()

# Check available samples
categories = ["kick", "snare", "hihat", "808", "bass", "synth_pad", 
              "synth_lead", "pluck", "guitar", "piano"]
for cat in categories:
    try:
        sm = engine.load_category(cat, "trap")
        print(f"   {cat}: {len(sm.samples)} samples")
    except Exception as e:
        print(f"   {cat}: ERROR - {e}")

# Render composition
composition = {
    "tracks": {
        "drums": pattern,
        "bass": bass_notes,
        "pads": pad_notes,
        "melody": melody_notes,
        "counter_melody": counter_notes,
        "guitar": guitar_notes,
        "piano": piano_notes,
    },
    "duration_bars": len(progression) * 4
}

stems = engine.render_beat(composition, genre="trap", bpm=params['bpm'])

# 5. Analyze output levels
print("\n[5] Output Analysis:")
for stem_name, audio in stems.items():
    peak = np.max(np.abs(audio))
    rms = np.sqrt(np.mean(audio**2))
    print(f"   {stem_name}:")
    print(f"      Peak: {peak:.4f} ({peak*100:.1f}%)")
    print(f"      RMS:  {rms:.4f}")
    
    if peak < 0.05:
        print(f"      WARNING: Very quiet!")
    elif peak > 0.95:
        print(f"      WARNING: Potential clipping!")
    else:
        print(f"      OK")

# 6. Mix and save
print("\n[6] Mixing stems...")

# Custom mix with better balance
custom_gains = {
    'drums': 0, 'bass': -2, 'pads': -10,
    'melody': -4, 'counter_melody': -10,
    'guitar': -6, 'piano': -5,
}

mix = engine.mix_stems(stems, gains=custom_gains)
peak = np.max(np.abs(mix))
print(f"   Final mix peak: {peak:.4f}")

# Normalize if needed
if peak < 0.5:
    print("   Normalizing to -1dBFS...")
    mix *= 0.9 / peak
    print(f"   New peak: {np.max(np.abs(mix)):.4f}")

output_path = "output/test_hit_beat.wav"
os.makedirs("output", exist_ok=True)
sf.write(output_path, mix.T, 44100)
print(f"   Saved: {output_path}")

# Also save individual stems
print("\n[7] Saving individual stems...")
for stem_name, audio in stems.items():
    stem_path = f"output/stem_{stem_name}.wav"
    sf.write(stem_path, audio.T, 44100)
    print(f"   {stem_path}")

# 8. Score against hit profile
print("\n[8] Hit-Profile Score:")
beat_features = {
    "bpm": params['bpm'],
    "key": params['key'],
    "progression": params['progression'],
    "structure": params['structure']
}
score = score_beat_against_profile(beat_features)
print(f"   Score: {score:.1f}/100")
if score >= 70:
    print("   STRONG hit characteristics")
elif score >= 50:
    print("   Average -- could be improved")
else:
    print("   Weak hit profile")

print("\n" + "=" * 60)
print("Test complete! Check output/ folder for audio files.")
print("=" * 60)
