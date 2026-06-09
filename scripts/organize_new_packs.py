"""Organize new Cymatics sample packs into the project structure.

This script sorts samples from raw pack folders into the project's
category/genre structure for use by the SampleEngine.

New packs being organized:
- 808s & Bass -> drums/808s/trap/, melodic/bass/trap/
- Drum Kit -> drums/{kicks,snares,hihats,claps}/trap/
- Drum Loops -> drums/{kicks,snares,hihats,claps}/trap/ (extracted)
- Ear Candy -> fx/, melodic/vocals/
- Hihat Loops -> drums/hihats/trap/ (extracted)
- Life Recordings -> fx/ambience/all/
- Melody Loops -> melodic/{synth_leads,synth_pads,bass,guitars,pianos}/trap/
- Percussion Loops -> drums/percs/trap/ (extracted)
- MIDI -> Keep as-is in midi/ folder
"""

import os
import shutil
import re
from pathlib import Path
from typing import Dict, List, Tuple
import structlog

logger = structlog.get_logger()

PROJECT_ROOT = Path(__file__).parent.parent
SAMPLES_DIR = PROJECT_ROOT / "samples"

# Source folders (raw packs)
PACKS = {
    "808s & Bass": SAMPLES_DIR / "808s & Bass",
    "Drum Kit": SAMPLES_DIR / "Drum Kit",
    "Drum Loops": SAMPLES_DIR / "Drum Loops",
    "Ear Candy": SAMPLES_DIR / "Ear Candy",
    "Hihat Loops & MIDI": SAMPLES_DIR / "Hihat Loops & MIDI",
    "Life Recordings": SAMPLES_DIR / "Life Recordings",
    "Melody Loops": SAMPLES_DIR / "Melody Loops",
    "Percussion Loops": SAMPLES_DIR / "Percussion Loops",
}


def parse_note_from_filename(filename: str) -> Tuple[str, str]:
    """Extract note name from filename like '808 Art Rug (C).wav'.
    
    Returns: (note_name, octave) or (None, None)
    """
    # Look for note in parentheses: (C), (C#), (F#), etc.
    match = re.search(r'\(([A-G][#b]?)\)', filename)
    if match:
        note = match.group(1)
        return note, "3"  # Default octave
    
    # Look for note at end: _C, _C#, etc.
    match = re.search(r'[_\s]([A-G][#b]?)(?:\d)?\.wav', filename)
    if match:
        note = match.group(1)
        return note, "3"
    
    return None, None


def organize_808s_and_bass():
    """Organize 808s & Bass pack."""
    source = PACKS["808s & Bass"]
    if not source.exists():
        logger.warning("source_not_found", pack="808s & Bass")
        return 0
    
    copied = 0
    
    for wav_file in source.glob("*.wav"):
        filename = wav_file.name
        
        if "808" in filename:
            # It's an 808
            dest_dir = SAMPLES_DIR / "drums" / "808s" / "trap"
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            # Try to extract note
            note, octave = parse_note_from_filename(filename)
            if note:
                dest_name = f"808_{note}.wav"
            else:
                dest_name = f"NEW_{filename}"
            
            shutil.copy2(wav_file, dest_dir / dest_name)
            copied += 1
            
        elif "Bass" in filename or "Sub" in filename:
            # It's a bass one-shot
            dest_dir = SAMPLES_DIR / "melodic" / "bass" / "trap"
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            note, octave = parse_note_from_filename(filename)
            if note:
                dest_name = f"bass_{note}.wav"
            else:
                dest_name = f"NEW_{filename}"
            
            shutil.copy2(wav_file, dest_dir / dest_name)
            copied += 1
    
    logger.info("organized_808s_and_bass", copied=copied)
    return copied


def organize_drum_kit():
    """Organize Drum Kit pack (already has subfolders)."""
    source = PACKS["Drum Kit"]
    if not source.exists():
        logger.warning("source_not_found", pack="Drum Kit")
        return 0
    
    copied = 0
    
    # Map subfolders to categories
    category_map = {
        "Claps": ("drums", "claps"),
        "Hihats": ("drums", "hihats"),
        "Kicks": ("drums", "kicks"),
        "Open Hats": ("drums", "hihats"),
        "Percs": ("drums", "percs"),
        "Rims": ("drums", "snares"),  # Rims go with snares
        "Snares": ("drums", "snares"),
    }
    
    for subfolder, (parent, category) in category_map.items():
        source_dir = source / subfolder
        if not source_dir.exists():
            continue
        
        dest_dir = SAMPLES_DIR / parent / category / "trap"
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        for wav_file in source_dir.glob("*.wav"):
            dest_name = f"NEW_{wav_file.name}"
            shutil.copy2(wav_file, dest_dir / dest_name)
            copied += 1
    
    logger.info("organized_drum_kit", copied=copied)
    return copied


def organize_ear_candy():
    """Organize Ear Candy pack (accents, phrases, textures)."""
    source = PACKS["Ear Candy"]
    if not source.exists():
        logger.warning("source_not_found", pack="Ear Candy")
        return 0
    
    copied = 0
    
    for wav_file in source.glob("*.wav"):
        filename = wav_file.name
        
        if "PHRASE" in filename:
            # Vocal phrases
            dest_dir = SAMPLES_DIR / "melodic" / "vocals" / "trap"
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest_name = f"NEW_{filename}"
            shutil.copy2(wav_file, dest_dir / dest_name)
            copied += 1
            
        elif "ACCENT" in filename or "TEXTURE" in filename:
            # FX/ambience
            dest_dir = SAMPLES_DIR / "fx" / "ambience" / "all"
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest_name = f"NEW_{filename}"
            shutil.copy2(wav_file, dest_dir / dest_name)
            copied += 1
    
    logger.info("organized_ear_candy", copied=copied)
    return copied


