"""Export Spitfire BBC Symphony Orchestra patches as one-shot WAV samples.

This script uses Windows Stereo Mix (loopback recording) to capture audio
from the Spitfire Audio plugin while it plays MIDI notes. The captured audio
is then trimmed and saved as one-shot WAV files for use in The Producer.

Requirements:
- Spitfire Audio app installed and working
- Windows Stereo Mix enabled (or virtual audio cable)
- Spitfire BBC SO loaded in standalone or DAW

Usage:
1. Open Spitfire Audio app
2. Load BBC Symphony Orchestra - Discover
3. Select an instrument (e.g., Violins 1 - Long)
4. Run this script
5. It will play each note and capture the audio
"""

import os
import sys
import time
import structlog
import numpy as np
import sounddevice as sd
import soundfile as sf
from pathlib import Path
from typing import List, Optional, Dict
from dataclasses import dataclass

logger = structlog.get_logger()

# Configuration
SAMPLE_RATE = 44100
CAPTURE_DURATION = 4.0  # Seconds per note (long for orchestral sounds)
NOTE_VELOCITY = 100
SILENCE_THRESHOLD = 0.001
STEREO_MIX_DEVICE = None  # Will auto-detect

# Notes to sample (C2 to C6 covers full orchestral range)
NOTES_TO_SAMPLE = [36, 48, 60, 72, 84]  # C2, C3, C4, C5, C6
NOTE_NAMES = {36: "C2", 48: "C3", 60: "C4", 72: "C5", 84: "C6"}

# MIDI note to frequency
NOTE_FREQS = {
    36: 65.41, 48: 130.81, 60: 261.63, 72: 523.25, 84: 1046.50
}


@dataclass
class SpitfireInstrument:
    """Represents a Spitfire instrument to sample."""
    name: str
    category: str  # strings, brass, woodwinds, percussion
    section: str   # violins, celli, trumpets, etc.
    articulation: str  # long, short, legato, etc.
    recommended_notes: List[int]  # Which notes to sample
    

# Define instruments to export from BBC SO Discover
BBC_SO_INSTRUMENTS = [
    # STRINGS
    SpitfireInstrument("Violins 1 Long", "strings", "violins", "long", [60, 72, 84]),
    SpitfireInstrument("Violins 1 Legato", "strings", "violins", "legato", [60, 72, 84]),
    SpitfireInstrument("Violins 1 Short", "strings", "violins", "short", [60, 72, 84]),
    SpitfireInstrument("Violins 1 Pizzicato", "strings", "violins", "pizzicato", [60, 72, 84]),
    SpitfireInstrument("Violins 2 Long", "strings", "violins", "long", [60, 72, 84]),
    SpitfireInstrument("Violas Long", "strings", "violas", "long", [48, 60, 72]),
    SpitfireInstrument("Celli Long", "strings", "celli", "long", [36, 48, 60]),
    SpitfireInstrument("Celli Legato", "strings", "celli", "legato", [36, 48, 60]),
    SpitfireInstrument("Basses Long", "strings", "basses", "long", [36, 48]),
    
    # BRASS
    SpitfireInstrument("Trumpet Long", "brass", "trumpet", "long", [60, 72]),
    SpitfireInstrument("Trumpet Short", "brass", "trumpet", "short", [60, 72]),
    SpitfireInstrument("Horns Long", "brass", "horns", "long", [48, 60]),
    SpitfireInstrument("Horns Legato", "brass", "horns", "legato", [48, 60]),
    SpitfireInstrument("Trombone Long", "brass", "trombone", "long", [36, 48, 60]),
    SpitfireInstrument("Tuba Long", "brass", "tuba", "long", [36, 48]),
    
    # WOODWINDS
    SpitfireInstrument("Flute Long", "woodwinds", "flute", "long", [72, 84]),
    SpitfireInstrument("Flute Legato", "woodwinds", "flute", "legato", [72, 84]),
    SpitfireInstrument("Oboe Long", "woodwinds", "oboe", "long", [60, 72]),
    SpitfireInstrument("Clarinet Long", "woodwinds", "clarinet", "long", [48, 60, 72]),
    SpitfireInstrument("Bassoon Long", "woodwinds", "bassoon", "long", [36, 48, 60]),
    
    # PERCUSSION
    SpitfireInstrument("Timpani Hits", "percussion", "timpani", "hits", [36, 48]),
    SpitfireInstrument("Cymbal Crash", "percussion", "cymbal", "crash", [60]),
    SpitfireInstrument("Snare Drum", "percussion", "snare", "hits", [60]),
]


