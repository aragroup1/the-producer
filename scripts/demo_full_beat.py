"""Demo: Generate a full commercial-length beat with song structure.

Generates 2-3 minute beats with:
- Intro/Verse/Hook/Bridge/Outro
- Different instrumentation per section
- Proper arrangement and dynamics
"""

import os
import sys
import time
import argparse
import importlib.util
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Load song structure generator
spec = importlib.util.spec_from_file_location(
    'song_structure',
    os.path.join(os.path.dirname(__file__), '..', 'services', 'composition-engine', 'app', 'models', 'song_structure.py')
)
song_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(song_mod)
SongStructureGenerator = song_mod.SongStructureGenerator
format_duration = song_mod.format_duration

# Load sample engine
spec = importlib.util.spec_from_file_location(
    'sample_engine',
    os.path.join(os.path.dirname(__file__), '..', 'services', 'sound-engine', 'app', 'sample_engine.py')
)
sample_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sample_mod)
SampleEngine = sample_mod.SampleEngine

import soundfile as sf


def generate_full_beat(genre: str, bpm: int, key: str, structure: str, output_dir: str):
    """Generate a complete commercial-length beat."""
    beat_id = f"{genre}_{bpm}_{key}_{structure}_{int(time.time())}"
    
    print(f"\n{'='*70}")
    print(f"  GENERATING: {genre.upper()} BEAT")
    print(f"  BPM: {bpm} | Key: {key} | Structure: {structure}")
    print(f"  Beat ID: {beat_id}")
    print(f"{'='*70}\n")
    
    # Step 1: Compose full song structure
    print("[1/3] Composing song structure...")
    generator = SongStructureGenerator()
    composition = generator.generate_full_beat(
        genre=genre,
        bpm=bpm,
        key=key,
        structure=structure
    )
    
    print(f"  -> Duration: {format_duration(composition['total_duration_seconds'])}")
    print(f"  -> Bars: {composition['total_bars']}")
    print(f"  -> Sections: {len(composition['section_order'])}")
    print(f"\n  Structure:")
    for section_name in composition['section_order']:
        section = composition['sections'][section_name]
        start = section['start_time']
        end = start + section['bar_count'] * 4
        print(f"    {section_name:12s} | {format_duration(start * 60 / bpm)} - {format_duration(end * 60 / bpm)} | intensity: {section['intensity']:.1f}")
    
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
    
    # Mix
    mix = engine.mix_stems(stems)
    mix_duration = mix.shape[1] / engine.sample_rate
    mix_peak = np.max(np.abs(mix))
    print(f"  -> Mixed: {mix_duration:.1f}s, peak={mix_peak:.3f}")
    
    # Step 3: Save
    print("\n[3/3] Saving outputs...")
    os.makedirs(output_dir, exist_ok=True)
    
    # Stems
    stems_dir = os.path.join(output_dir, 'stems')
    os.makedirs(stems_dir, exist_ok=True)
    for name, audio in stems.items():
        path = os.path.join(stems_dir, f'{beat_id}_{name}.wav')
        sf.write(path, audio.T, engine.sample_rate, subtype='PCM_24')
        print(f"  -> Stem: {path}")
    
    # Full mix
    mix_path = os.path.join(output_dir, f'{beat_id}_mix.wav')
    sf.write(mix_path, mix.T, engine.sample_rate, subtype='PCM_24')
    print(f"  -> Mix: {mix_path}")
    
    # Summary
    print(f"\n{'='*70}")
    print(f"  BEAT COMPLETE: {beat_id}")
    print(f"{'='*70}")
    print(f"  Genre: {genre}")
    print(f"  BPM: {bpm}")
    print(f"  Key: {key}")
    print(f"  Duration: {format_duration(mix_duration)}")
    print(f"  Structure: {structure}")
    print(f"  Stems: {len(stems)}")
    print(f"  Output: {output_dir}")
    print(f"{'='*70}\n")
    
    return beat_id


def main():
    parser = argparse.ArgumentParser(description='Generate a full commercial-length beat')
    
    # Load available genres
    spec = importlib.util.spec_from_file_location(
        'genre_library',
        os.path.join(os.path.dirname(__file__), '..', 'services', 'composition-engine', 'app', 'models', 'genre_library.py')
    )
    gl = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gl)
    all_genres = gl.get_all_genres()
    
    parser.add_argument('--genre', default='trap', choices=all_genres,
                       help=f'Genre ({len(all_genres)} available)')
    parser.add_argument('--bpm', type=int, default=140,
                       help='Tempo in BPM')
    parser.add_argument('--key', default='C',
                       help='Musical key (C, D, E, F, G, A, B)')
    parser.add_argument('--structure', default='standard', 
                       choices=['short', 'standard', 'extended'],
                       help='Song structure length')
    parser.add_argument('--output', default='./output',
                       help='Output directory')
    parser.add_argument('--list-genres', action='store_true',
                       help='List all available genres and exit')
    
    args = parser.parse_args()
    
    if args.list_genres:
        print(f"\nAvailable Genres ({len(all_genres)}):")
        print("-" * 50)
        for genre in all_genres:
            config = gl.get_genre_config(genre)
            print(f"  {genre:15s} - {config['description']}")
            print(f"  {'':15s}   BPM: {config['bpms']}, Moods: {config['moods']}")
        print()
        return
    
    generate_full_beat(args.genre, args.bpm, args.key, args.structure, args.output)


if __name__ == '__main__':
    main()
