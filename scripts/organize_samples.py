#!/usr/bin/env python3
"""
Sample Organization Helper

This script helps you organize sample packs into the correct folder structure.
Place your downloaded sample WAV files in a 'downloads/' folder and run:

    python scripts/organize_samples.py

It will:
1. Scan all WAV files in downloads/
2. Detect instrument type from filenames (kick, snare, 808, etc.)
3. Detect genre from folder structure or filenames
4. Copy files to the correct samples/ location
5. Validate naming conventions for melodic samples

Usage:
    python scripts/organize_samples.py --source ~/Downloads/sample-packs --dry-run
    python scripts/organize_samples.py --source ~/Downloads/sample-packs
"""

import argparse
import shutil
import re
from pathlib import Path
from typing import Optional, Tuple

# Map common filename patterns to categories
CATEGORY_PATTERNS = {
    'kick': [r'kick', r'kik', r'bd'],
    'snare': [r'snare', r'snr', r'sd'],
    'hihat': [r'hat', r'hihat', r'hh', r'openhat', r'closedhat'],
    'clap': [r'clap', r'cp'],
    '808': [r'808', r'eightoheight', r'sub'],
    'perc': [r'perc', r'shaker', r'conga', r'tamb', r'cowbell', r'log_drum', r'tom'],
    'cymbals': [r'crash', r'ride', r'cymbal', r'china'],
    'synth_lead': [r'lead', r'synth', r'arp', r'saw', r'square'],
    'synth_pad': [r'pad', r'atmosphere', r'ambient'],
    'piano': [r'piano', r'rhodes', r'keys', r'epiano'],
    'bass': [r'bass(?!_drum)', r'808_bass'],
    'pluck': [r'pluck', r'mallet', r'bell', r'marimba'],
    'guitar': [r'guitar', r'string', r'nylon', r'electric'],
    'riser': [r'riser', r'build', r'uplift'],
    'impact': [r'impact', r'hit', r'smash', r'punch'],
    'transition': [r'transition', r'sweep', r'whoosh', r'fx'],
    'ambience': [r'ambience', r'ambient', r'noise', r'texture', r'vinyl'],
}

# Map folder/genre names to our genre slugs
GENRE_PATTERNS = {
    'trap': [r'trap'],
    'drill': [r'drill', r'uk_drill'],
    'boom_bap': [r'boombap', r'boom_bap', r'old_school', r'golden_era'],
    'rage': [r'rage', r'yeat', r'hyper'],
    'phonk': [r'phonk', r'memphis'],
    'jersey_club': [r'jersey', r'club'],
    'plugg': [r'plugg', r'wavy'],
    'west_coast': [r'westcoast', r'g_funk', r'gfunk'],
    'rnb': [r'rnb', r'r&b', r'rb'],
    'neo_soul': [r'neosoul', r'neo_soul', r'jazz'],
    'afrobeats': [r'afro', r'afrobeats', r'dancehall'],
    'amapiano': [r'amapiano', r'piano_log'],
    'dancehall': [r'dancehall', r'reggaeton', r'dembow'],
    'reggaeton': [r'reggaeton', r'latino', r'moombahton'],
    'hyperpop': [r'hyperpop', r'glitch', r'experimental'],
    'edm_trap': [r'edm', r'festival', r'big_room'],
    'future_bass': [r'future', r'future_bass', r'melodic_trap'],
    'lofi': [r'lofi', r'lo-fi', r'chill', r'jazzhop'],
    'ambient': [r'ambient', r'cinematic', r'film'],
}

# Note detection for melodic samples
NOTE_PATTERN = re.compile(r'[_\-]([A-G][#b]?)\d?', re.IGNORECASE)


def detect_category(filename: str) -> Optional[str]:
    """Detect sample category from filename."""
    lower = filename.lower()
    for category, patterns in CATEGORY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, lower):
                return category
    return None


def detect_genre(path: Path) -> Optional[str]:
    """Detect genre from file path or name."""
    full_path = str(path).lower().replace('\\', '/')
    for genre, patterns in GENRE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, full_path):
                return genre
    return None


def detect_note(filename: str) -> Optional[str]:
    """Detect root note from filename for melodic samples."""
    match = NOTE_PATTERN.search(filename)
    if match:
        return match.group(1).upper()
    return None


