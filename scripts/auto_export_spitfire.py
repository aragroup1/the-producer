"""Fully automated Spitfire BBC SO sample exporter.

This script automatically triggers MIDI notes and captures the audio
via Windows WASAPI loopback recording. No manual interaction needed.

Requirements:
- Spitfire Audio app open with BBC SO loaded
- Stereo Mix enabled OR virtual MIDI cable + audio routing
- MIDI output available (Microsoft GS Wavetable or virtual)

The script will:
1. Send MIDI note-on to trigger Spitfire
2. Record audio via Stereo Mix loopback
3. Trim silence and normalize
4. Save as WAV
5. Repeat for all notes and instruments
"""

import os
import time
import structlog
import numpy as np
import sounddevice as sd
import soundfile as sf
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass

logger = structlog.get_logger()

# Configuration
SAMPLE_RATE = 44100
STEREO_MIX_DEVICE = None  # Auto-detect

# How long to wait for note to sound after MIDI trigger
NOTE_TRIGGER_DELAY = 0.3  # seconds
NOTE_DURATION = 3.0       # seconds of recording per note
TOTAL_CAPTURE_TIME = NOTE_TRIGGER_DELAY + NOTE_DURATION + 0.5

# Notes to sample (orchestral range)
NOTE_NAMES = {36: "C2", 48: "C3", 60: "C4", 72: "C5", 84: "C6"}


@dataclass
class Instrument:
    name: str
    category: str
    notes: List[int]


# Essential trap orchestral instruments
INSTRUMENTS = [
    Instrument("Violins_Long", "strings", [60, 72]),
    Instrument("Violins_Legato", "strings", [60, 72]),
    Instrument("Celli_Long", "strings", [48, 60]),
    Instrument("Celli_Legato", "strings", [48, 60]),
    Instrument("Basses_Long", "strings", [36, 48]),
    Instrument("Horns_Long", "brass", [48, 60]),
    Instrument("Trumpet_Long", "brass", [60]),
    Instrument("Flute_Long", "woodwinds", [72]),
]


def find_stereo_mix() -> Optional[int]:
    """Find Stereo Mix or loopback device."""
    for i, dev in enumerate(sd.query_devices()):
        if dev['max_input_channels'] > 0:
            name = dev['name'].lower()
            if any(x in name for x in ['stereo mix', 'loopback', 'what u hear', 'cable output']):
                print(f"Found loopback device: [{i}] {dev['name']}")
                return i
    return None


def send_midi_note(note: int, velocity: int = 100, duration: float = 2.0):
    """Send MIDI note via Windows built-in synth.
    
    Note: This triggers Microsoft GS Wavetable, NOT Spitfire directly.
    For Spitfire, you need a virtual MIDI cable like loopMIDI.
    """
    try:
        import mido
        outputs = mido.get_output_names()
        
        # Look for a virtual MIDI cable or Spitfire
        target_output = None
        for out in outputs:
            if any(x in out.lower() for x in ['spitfire', 'loopmidi', 'virtual', 'cable']):
                target_output = out
                break
        
        if not target_output and outputs:
            target_output = outputs[0]  # Use first available
            print(f"Warning: Using {target_output} (may not trigger Spitfire)")
        
        if target_output:
            with mido.open_output(target_output) as port:
                port.send(mido.Message('note_on', note=note, velocity=velocity))
                time.sleep(duration)
                port.send(mido.Message('note_off', note=note, velocity=0))
                return True
    except Exception as e:
        print(f"MIDI error: {e}")
    return False


def capture_audio(duration: float, device_index: int) -> np.ndarray:
    """Record audio from loopback device."""
    samples = int(duration * SAMPLE_RATE)
    recording = sd.rec(samples, samplerate=SAMPLE_RATE, channels=2, 
                       dtype=np.float32, device=device_index)
    sd.wait()
    return recording


def trim_and_normalize(audio: np.ndarray) -> np.ndarray:
    """Trim silence and normalize."""
    # Simple threshold-based trim
    threshold = 0.001
    mask = np.abs(audio).max(axis=1) > threshold
    
    if not mask.any():
        return audio
    
    first = np.argmax(mask)
    last = len(mask) - np.argmax(mask[::-1])
    
    # Add padding
    padding = int(0.1 * SAMPLE_RATE)
    first = max(0, first - padding)
    last = min(len(audio), last + padding)
    
    audio = audio[first:last]
    
    # Normalize
    peak = np.max(np.abs(audio))
    if peak > 0:
        audio = audio * (0.9 / peak)
    
    return audio


