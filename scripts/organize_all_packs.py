"""Organize ALL new Cymatics sample packs into project structure.

Handles multiple pack drops with smart categorization.
"""

import os
import shutil
import re
from pathlib import Path
from typing import Tuple
import structlog

logger = structlog.get_logger()

PROJECT_ROOT = Path(__file__).parent.parent
SAMPLES_DIR = PROJECT_ROOT / "samples"


def parse_note(filename: str) -> Tuple[str, str]:
    """Extract note from filename like '808 Art Rug (C).wav'."""
    match = re.search(r'\(([A-G][#b]?)\)', filename)
    if match:
        return match.group(1), "3"
    match = re.search(r'[_\s]([A-G][#b]?)(?:\d)?\.wav', filename)
    if match:
        return match.group(1), "3"
    return None, None


def copy_with_prefix(src: Path, dest_dir: Path, prefix: str = "NEW") -> int:
    """Copy WAV file with prefix to avoid overwrites."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_name = f"{prefix}_{src.name}"
    if not (dest_dir / dest_name).exists():
        shutil.copy2(src, dest_dir / dest_name)
        return 1
    return 0


def organize_808s_bass() -> int:
    """808s & Bass -> drums/808s/trap/ + melodic/bass/trap/"""
    source = SAMPLES_DIR / "808s & Bass"
    if not source.exists():
        return 0
    copied = 0
    for f in source.glob("*.wav"):
        if "808" in f.name:
            note, _ = parse_note(f.name)
            dest_name = f"808_{note}.wav" if note else f"NEW_{f.name}"
            dest = SAMPLES_DIR / "drums" / "808s" / "trap" / dest_name
            if not dest.exists():
                shutil.copy2(f, dest)
                copied += 1
        elif "Bass" in f.name or "Sub" in f.name:
            copied += copy_with_prefix(f, SAMPLES_DIR / "melodic" / "bass" / "trap")
    logger.info("organized_808s_bass", copied=copied)
    return copied


def organize_drum_accents() -> int:
    """Drum Accents -> fx/impacts/all/ + fx/transitions/all/"""
    source = SAMPLES_DIR / "Drum Accents"
    if not source.exists():
        return 0
    copied = 0
    for f in source.glob("*.wav"):
        if any(x in f.name for x in ["Impact", "Hit", "Crash", "Clap"]):
            copied += copy_with_prefix(f, SAMPLES_DIR / "fx" / "impacts" / "all")
        else:
            copied += copy_with_prefix(f, SAMPLES_DIR / "fx" / "transitions" / "all")
    logger.info("organized_drum_accents", copied=copied)
    return copied


def organize_drum_kit() -> int:
    """Drum Kit -> drums/{category}/trap/"""
    source = SAMPLES_DIR / "Drum Kit"
    if not source.exists():
        return 0
    
    mapping = {
        "Claps": "claps", "Hihats": "hihats", "Kicks": "kicks",
        "Open Hats": "hihats", "Percussion": "percs", "Rims": "snares",
        "Snaps": "claps", "Snares": "snares"
    }
    copied = 0
    for subfolder, category in mapping.items():
        src_dir = source / subfolder
        if src_dir.exists():
            for f in src_dir.glob("*.wav"):
                copied += copy_with_prefix(f, SAMPLES_DIR / "drums" / category / "trap")
    logger.info("organized_drum_kit", copied=copied)
    return copied


def organize_drum_kits() -> int:
    """Drum Kits (RnB/Trap/Vintage) -> drums/{category}/{genre}/"""
    source = SAMPLES_DIR / "Drum Kits"
    if not source.exists():
        return 0
    
    genre_map = {"RnB": "rnb", "Trap": "trap", "Vintage": "boom_bap"}
    copied = 0
    
    for genre_folder, genre in genre_map.items():
        src = source / genre_folder
        if not src.exists():
            continue
        for f in src.rglob("*.wav"):
            # Determine category from filename
            name = f.name.lower()
            if "kick" in name:
                cat = "kicks"
            elif "snare" in name or "rim" in name:
                cat = "snares"
            elif "hat" in name or "cymbal" in name:
                cat = "hihats"
            elif "clap" in name or "snap" in name:
                cat = "claps"
            elif "perc" in name or "tom" in name:
                cat = "percs"
            elif "808" in name:
                cat = "808s"
            else:
                cat = "percs"  # Default
            
            copied += copy_with_prefix(f, SAMPLES_DIR / "drums" / cat / genre)
    
    logger.info("organized_drum_kits", copied=copied)
    return copied


def organize_drum_loops() -> int:
    """Drum Loops -> drums/{category}/trap/ (extracted one-shots from stems)"""
    source = SAMPLES_DIR / "Drum Loops"
    if not source.exists():
        return 0
    
    copied = 0
    # Copy full loops to drums/percs/trap/ for now
    # Extracted stems go to their respective categories
    for f in source.rglob("*.wav"):
        path_str = str(f).lower()
        
        if "stem" in path_str or "kick" in f.name.lower():
            copied += copy_with_prefix(f, SAMPLES_DIR / "drums" / "kicks" / "trap")
        elif "snare" in f.name.lower() or "clap" in f.name.lower():
            copied += copy_with_prefix(f, SAMPLES_DIR / "drums" / "snares" / "trap")
        elif "hat" in f.name.lower():
            copied += copy_with_prefix(f, SAMPLES_DIR / "drums" / "hihats" / "trap")
        elif "perc" in f.name.lower():
            copied += copy_with_prefix(f, SAMPLES_DIR / "drums" / "percs" / "trap")
        else:
            # Full drum loops -> percs for now
            copied += copy_with_prefix(f, SAMPLES_DIR / "drums" / "percs" / "trap")
    
    logger.info("organized_drum_loops", copied=copied)
    return copied


def organize_ear_candy() -> int:
    """Ear Candy -> fx/ + melodic/vocals/"""
    source = SAMPLES_DIR / "Ear Candy"
    if not source.exists():
        return 0
    
    copied = 0
    for f in source.glob("*.wav"):
        if "PHRASE" in f.name or "Vocal" in f.name:
            copied += copy_with_prefix(f, SAMPLES_DIR / "melodic" / "vocals" / "trap")
        elif "ACCENT" in f.name:
            copied += copy_with_prefix(f, SAMPLES_DIR / "fx" / "ambience" / "all")
        else:
            copied += copy_with_prefix(f, SAMPLES_DIR / "fx" / "transitions" / "all")
    
    logger.info("organized_ear_candy", copied=copied)
    return copied


def organize_hihat_loops() -> int:
    """Hihat Loops -> drums/hihats/{genre}/"""
    source = SAMPLES_DIR / "Hihat Loops & MIDI"
    if not source.exists():
        return 0
    
    copied = 0
    genre_map = {"Live": "trap", "RnB": "rnb", "Trap": "trap"}
    
    for folder, genre in genre_map.items():
        src = source / folder
        if src.exists():
            for f in src.rglob("*.wav"):
                copied += copy_with_prefix(f, SAMPLES_DIR / "drums" / "hihats" / genre)
    
    logger.info("organized_hihat_loops", copied=copied)
    return copied


def organize_life_recordings() -> int:
    """Life Recordings -> fx/ambience/all/"""
    source = SAMPLES_DIR / "Life Recordings"
    if not source.exists():
        return 0
    copied = 0
    for f in source.glob("*.wav"):
        copied += copy_with_prefix(f, SAMPLES_DIR / "fx" / "ambience" / "all")
    logger.info("organized_life_recordings", copied=copied)
    return copied


def organize_melody_loops() -> int:
    """Melody Loops -> melodic/{category}/trap/"""
    source = SAMPLES_DIR / "Melody Loops"
    if not source.exists():
        return 0
    
    copied = 0
    for f in source.glob("*.wav"):
        name = f.name.lower()
        
        # Try to determine instrument type
        if any(x in name for x in ["guitar", "pluck", "strum"]):
            cat = "guitars"
        elif any(x in name for x in ["piano", "keys", "rhodes"]):
            cat = "pianos"
        elif any(x in name for x in ["pad", "ambient", "atmo"]):
            cat = "synth_pads"
        elif any(x in name for x in ["bass", "808", "sub"]):
            cat = "bass"
        elif any(x in name for x in ["flute", "wind", "pipe"]):
            cat = "flutes"
        elif any(x in name for x in ["vocal", "voice", "choir"]):
            cat = "vocals"
        else:
            cat = "synth_leads"  # Default for melodic loops
        
        copied += copy_with_prefix(f, SAMPLES_DIR / "melodic" / cat / "trap")
    
    logger.info("organized_melody_loops", copied=copied)
    return copied


def organize_percussion() -> int:
    """Percussion Loops + Wet Percussion -> drums/percs/trap/"""
    copied = 0
    for pack_name in ["Percussion Loops", "Wet Percussion"]:
        source = SAMPLES_DIR / pack_name
        if source.exists():
            for f in source.rglob("*.wav"):
                copied += copy_with_prefix(f, SAMPLES_DIR / "drums" / "percs" / "trap")
    logger.info("organized_percussion", copied=copied)
    return copied


def organize_midi() -> int:
    """MIDI -> midi/ folder"""
    source = SAMPLES_DIR / "MIDI"
    if not source.exists():
        return 0
    
    dest = PROJECT_ROOT / "midi"
    dest.mkdir(exist_ok=True)
    copied = 0
    
    for f in source.rglob("*.mid"):
        if not (dest / f.name).exists():
            shutil.copy2(f, dest / f.name)
            copied += 1
    
    logger.info("organized_midi", copied=copied)
    return copied


def update_index():
    """Update sample index."""
    import json
    index = {"categories": {}, "total_samples": 0}
    
    for parent in [SAMPLES_DIR / "drums", SAMPLES_DIR / "melodic", SAMPLES_DIR / "fx"]:
        if not parent.exists():
            continue
        for subdir in parent.iterdir():
            if not subdir.is_dir():
                continue
            cat_name = subdir.name
            index["categories"][cat_name] = {}
            for genre_dir in subdir.iterdir():
                if not genre_dir.is_dir():
                    continue
                wavs = list(genre_dir.glob("*.wav"))
                index["categories"][cat_name][genre_dir.name] = len(wavs)
                index["total_samples"] += len(wavs)
    
    with open(SAMPLES_DIR / "sample_index.json", 'w') as f:
        json.dump(index, f, indent=2)
    
    return index


def main():
    print("=" * 60)
    print("THE PRODUCER -- Organize All Sample Packs")
    print("=" * 60)
    
    organizers = [
        ("808s & Bass", organize_808s_bass),
        ("Drum Accents", organize_drum_accents),
        ("Drum Kit", organize_drum_kit),
        ("Drum Kits", organize_drum_kits),
        ("Drum Loops", organize_drum_loops),
        ("Ear Candy", organize_ear_candy),
        ("Hihat Loops", organize_hihat_loops),
        ("Life Recordings", organize_life_recordings),
        ("Melody Loops", organize_melody_loops),
        ("Percussion", organize_percussion),
        ("MIDI", organize_midi),
    ]
    
    total = 0
    for name, func in organizers:
        print(f"\n[+] {name}...")
        try:
            count = func()
            total += count
            print(f"    Copied: {count}")
        except Exception as e:
            print(f"    ERROR: {e}")
    
    print("\n[+] Updating index...")
    index = update_index()
    
    print("\n" + "=" * 60)
    print(f"DONE: {total} files organized")
    print(f"Total library: {index['total_samples']} samples")
    print("=" * 60)


if __name__ == "__main__":
    main()
