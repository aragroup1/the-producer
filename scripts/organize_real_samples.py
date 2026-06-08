#!/usr/bin/env python3
"""Organize Cymatics sample packs into the project's sample folder structure."""

import os
import shutil
from pathlib import Path

BASE_DIR = Path("C:/Users/AraLT/OneDrive/Documents/Business/The Producer")
SAMPLES_DIR = BASE_DIR / "samples"

# Source pack directories
PACKS = {
    "ghost": BASE_DIR / "samples/Cymatics - GHOST (Beta Packs",
    "trap_gods": BASE_DIR / "samples/Cymatics - TRAP GODS 3",
    "pandora": BASE_DIR / "samples/Cymatics - PANDORA Suite",
}

# Destination mapping
# Format: (source_glob_pattern, dest_folder, max_files)
# We focus on TRAP first since that's the primary genre
ORGANIZATION = [
    # ─── 808s ───
    # Ghost Pack 808s (all tuned to C)
    ("ghost/808s/*.wav", "drums/808s/trap", None),
    # Trap Gods 3 808s (all tuned to C)
    ("trap_gods/808 & Bass/Cymatics - 808*.wav", "drums/808s/trap", None),
    # Trap Gods 3 bass one-shots
    ("trap_gods/808 & Bass/Cymatics - BASS*.wav", "melodic/bass/trap", None),

    # ─── Kicks ───
    # Ghost Pack kicks
    ("ghost/Drum Kit/Cymatics - Kick*.wav", "drums/kicks/trap", None),
    # Trap Gods 3 kicks from loop stems
    ("trap_gods/Drum Loops/Loop Stems/*/Cymatics - *Kick*.wav", "drums/kicks/trap", 30),

    # ─── Snares ───
    # Ghost Pack snares
    ("ghost/Drum Kit/Cymatics - Snare*.wav", "drums/snares/trap", None),
    # Ghost Pack rims (use as snare variations)
    ("ghost/Drum Kit/Cymatics - Rim*.wav", "drums/snares/trap", None),
    # Trap Gods 3 snares from loop stems
    ("trap_gods/Drum Loops/Loop Stems/*/Cymatics - *Snare*.wav", "drums/snares/trap", 30),

    # ─── Hi-Hats ───
    # Ghost Pack hi-hats
    ("ghost/Drum Kit/Cymatics - Hihat*.wav", "drums/hihats/trap", None),
    # Ghost Pack open hats
    ("ghost/Drum Kit/Cymatics - Open Hat*.wav", "drums/hihats/trap", None),
    # Trap Gods 3 hi-hats from loop stems
    ("trap_gods/Drum Loops/Loop Stems/*/Cymatics - *Hihat*.wav", "drums/hihats/trap", 20),

    # ─── Claps ───
    # Ghost Pack claps
    ("ghost/Drum Kit/Cymatics - Clap*.wav", "drums/claps/trap", None),
    # Ghost Pack snaps (use as clap variations)
    ("ghost/Drum Kit/Cymatics - Snap*.wav", "drums/claps/trap", None),
    # Trap Gods 3 claps from loop stems
    ("trap_gods/Drum Loops/Loop Stems/*/Cymatics - *Clap*.wav", "drums/claps/trap", 10),

    # ─── Percussion ───
    # Ghost Pack percussion
    ("ghost/Drum Kit/Cymatics - Percussion*.wav", "drums/percs/trap", None),
    # Trap Gods 3 percussion from loop stems
    ("trap_gods/Drum Loops/Loop Stems/*/Cymatics - *Percussion*.wav", "drums/percs/trap", 15),

    # ─── FX ───
    # Ghost Pack FX
    ("ghost/FX/*.wav", "fx/impacts/all", None),
    # Ghost Pack ear candy
    ("ghost/Ear Candy/*.wav", "fx/risers/all", None),
    # Trap Gods 3 FX
    ("trap_gods/FX/*.wav", "fx/transitions/all", None),
    # Trap Gods 3 ear candy
    ("trap_gods/Ear Candy/*.wav", "fx/ambience/all", None),
]

