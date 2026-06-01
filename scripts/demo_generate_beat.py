"""Demo script: Generate a complete beat using the sample-based pipeline.

This demonstrates the core sample engine rendering a composed beat.
"""

import os
import sys
import time
import importlib.util
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Load composition engine
spec = importlib.util.spec_from_file_location(
    'music_transformer',
    os.path.join(os.path.dirname(__file__), '..', 'services', 'composition-engine', 'app', 'models', 'music_transformer.py')
)
composition_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(composition_mod)
CompositionEngine = composition_mod.CompositionEngine

# Load sample engine
spec = importlib.util.spec_from_file_location(
    'sample_engine',
    os.path.join(os.path.dirname(__file__), '..', 'services', 'sound-engine', 'app', 'sample_engine.py')
)
sample_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sample_mod)
SampleEngine = sample_mod.SampleEngine

import soundfile as sf


def generate_beat(genre: str, bpm: int, key: str, output_dir: str):
    """Generate a complete beat."""
    beat_id = f"demo_{genre}_{bpm}_{int(time.time())}"
    
    print(f"\n{'='*60}")
    print(f"  Generating {genre} beat at {bpm} BPM in {key}")
    print(f"  Beat ID: {beat_id}")
    print(f"{'='*60}\n")
    
    # Step 1: Compose
    print("[1/3] Composing...")
    composer = CompositionEngine()
    composition = composer.compose_beat(
        genre=genre,
        bpm=bpm,
        key=key,
        duration_bars=8
    )
    print(f"  -> Generated {len(composition['tracks'])} tracks")
    chord_names = []
    for chord in composition['chord_progression']:
        if isinstance(chord, dict):
            chord_names.append(chord.get('name', str(chord)))
        else:
            chord_names.append(str(chord))
    print(f"  -> Chords: {chord_names}")
    
    # Step 2: Render with samples
    print("\n[2/3] Rendering with sample engine...")
    sample_base = os.path.join(os.path.dirname(__file__), '..', 'samples')
    engine = SampleEngine(sample_base_path=sample_base)
    
    stems = engine.render_beat(composition, genre, bpm=bpm, humanize_ms=5.0)
    print(f"  -> Rendered {len(stems)} stems:")
    for name, audio in stems.items():
        duration = audio.shape[1] / engine.sample_rate
        peak = np.max(np.abs(audio))
        print(f"    - {name}: {duration:.1f}s, peak={peak:.3f}")
    
    # Mix stems
    mix = engine.mix_stems(stems)
    mix_duration = mix.shape[1] / engine.sample_rate
    mix_peak = np.max(np.abs(mix))
    print(f"  -> Mixed: {mix_duration:.1f}s, peak={mix_peak:.3f}")
    
    # Step 3: Save outputs
    print("\n[3/3] Saving outputs...")
    os.makedirs(output_dir, exist_ok=True)
    
    # Save individual stems
    stems_dir = os.path.join(output_dir, 'stems')
    os.makedirs(stems_dir, exist_ok=True)
    
    for name, audio in stems.items():
        path = os.path.join(stems_dir, f'{beat_id}_{name}.wav')
        sf.write(path, audio.T, engine.sample_rate, subtype='PCM_24')
        print(f"  -> Stem: {path}")
    
    # Save full mix
    mix_path = os.path.join(output_dir, f'{beat_id}_mix.wav')
    sf.write(mix_path, mix.T, engine.sample_rate, subtype='PCM_24')
    print(f"  -> Mix: {mix_path}")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"  BEAT GENERATED: {beat_id}")
    print(f"{'='*60}")
    print(f"  Genre: {genre}")
    print(f"  BPM: {bpm}")
    print(f"  Key: {key}")
    print(f"  Duration: {mix_duration:.1f}s")
    print(f"  Stems: {len(stems)}")
    print(f"  Output: {output_dir}")
    print(f"{'='*60}\n")
    
    return beat_id


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Generate a demo beat')
    parser.add_argument('--genre', default='trap', choices=['trap', 'drill', 'afrobeats', 'lofi'])
    parser.add_argument('--bpm', type=int, default=140)
    parser.add_argument('--key', default='C')
    parser.add_argument('--output', default='./output')
    
    args = parser.parse_args()
    generate_beat(args.genre, args.bpm, args.key, args.output)