def find_stereo_mix_device() -> Optional[int]:
    """Find the Stereo Mix (loopback) input device."""
    devices = sd.query_devices()
    
    for i, dev in enumerate(devices):
        if 'Stereo Mix' in dev['name'] and dev['max_input_channels'] > 0:
            logger.info("found_stereo_mix", device_index=i, name=dev['name'])
            return i
    
    # Also check for other loopback/virtual devices
    for i, dev in enumerate(devices):
        name = dev['name'].lower()
        if any(x in name for x in ['loopback', 'virtual', 'cable', 'what u hear']) and dev['max_input_channels'] > 0:
            logger.info("found_loopback_device", device_index=i, name=dev['name'])
            return i
    
    logger.error("no_stereo_mix_found")
    print("\n" + "=" * 60)
    print("ERROR: Stereo Mix not found!")
    print("=" * 60)
    print("\nTo enable Stereo Mix in Windows:")
    print("  1. Right-click speaker icon in taskbar -> Sounds")
    print("  2. Go to 'Recording' tab")
    print("  3. Right-click in empty area -> 'Show Disabled Devices'")
    print("  4. Find 'Stereo Mix' -> Right-click -> 'Enable'")
    print("  5. Right-click 'Stereo Mix' -> 'Set as Default Device'")
    print("\nAlternative: Use a virtual audio cable like VB-Cable")
    print("=" * 60)
    return None


def capture_audio(duration: float, device_index: int) -> np.ndarray:
    """Capture audio from Stereo Mix (loopback)."""
    samples = int(duration * SAMPLE_RATE)
    
    logger.info("capturing_audio", duration=duration, samples=samples)
    
    recording = sd.rec(
        samples,
        samplerate=SAMPLE_RATE,
        channels=2,
        dtype=np.float32,
        device=device_index
    )
    
    sd.wait()
    
    return recording


def trim_silence(audio: np.ndarray, threshold: float = SILENCE_THRESHOLD,
                 padding_samples: int = int(0.1 * SAMPLE_RATE)) -> np.ndarray:
    """Trim silence from start and end of audio."""
    # Calculate RMS per block
    block_size = 1024
    blocks = len(audio) // block_size
    
    rms_values = []
    for i in range(blocks):
        block = audio[i * block_size:(i + 1) * block_size]
        rms = np.sqrt(np.mean(block ** 2))
        rms_values.append(rms)
    
    rms_values = np.array(rms_values)
    
    # Find first and last blocks above threshold
    above_threshold = rms_values > threshold
    
    if not np.any(above_threshold):
        return audio  # No sound found, return original
    
    first_block = np.argmax(above_threshold)
    last_block = len(above_threshold) - np.argmax(above_threshold[::-1]) - 1
    
    # Convert block indices to sample indices
    start_sample = max(0, first_block * block_size - padding_samples)
    end_sample = min(len(audio), (last_block + 1) * block_size + padding_samples)
    
    return audio[start_sample:end_sample]


def normalize_audio(audio: np.ndarray, target_peak: float = 0.9) -> np.ndarray:
    """Normalize audio to target peak level."""
    peak = np.max(np.abs(audio))
    if peak > 0:
        audio = audio * (target_peak / peak)
    return audio


def export_instrument(instrument: SpitfireInstrument, 
                      output_base: Path,
                      stereo_mix_device: int,
                      genre: str = "all") -> List[Path]:
    """Export a single instrument as one-shot WAVs.
    
    Args:
        instrument: Instrument definition
        output_base: Base output directory
        stereo_mix_device: Index of Stereo Mix input device
        genre: Genre folder name
    
    Returns:
        List of exported file paths
    """
    # Create output directory
    output_dir = output_base / "melodic" / instrument.category / genre
    output_dir.mkdir(parents=True, exist_ok=True)
    
    exported_files = []
    
    print(f"\n{'='*60}")
    print(f"Exporting: {instrument.name}")
    print(f"Category: {instrument.category}")
    print(f"{'='*60}")
    
    for midi_note in instrument.recommended_notes:
        note_name = NOTE_NAMES.get(midi_note, f"Note_{midi_note}")
        freq = NOTE_FREQS.get(midi_note, 440)
        
        # Generate filename
        safe_name = instrument.name.replace(" ", "_").replace("&", "and")
        filename = f"BBC_{safe_name}_{note_name}.wav"
        output_path = output_dir / filename
        
        if output_path.exists():
            print(f"  Skipping {filename} (already exists)")
            exported_files.append(output_path)
            continue
        
        print(f"\n  Note: {note_name} (MIDI {midi_note}, {freq:.1f} Hz)")
        print(f"  File: {filename}")
        print(f"  INSTRUCTIONS:")
        print(f"    1. In Spitfire, select: {instrument.name}")
        print(f"    2. Play MIDI note {midi_note} ({note_name})")
        print(f"    3. Press ENTER to start capture...")
        
        input("    > ")
        
        # Capture audio
        print(f"    Capturing {CAPTURE_DURATION}s...")
        audio = capture_audio(CAPTURE_DURATION, stereo_mix_device)
        
        # Process
        print(f"    Trimming silence...")
        audio = trim_silence(audio)
        
        if len(audio) < SAMPLE_RATE * 0.1:  # Less than 100ms
            print(f"    WARNING: Audio too short ({len(audio)/SAMPLE_RATE:.2f}s)")
            print(f"    Retrying...")
            audio = capture_audio(CAPTURE_DURATION, stereo_mix_device)
            audio = trim_silence(audio)
        
        print(f"    Normalizing...")
        audio = normalize_audio(audio)
        
        # Save
        sf.write(output_path, audio, SAMPLE_RATE)
        
        duration = len(audio) / SAMPLE_RATE
        peak = np.max(np.abs(audio))
        print(f"    Saved: {output_path}")
        print(f"    Duration: {duration:.2f}s, Peak: {peak:.3f}")
        
        exported_files.append(output_path)
        
        # Small pause between notes
        time.sleep(0.5)
    
    return exported_files