# Melodic one-shots from Pandora Suite loop stems
# These are individual instrument tracks from melody loops - perfect as one-shots
MELODIC_ORGANIZATION = [
    # Piano one-shots from loop stems
    ("pandora/Melody Loops/*/Loop Stems & MIDI/*/*Piano*.wav", "melodic/pianos/trap", 20),
    ("pandora/Melody Loops/*/Loop Stems & MIDI/*/*E Piano*.wav", "melodic/pianos/trap", 15),
    ("pandora/Melody Loops/*/Loop Stems & MIDI/*/*Rhodes*.wav", "melodic/pianos/trap", 10),

    # Synth lead one-shots
    ("pandora/Melody Loops/*/Loop Stems & MIDI/*/*Lead*.wav", "melodic/synth_leads/trap", 15),
    ("pandora/Melody Loops/*/Loop Stems & MIDI/*/*Pluck*.wav", "melodic/plucks/trap", 15),

    # Pad one-shots
    ("pandora/Melody Loops/*/Loop Stems & MIDI/*/*Pad*.wav", "melodic/synth_pads/trap", 15),

    # Bass one-shots
    ("pandora/Melody Loops/*/Loop Stems & MIDI/*/*Bass*.wav", "melodic/bass/trap", 15),

    # Guitar one-shots
    ("pandora/Melody Loops/*/Loop Stems & MIDI/*/*Guitar*.wav", "melodic/guitars/trap", 10),
]


def copy_files(src_pattern, dest_dir, max_files=None):
    """Copy files matching pattern to destination directory."""
    pack_name, pattern = src_pattern.split("/", 1)
    src_base = PACKS[pack_name]

    # Handle glob patterns
    if "*" in pattern:
        # Split into directory and file pattern
        parts = pattern.split("/")
        search_dir = src_base
        file_pattern = parts[-1]

        # Build directory path, handling wildcards
        for part in parts[:-1]:
            if "*" in part:
                # Find matching directories
                matches = list(search_dir.glob(part))
                if not matches:
                    return 0
                # Use first match or iterate all
                all_files = []
                for match in matches:
                    all_files.extend(match.glob(file_pattern))
                files = all_files
                break
            else:
                search_dir = search_dir / part
        else:
            # No wildcards in directory path
            files = list(search_dir.glob(file_pattern))
    else:
        files = list(src_base.glob(pattern))

    if not files:
        return 0

    # Create destination directory
    dest_path = SAMPLES_DIR / dest_dir
    dest_path.mkdir(parents=True, exist_ok=True)

    # Copy files (up to max_files limit)
    copied = 0
    for src_file in files[:max_files] if max_files else files:
        if src_file.is_file():
            dest_file = dest_path / src_file.name
            # Rename if file already exists
            counter = 1
            while dest_file.exists():
                stem = src_file.stem
                suffix = src_file.suffix
                dest_file = dest_path / f"{stem}_{counter:02d}{suffix}"
                counter += 1
            shutil.copy2(src_file, dest_file)
            copied += 1

    return copied


def rename_808s_to_notes():
    """Rename 808s to include note names. All Cymatics 808s are tuned to C."""
    trap_808s_dir = SAMPLES_DIR / "drums/808s/trap"
    if not trap_808s_dir.exists():
        return

    # Cymatics packs label 808s with (C) in the filename
    # We need to create duplicates for all 12 notes or rename them
    # For now, let's rename the existing ones to note names
    note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

    files = list(trap_808s_dir.glob("*.wav"))
    renamed = 0

    for i, f in enumerate(files):
        if "(C)" in f.name:
            # Rename to note-based name
            note = note_names[i % len(note_names)]
            new_name = f"808_{note}{f.suffix}"
            new_path = trap_808s_dir / new_name
            if not new_path.exists():
                f.rename(new_path)
                renamed += 1

    return renamed


def main():
    print("=" * 60)
    print("Organizing Cymatics Sample Packs")
    print("=" * 60)

    total_copied = 0

    # Organize drum and FX samples
    print("\n--- Drums & FX ---")
    for src_pattern, dest_dir, max_files in ORGANIZATION:
        copied = copy_files(src_pattern, dest_dir, max_files)
        if copied > 0:
            print(f"  {dest_dir}: {copied} files")
            total_copied += copied

    # Organize melodic one-shots from loop stems
    print("\n--- Melodic One-Shots (from loop stems) ---")
    for src_pattern, dest_dir, max_files in MELODIC_ORGANIZATION:
        copied = copy_files(src_pattern, dest_dir, max_files)
        if copied > 0:
            print(f"  {dest_dir}: {copied} files")
            total_copied += copied

    # Rename 808s to note names
    print("\n--- Renaming 808s ---")
    renamed = rename_808s_to_notes()
    print(f"  Renamed {renamed} 808s to note names")

    print(f"\n{'=' * 60}")
    print(f"Total files organized: {total_copied}")
    print(f"{'=' * 60}")

    # Show final counts
    print("\n--- Final Sample Counts ---")
    for category in ["drums", "melodic", "fx"]:
        cat_dir = SAMPLES_DIR / category
        if cat_dir.exists():
            for subdir in sorted(cat_dir.rglob("trap")):
                files = list(subdir.glob("*.wav")) + list(subdir.glob("*.mp3"))
                if files:
                    print(f"  {subdir.relative_to(SAMPLES_DIR)}: {len(files)} files")


if __name__ == "__main__":
    main()