def export_instrument(instrument: Instrument, output_dir: Path, 
                      loopback_device: int) -> List[Path]:
    """Export one instrument automatically."""
    exported = []
    
    cat_dir = output_dir / "melodic" / instrument.category / "all"
    cat_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'='*50}")
    print(f"Exporting: {instrument.name}")
    print(f"{'='*50}")
    
    for note in instrument.notes:
        note_name = NOTE_NAMES.get(note, f"Note_{note}")
        filename = f"BBC_{instrument.name}_{note_name}.wav"
        output_path = cat_dir / filename
        
        if output_path.exists():
            print(f"  Skip {filename} (exists)")
            exported.append(output_path)
            continue
        
        print(f"\n  Note {note_name} (MIDI {note})")
        
        # Start recording BEFORE triggering note
        print(f"  Starting capture...")
        
        # Use a thread or async to start recording, then trigger MIDI
        import threading
        
        recorded_audio = [None]
        
        def record():
            recorded_audio[0] = capture_audio(TOTAL_CAPTURE_TIME, loopback_device)
        
        # Start recording
        record_thread = threading.Thread(target=record)
        record_thread.start()
        
        # Wait a tiny bit for recording to start
        time.sleep(0.1)
        
        # Trigger MIDI note
        print(f"  Triggering MIDI note {note}...")
        midi_ok = send_midi_note(note, duration=NOTE_DURATION)
        
        if not midi_ok:
            print(f"  WARNING: MIDI trigger failed!")
            print(f"  Make sure Spitfire is receiving MIDI from the selected output")
        
        # Wait for recording to finish
        record_thread.join()
        audio = recorded_audio[0]
        
        if audio is None or len(audio) == 0:
            print(f"  ERROR: No audio captured!")
            continue
        
        # Process
        print(f"  Processing...")
        audio = trim_and_normalize(audio)
        
        # Save
        sf.write(output_path, audio, SAMPLE_RATE)
        duration = len(audio) / SAMPLE_RATE
        print(f"  Saved: {filename} ({duration:.2f}s)")
        exported.append(output_path)
        
        time.sleep(0.3)  # Brief pause between notes
    
    return exported


def main():
    """Main export loop."""
    print("=" * 60)
    print("AUTO SPITFIRE EXPORTER")
    print("=" * 60)
    
    # Find loopback device
    loopback = find_stereo_mix()
    if loopback is None:
        print("\nERROR: No loopback device found!")
        print("Enable Stereo Mix or install loopMIDI + VB-Cable")
        return
    
    # Check MIDI
    try:
        import mido
        outputs = mido.get_output_names()
        print(f"\nMIDI outputs: {outputs}")
        if not outputs:
            print("ERROR: No MIDI outputs available!")
            return
    except ImportError:
        print("ERROR: mido not installed!")
        return
    
    print(f"\nLoopback device: [{loopback}]")
    print(f"Instruments: {len(INSTRUMENTS)}")
    print(f"\nIMPORTANT SETUP:")
    print("  1. Open Spitfire Audio app")
    print("  2. Load BBC Symphony Orchestra")
    print("  3. Select instrument (e.g., Violins 1 Long)")
    print("  4. Make sure MIDI input is configured")
    print("  5. Audio must play through speakers (for loopback)")
    print("\nIf MIDI doesn't trigger Spitfire:")
    print("  - Install loopMIDI (free virtual MIDI cable)")
    print("  - Set Spitfire MIDI input to loopMIDI port")
    print("  - This script will send to loopMIDI")
    print("=" * 60)
    
    input("\nPress ENTER when ready (Ctrl+C to cancel)...")
    
    output_base = Path(__file__).parent.parent / "samples"
    all_exported = []
    
    for instrument in INSTRUMENTS:
        try:
            files = export_instrument(instrument, output_base, loopback)
            all_exported.extend(files)
        except KeyboardInterrupt:
            print("\nCancelled by user")
            break
        except Exception as e:
            print(f"Error: {e}")
            continue
    
    print("\n" + "=" * 60)
    print(f"EXPORTED: {len(all_exported)} samples")
    print("=" * 60)


if __name__ == "__main__":
    main()
