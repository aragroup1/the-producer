"""Integrate new PML and PULSE sample packs into the project structure.

This script:
1. Copies PML one-shots into the project's drums/melodic/fx folders
2. Copies PML vocal loops into a new vocals folder
3. Copies PULSE drums into the project's drums folders
4. Leaves original PML melodic loops in place (they're full loops, not one-shots)
5. Creates genre mappings for the new samples
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List
import structlog

logger = structlog.get_logger()

# Project base paths
PROJECT_ROOT = Path(__file__).parent.parent
SAMPLES_DIR = PROJECT_ROOT / "samples"
PML_PACK = SAMPLES_DIR / "PML - Melodic House - Sample Pack"
PML_VOCALS = SAMPLES_DIR / "PML - Melodic House - Bonus Vocal Pack"
PULSE_PACK = SAMPLES_DIR / "PULSE - JERSEY CLUB DRUM KIT"

# Mapping: source pattern -> (destination_category, genre_tags)
# Genre tags determine which genre folders get the samples
PML_ONE_SHOT_MAPPING = {
    # Drums
    "One Shots/Kicks": ("drums/kicks", ["house", "future_bass", "edm_trap"]),
    "One Shots/Claps": ("drums/claps", ["house", "future_bass", "edm_trap"]),
    "One Shots/Hats": ("drums/hihats", ["house", "future_bass", "edm_trap"]),
    "One Shots/Rims": ("drums/snares", ["house", "future_bass", "edm_trap"]),  # Rims go with snares
    "One Shots/Ride": ("drums/cymbals", ["house", "future_bass", "edm_trap"]),
    "One Shots/Percussions": ("drums/percs", ["house", "future_bass", "edm_trap"]),
    "One Shots/Shaker and Tambs": ("drums/percs", ["house", "future_bass", "edm_trap"]),
    
    # FX
    "One Shots/Fx": ("fx/transitions", ["all"]),
    
    # Melodic one-shots
    "One Shots/Synth One Shots": ("melodic/synth_leads", ["house", "future_bass", "edm_trap"]),
}

PML_VOCAL_MAPPING = {
    "": ("melodic/vocals", ["house", "trap", "future_bass", "all"]),
}

PULSE_DRUM_MAPPING = {
    "KICKS": ("drums/kicks", ["jersey_club", "trap", "drill"]),
    "CLAPS": ("drums/claps", ["jersey_club", "trap", "drill"]),
}


def copy_samples(source_dir: Path, dest_base: Path, mapping: Dict[str, tuple],
                 pack_prefix: str = ""):
    """Copy samples from source to destination based on mapping.
    
    Args:
        source_dir: Root directory of the pack
        dest_base: Base samples directory
        mapping: Dict of source_subdir -> (dest_category, genres)
        pack_prefix: Prefix to add to filenames (e.g., "PML_", "PULSE_")
    """
    copied = 0
    
    for source_subdir, (dest_category, genres) in mapping.items():
        source_path = source_dir / source_subdir
        
        if not source_path.exists():
            logger.warning("source_not_found", path=str(source_path))
            continue
        
        # Find all WAV files
        wav_files = list(source_path.glob("*.wav"))
        
        if not wav_files:
            logger.warning("no_wav_files", path=str(source_path))
            continue
        
        for wav_file in wav_files:
            # Copy to each genre folder
            for genre in genres:
                if genre == "all":
                    # Copy to all existing genre folders
                    dest_category_path = dest_base / dest_category
                    if dest_category_path.exists():
                        genre_dirs = [d for d in dest_category_path.iterdir() if d.is_dir()]
                        for genre_dir in genre_dirs:
                            dest_path = genre_dir / f"{pack_prefix}{wav_file.name}"
                            shutil.copy2(wav_file, dest_path)
                            copied += 1
                else:
                    dest_path = dest_base / dest_category / genre
                    dest_path.mkdir(parents=True, exist_ok=True)
                    dest_file = dest_path / f"{pack_prefix}{wav_file.name}"
                    shutil.copy2(wav_file, dest_file)
                    copied += 1
        
        logger.info("copied_samples", 
                   source=str(source_path),
                   count=len(wav_files),
                   genres=genres)
    
    return copied


def integrate_pml_one_shots():
    """Integrate PML one-shots into project structure."""
    logger.info("integrating_pml_one_shots")
    
    if not PML_PACK.exists():
        logger.error("pml_pack_not_found", path=str(PML_PACK))
        return 0
    
    copied = copy_samples(
        PML_PACK, SAMPLES_DIR, PML_ONE_SHOT_MAPPING,
        pack_prefix="PML_"
    )
    
    logger.info("pml_one_shots_complete", total_copied=copied)
    return copied


def integrate_pml_vocals():
    """Integrate PML vocal loops into project structure."""
    logger.info("integrating_pml_vocals")
    
    if not PML_VOCALS.exists():
        logger.error("pml_vocals_not_found", path=str(PML_VOCALS))
        return 0
    
    # Create vocals directory structure
    vocals_dir = SAMPLES_DIR / "melodic" / "vocals"
    
    # Find all vocal files
    vocal_files = list(PML_VOCALS.glob("*.wav"))
    
    if not vocal_files:
        logger.warning("no_vocal_files_found")
        return 0
    
    copied = 0
    for vocal_file in vocal_files:
        # Parse key from filename for organization
        # e.g., PML_MH4_Vocal_Loop_001_Shout_Dry_118BPM_Fmin_Always.wav
        key = "unknown"
        if "_Fmin" in vocal_file.name or "_F#min" in vocal_file.name:
            key = "F"
        elif "_Bmin" in vocal_file.name:
            key = "B"
        elif "_C#min" in vocal_file.name or "_C#" in vocal_file.name:
            key = "C#"
        elif "_D#min" in vocal_file.name or "_D#" in vocal_file.name:
            key = "D#"
        elif "_G#min" in vocal_file.name or "_G#" in vocal_file.name:
            key = "G#"
        elif "_Amin" in vocal_file.name:
            key = "A"
        elif "_Cmin" in vocal_file.name:
            key = "C"
        elif "_Dmin" in vocal_file.name:
            key = "D"
        elif "_Gmin" in vocal_file.name:
            key = "G"
        elif "_Emin" in vocal_file.name:
            key = "E"
        
        # Create key-labeled subdirectories
        for genre in ["house", "trap", "future_bass", "all"]:
            if genre == "all":
                dest_dir = vocals_dir / "all"
            else:
                dest_dir = vocals_dir / genre
            
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            # Add key to filename for easy identification
            dest_file = dest_dir / f"PML_{vocal_file.name}"
            shutil.copy2(vocal_file, dest_file)
            copied += 1
    
    logger.info("pml_vocals_complete", total_copied=copied, files=len(vocal_files))
    return copied


def integrate_pulse_drums():
    """Integrate PULSE Jersey Club drums into project structure."""
    logger.info("integrating_pulse_drums")
    
    if not PULSE_PACK.exists():
        logger.error("pulse_pack_not_found", path=str(PULSE_PACK))
        return 0
    
    copied = copy_samples(
        PULSE_PACK, SAMPLES_DIR, PULSE_DRUM_MAPPING,
        pack_prefix="PULSE_"
    )
    
    logger.info("pulse_drums_complete", total_copied=copied)
    return copied


def create_sample_index():
    """Create an index of all available samples for quick lookup."""
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
    
    # Save index
    import json
    index_path = PROJECT_ROOT / "samples" / "sample_index.json"
    with open(index_path, 'w') as f:
        json.dump(index, f, indent=2)
    
    logger.info("sample_index_created", 
               path=str(index_path),
               total=index["total_samples"])
    
    return index


def main():
    """Run full integration."""
    print("=" * 60)
    print("THE PRODUCER -- Sample Pack Integration")
    print("=" * 60)
    
    total_copied = 0
    
    # Integrate PML one-shots
    print("\n[1] Integrating PML Melodic House one-shots...")
    pml_one_shots = integrate_pml_one_shots()
    total_copied += pml_one_shots
    print(f"    Copied: {pml_one_shots}")
    
    # Integrate PML vocals
    print("\n[2] Integrating PML vocal loops...")
    pml_vocals = integrate_pml_vocals()
    total_copied += pml_vocals
    print(f"    Copied: {pml_vocals}")
    
    # Integrate PULSE drums
    print("\n[3] Integrating PULSE Jersey Club drums...")
    pulse_drums = integrate_pulse_drums()
    total_copied += pulse_drums
    print(f"    Copied: {pulse_drums}")
    
    # Create index
    print("\n[4] Creating sample index...")
    index = create_sample_index()
    
    # Summary
    print("\n" + "=" * 60)
    print("INTEGRATION COMPLETE")
    print("=" * 60)
    print(f"\nTotal samples copied: {total_copied}")
    print(f"Total samples in library: {index['total_samples']}")
    print("\nNew categories available:")
    print("  - melodic/vocals (house, trap, future_bass)")
    print("  - drums/kicks/jersey_club")
    print("  - drums/claps/jersey_club")
    print("  - drums/hihats/house")
    print("  - drums/percs/house")
    print("  - melodic/synth_leads/house")
    print("  - fx/transitions (noise sweeps)")
    print("\nNote: PML melodic loops left in original location")
    print("      (use as full loops or extract one-shots as needed)")
    print("=" * 60)


if __name__ == "__main__":
    main()