def export_all_instruments(output_base: Optional[Path] = None,
                           instruments: Optional[List[SpitfireInstrument]] = None):
    """Export all defined instruments.
    
    Args:
        output_base: Base directory for output (default: project samples/)
        instruments: List of instruments to export (default: all BBC SO)
    """
    if output_base is None:
        output_base = Path(__file__).parent.parent / "samples"
    
    if instruments is None:
        instruments = BBC_SO_INSTRUMENTS
    
    # Find Stereo Mix
    stereo_mix = find_stereo_mix_device()
    if stereo_mix is None:
        return
    
    print("\n" + "=" * 60)
    print("SPITFIRE SAMPLE EXPORTER")
    print("=" * 60)
    print(f"\nStereo Mix device: [{stereo_mix}]")
    print(f"Output directory: {output_base}")
    print(f"Instruments to export: {len(instruments)}")
    print(f"\nIMPORTANT:")
    print("  - Open Spitfire Audio app")
    print("  - Load BBC Symphony Orchestra")
    print("  - Make sure audio is playing through your speakers")
    print("  - Stereo Mix will capture the speaker output")
    print("=" * 60)
    
    input("\nPress ENTER when ready...")
    
    all_exported = []
    
    for instrument in instruments:
        try:
            files = export_instrument(instrument, output_base, stereo_mix)
            all_exported.extend(files)
        except KeyboardInterrupt:
            print("\n\nExport interrupted by user.")
            break
        except Exception as e:
            logger.error("export_failed", instrument=instrument.name, error=str(e))
            print(f"\nERROR exporting {instrument.name}: {e}")
            continue
    
    # Summary
    print("\n" + "=" * 60)
    print("EXPORT COMPLETE")
    print("=" * 60)
    print(f"\nTotal files exported: {len(all_exported)}")
    print(f"\nNew categories created:")
    categories = set()
    for f in all_exported:
        cat = f.parent.parent.name
        categories.add(cat)
    for cat in sorted(categories):
        print(f"  - melodic/{cat}/all/")
    print("\nThese samples can now be used by The Producer engine!")
    print("=" * 60)


def quick_export_preset():
    """Quick export of most useful orchestral samples for trap."""
    # Select only the most useful instruments for trap production
    trap_essentials = [
        SpitfireInstrument("Violins 1 Long", "strings", "violins", "long", [60, 72]),
        SpitfireInstrument("Violins 1 Legato", "strings", "violins", "legato", [60, 72]),
        SpitfireInstrument("Celli Long", "strings", "celli", "long", [48, 60]),
        SpitfireInstrument("Celli Legato", "strings", "celli", "legato", [48, 60]),
        SpitfireInstrument("Basses Long", "strings", "basses", "long", [36, 48]),
        SpitfireInstrument("Horns Long", "brass", "horns", "long", [48, 60]),
        SpitfireInstrument("Trumpet Long", "brass", "trumpet", "long", [60]),
        SpitfireInstrument("Flute Long", "woodwinds", "flute", "long", [72]),
    ]
    
    export_all_instruments(instruments=trap_essentials)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Export Spitfire BBC SO patches as one-shot WAVs"
    )
    parser.add_argument(
        "--quick", "-q",
        action="store_true",
        help="Export only essential trap instruments (8 instruments)"
    )
    parser.add_argument(
        "--instrument", "-i",
        type=str,
        help="Export specific instrument by name"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Output directory (default: project samples/)"
    )
    
    args = parser.parse_args()
    
    if args.quick:
        quick_export_preset()
    elif args.instrument:
        # Find instrument by name
        instrument = None
        for inst in BBC_SO_INSTRUMENTS:
            if args.instrument.lower() in inst.name.lower():
                instrument = inst
                break
        
        if instrument:
            stereo_mix = find_stereo_mix_device()
            if stereo_mix:
                output_base = args.output or Path(__file__).parent.parent / "samples"
                export_instrument(instrument, output_base, stereo_mix)
        else:
            print(f"Instrument '{args.instrument}' not found.")
            print("Available instruments:")
            for inst in BBC_SO_INSTRUMENTS:
                print(f"  - {inst.name}")
    else:
        export_all_instruments(output_base=args.output)


if __name__ == "__main__":
    main()