def get_target_path(category: str, genre: str, filename: str) -> Path:
    """Get the target path for a sample."""
    base = Path('samples')
    
    # Map category to directory structure
    if category in ['kick', 'snare', 'hihat', 'clap', '808', 'perc', 'cymbals']:
        parent = 'drums'
        dir_name = category + 's' if category != '808' else '808s'
        if category == 'hihat':
            dir_name = 'hihats'
        elif category == 'perc':
            dir_name = 'percs'
        return base / parent / dir_name / genre / filename
    
    elif category in ['synth_lead', 'synth_pad', 'piano', 'bass', 'pluck', 'guitar']:
        parent = 'melodic'
        dir_map = {
            'synth_lead': 'synth_leads',
            'synth_pad': 'synth_pads',
            'piano': 'pianos',
            'bass': 'bass',
            'pluck': 'plucks',
            'guitar': 'guitars',
        }
        return base / parent / dir_map[category] / genre / filename
    
    else:  # FX
        fx_map = {
            'riser': 'risers',
            'impact': 'impacts',
            'transition': 'transitions',
            'ambience': 'ambience',
        }
        return base / 'fx' / fx_map.get(category, category) / 'all' / filename


def validate_melodic_sample(filepath: Path, category: str) -> Tuple[bool, str]:
    """Validate that melodic samples have proper note naming."""
    if category in ['kick', 'snare', 'hihat', 'clap', 'perc', 'cymbals']:
        return True, "Drums don't need note names"
    
    note = detect_note(filepath.stem)
    if note:
        return True, f"Note detected: {note}"
    
    return False, "WARNING: Melodic sample missing note name (e.g., lead_C.wav, 808_F#.wav)"


def organize_samples(source_dir: str, dry_run: bool = False):
    """Organize samples from source directory."""
    source = Path(source_dir)
    if not source.exists():
        print(f"Source directory not found: {source}")
        return
    
    wav_files = list(source.rglob('*.wav')) + list(source.rglob('*.WAV'))
    print(f"Found {len(wav_files)} WAV files in {source}")
    
    stats = {'copied': 0, 'skipped': 0, 'warnings': 0, 'unknown': 0}
    
    for wav_file in wav_files:
        category = detect_category(wav_file.name)
        genre = detect_genre(wav_file)
        
        if not category:
            print(f"  [UNKNOWN] {wav_file.name} — could not detect category")
            stats['unknown'] += 1
            continue
        
        if not genre:
            genre = 'trap'  # Default genre
            print(f"  [GUESS] {wav_file.name} — defaulting to 'trap' (detected: {category})")
        
        target = get_target_path(category, genre, wav_file.name)
        
        valid, msg = validate_melodic_sample(wav_file, category)
        if not valid:
            print(f"  {msg}")
            stats['warnings'] += 1
        
        if dry_run:
            print(f"  [DRY-RUN] {wav_file.name} -> {target}")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(wav_file, target)
            print(f"  [COPIED] {wav_file.name} -> {target}")
            stats['copied'] += 1
    
    print(f"\n{'='*50}")
    print(f"Organization complete!")
    print(f"  Copied: {stats['copied']}")
    print(f"  Skipped: {stats['skipped']}")
    print(f"  Warnings: {stats['warnings']}")
    print(f"  Unknown: {stats['unknown']}")
    
    if dry_run:
        print(f"\nThis was a DRY RUN. No files were actually copied.")
        print(f"Run without --dry-run to actually organize the samples.")


def print_folder_stats():
    """Print current sample folder statistics."""
    base = Path('samples')
    if not base.exists():
        print("No samples/ folder found.")
        return
    
    print("\nCurrent Sample Library:")
    print("=" * 50)
    
    for category_dir in sorted(base.rglob('*')):
        if category_dir.is_dir():
            wav_count = len(list(category_dir.glob('*.wav')))
            if wav_count > 0:
                rel_path = category_dir.relative_to(base)
                print(f"  {rel_path}: {wav_count} files")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Organize sample packs into the correct folder structure')
    parser.add_argument('--source', default='downloads', help='Source directory with downloaded samples')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without copying')
    parser.add_argument('--stats', action='store_true', help='Show current sample folder statistics')
    
    args = parser.parse_args()
    
    if args.stats:
        print_folder_stats()
    else:
        organize_samples(args.source, args.dry_run)