def organize_life_recordings():
    """Organize Life Recordings (field recordings)."""
    source = PACKS["Life Recordings"]
    if not source.exists():
        logger.warning("source_not_found", pack="Life Recordings")
        return 0
    
    copied = 0
    dest_dir = SAMPLES_DIR / "fx" / "ambience" / "all"
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    for wav_file in source.glob("*.wav"):
        dest_name = f"NEW_{wav_file.name}"
        shutil.copy2(wav_file, dest_dir / dest_name)
        copied += 1
    
    logger.info("organized_life_recordings", copied=copied)
    return copied


def organize_melody_loops():
    """Organize Melody Loops (key-labeled melodic stems)."""
    source = PACKS["Melody Loops"]
    if not source.exists():
        logger.warning("source_not_found", pack="Melody Loops")
        return 0
    
    copied = 0
    
    # These are full melodic loops - categorize by content
    for wav_file in source.glob("*.wav"):
        filename = wav_file.name
        
        # Try to determine instrument type from filename
        # Most Cymatics melody loops are synth-based unless specified
        dest_dir = SAMPLES_DIR / "melodic" / "synth_leads" / "trap"
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        dest_name = f"NEW_{filename}"
        shutil.copy2(wav_file, dest_dir / dest_name)
        copied += 1
    
    logger.info("organized_melody_loops", copied=copied)
    return copied


def organize_percussion_loops():
    """Organize Percussion Loops."""
    source = PACKS["Percussion Loops"]
    if not source.exists():
        logger.warning("source_not_found", pack="Percussion Loops")
        return 0
    
    copied = 0
    dest_dir = SAMPLES_DIR / "drums" / "percs" / "trap"
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    for wav_file in source.glob("*.wav"):
        dest_name = f"NEW_{wav_file.name}"
        shutil.copy2(wav_file, dest_dir / dest_name)
        copied += 1
    
    logger.info("organized_percussion_loops", copied=copied)
    return copied


def organize_midi():
    """Move MIDI files to dedicated folder."""
    source = SAMPLES_DIR / "MIDI"
    if not source.exists():
        return 0
    
    dest_dir = PROJECT_ROOT / "midi"
    dest_dir.mkdir(exist_ok=True)
    
    copied = 0
    for midi_file in source.glob("*.mid"):
        shutil.copy2(midi_file, dest_dir / midi_file.name)
        copied += 1
    
    logger.info("organized_midi", copied=copied)
    return copied


def update_sample_index():
    """Update the sample index JSON."""
    import json
    
    index = {
        "packs": ["Cymatics", "PML", "PULSE"],
        "categories": {},
        "total_samples": 0
    }
    
    for category_dir in [SAMPLES_DIR / "drums", SAMPLES_DIR / "melodic", SAMPLES_DIR / "fx"]:
        if not category_dir.exists():
            continue
        
        for subdir in category_dir.iterdir():
            if not subdir.is_dir():
                continue
            
            category_name = subdir.name
            index["categories"][category_name] = {}
            
            for genre_dir in subdir.iterdir():
                if not genre_dir.is_dir():
                    continue
                
                genre = genre_dir.name
                wav_files = list(genre_dir.glob("*.wav"))
                
                index["categories"][category_name][genre] = len(wav_files)
                index["total_samples"] += len(wav_files)
    
    index_path = SAMPLES_DIR / "sample_index.json"
    with open(index_path, 'w') as f:
        json.dump(index, f, indent=2)
    
    logger.info("sample_index_updated", total=index["total_samples"])
    return index


def main():
    """Run full organization."""
    print("=" * 60)
    print("THE PRODUCER -- Organize New Sample Packs")
    print("=" * 60)
    
    total_copied = 0
    
    organizers = [
        ("808s & Bass", organize_808s_and_bass),
        ("Drum Kit", organize_drum_kit),
        ("Ear Candy", organize_ear_candy),
        ("Life Recordings", organize_life_recordings),
        ("Melody Loops", organize_melody_loops),
        ("Percussion Loops", organize_percussion_loops),
        ("MIDI", organize_midi),
    ]
    
    for name, organizer in organizers:
        print(f"\n[+] Organizing {name}...")
        try:
            count = organizer()
            total_copied += count
            print(f"    Copied: {count}")
        except Exception as e:
            logger.error("organize_failed", pack=name, error=str(e))
            print(f"    ERROR: {e}")
    
    # Update index
    print("\n[+] Updating sample index...")
    index = update_sample_index()
    
    # Summary
    print("\n" + "=" * 60)
    print("ORGANIZATION COMPLETE")
    print("=" * 60)
    print(f"\nTotal samples copied: {total_copied}")
    print(f"Total samples in library: {index['total_samples']}")
    print("\nNew/updated categories:")
    for cat, genres in sorted(index["categories"].items()):
        total = sum(genres.values())
        if total > 0:
            print(f"  {cat}: {total} samples")
    print("=" * 60)


if __name__ == "__main__":
    main()
