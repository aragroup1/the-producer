"""Shared MIDI processing utilities."""

import mido
from mido import MidiFile, MidiTrack, Message, MetaMessage
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path


# Standard MIDI note mappings
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Common chord progressions by genre
CHORD_PROGRESSIONS = {
    "trap": [
        ["Cm", "Gm", "Ab", "Eb"],
        ["Dm", "Am", "Bb", "F"],
        ["Fm", "Cm", "Db", "Ab"],
        ["Gm", "Dm", "Eb", "Bb"],
    ],
    "drill": [
        ["Cm", "Fm", "Gm", "Cm"],
        ["Dm", "Gm", "Am", "Dm"],
        ["Fm", "Bbm", "Cm", "Fm"],
    ],
    "lo-fi": [
        ["Am", "F", "C", "G"],
        ["Dm", "G", "C", "Am"],
        ["Em", "C", "G", "D"],
        ["Am", "Em", "F", "C"],
    ],
    "afrobeats": [
        ["C", "G", "Am", "F"],
        ["F", "C", "Dm", "Bb"],
        ["G", "D", "Em", "C"],
    ],
    "rage": [
        ["Cm", "Eb", "Fm", "Ab"],
        ["Dm", "F", "Gm", "Bb"],
    ],
}

# Scale definitions
SCALES = {
    "major": [0, 2, 4, 5, 7, 9, 11],
    "minor": [0, 2, 3, 5, 7, 8, 10],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "phrygian": [0, 1, 3, 5, 7, 8, 10],
    "lydian": [0, 2, 4, 6, 7, 9, 11],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
}

# Chord definitions (root relative semitones)
CHORDS = {
    "": [0, 4, 7],          # Major
    "m": [0, 3, 7],         # Minor
    "7": [0, 4, 7, 10],     # Dominant 7
    "m7": [0, 3, 7, 10],    # Minor 7
    "maj7": [0, 4, 7, 11],  # Major 7
    "dim": [0, 3, 6],       # Diminished
    "aug": [0, 4, 8],       # Augmented
    "sus4": [0, 5, 7],      # Sus4
    "add9": [0, 4, 7, 14],  # Add9
}


def note_name_to_midi(note_name: str, octave: int = 4) -> int:
    """Convert note name to MIDI note number."""
    note_name = note_name.strip()
    
    # Parse accidental
    if len(note_name) == 1:
        note_idx = NOTE_NAMES.index(note_name)
    elif note_name[1] == '#':
        note_idx = NOTE_NAMES.index(note_name[:2])
    elif note_name[1] == 'b':
        note_idx = NOTE_NAMES.index(note_name[:2]) if note_name[:2] in NOTE_NAMES else NOTE_NAMES.index(note_name[0]) - 1
    else:
        note_idx = NOTE_NAMES.index(note_name[0])
    
    return (octave + 1) * 12 + note_idx


def midi_to_note_name(midi_note: int) -> str:
    """Convert MIDI note number to note name."""
    octave = (midi_note // 12) - 1
    note_idx = midi_note % 12
    return f"{NOTE_NAMES[note_idx]}{octave}"


def parse_chord(chord_name: str) -> Tuple[str, str]:
    """Parse chord name into root and quality."""
    chord_name = chord_name.strip()
    
    if len(chord_name) == 1:
        return chord_name, ""
    
    if chord_name[1] in ['#', 'b']:
        root = chord_name[:2]
        quality = chord_name[2:]
    else:
        root = chord_name[0]
        quality = chord_name[1:]
    
    return root, quality


def chord_to_notes(chord_name: str, octave: int = 4) -> List[int]:
    """Convert chord name to MIDI note numbers."""
    root, quality = parse_chord(chord_name)
    root_midi = note_name_to_midi(root, octave)
    
    intervals = CHORDS.get(quality, CHORDS[""])
    return [root_midi + interval for interval in intervals]


def generate_chord_progression(genre: str, key: str = None, 
                                num_chords: int = 4) -> List[List[int]]:
    """Generate a chord progression for a genre."""
    progressions = CHORD_PROGRESSIONS.get(genre, CHORD_PROGRESSIONS["trap"])
    progression = progressions[np.random.randint(len(progressions))]
    
    # Convert to MIDI notes
    midi_chords = []
    for chord_name in progression[:num_chords]:
        midi_chords.append(chord_to_notes(chord_name, octave=4))
    
    return midi_chords


def create_midi_file(bpm: int = 140, ppq: int = 480) -> MidiFile:
    """Create a new MIDI file with default settings."""
    midi = MidiFile(type=1, ticks_per_beat=ppq)
    return midi


def add_track(midi: MidiFile, track_name: str = "") -> MidiTrack:
    """Add a new track to MIDI file."""
    track = MidiTrack()
    midi.tracks.append(track)
    
    if track_name:
        track.append(MetaMessage('track_name', name=track_name, time=0))
    
    return track


def set_tempo(track: MidiTrack, bpm: int, time: int = 0) -> None:
    """Set tempo on a track."""
    tempo = mido.bpm2tempo(bpm)
    track.append(MetaMessage('set_tempo', tempo=tempo, time=time))


def add_note(track: MidiTrack, note: int, velocity: int, 
             start_time: int, duration: int, channel: int = 0) -> None:
    """Add a note to a track."""
    track.append(Message('note_on', note=note, velocity=velocity, 
                         time=start_time, channel=channel))
    track.append(Message('note_off', note=note, velocity=0, 
                         time=duration, channel=channel))


def add_chord(track: MidiTrack, notes: List[int], velocity: int,
              start_time: int, duration: int, channel: int = 0) -> None:
    """Add a chord (multiple notes simultaneously) to a track."""
    for i, note in enumerate(notes):
        note_start = start_time if i == 0 else 0
        track.append(Message('note_on', note=note, velocity=velocity,
                             time=note_start, channel=channel))
    
    for i, note in enumerate(notes):
        note_duration = duration if i == 0 else 0
        track.append(Message('note_off', note=note, velocity=0,
                             time=note_duration, channel=channel))


def bars_to_ticks(bars: float, ppq: int = 480, beats_per_bar: int = 4) -> int:
    """Convert bars to MIDI ticks."""
    return int(bars * beats_per_bar * ppq)


def generate_drum_pattern(genre: str, bars: int = 4, 
                          variation: int = 0) -> Dict[str, List[Tuple[float, int]]]:
    """Generate a drum pattern for a genre.
    
    Returns dict of drum_name -> list of (beat_position, velocity)
    """
    if genre in ["trap", "drill", "rage"]:
        return _generate_trap_drums(bars, variation)
    elif genre == "lo-fi":
        return _generate_lofi_drums(bars, variation)
    elif genre == "afrobeats":
        return _generate_afrobeats_drums(bars, variation)
    else:
        return _generate_trap_drums(bars, variation)


def _generate_trap_drums(bars: int, variation: int) -> Dict[str, List[Tuple[float, int]]]:
    """Generate trap/drill drum pattern."""
    pattern = {
        "kick": [],
        "snare": [],
        "hihat": [],
        "open_hihat": [],
        "clap": []
    }
    
    for bar in range(bars):
        bar_offset = bar * 4
        
        # Kick on 1, 2.5, 3 (trap pattern)
        pattern["kick"].append((bar_offset + 0, 100))
        pattern["kick"].append((bar_offset + 1.5, 90))
        pattern["kick"].append((bar_offset + 2.5, 95))
        
        # Snare/clap on 2 and 4
        pattern["snare"].append((bar_offset + 1, 110))
        pattern["snare"].append((bar_offset + 3, 110))
        pattern["clap"].append((bar_offset + 1, 100))
        pattern["clap"].append((bar_offset + 3, 100))
        
        # Hi-hats every 8th note
        for i in range(8):
            vel = 70 + np.random.randint(-10, 10)
            pattern["hihat"].append((bar_offset + i * 0.5, vel))
        
        # Occasional open hihat
        if bar % 2 == 1:
            pattern["open_hihat"].append((bar_offset + 3.5, 80))
    
    return pattern


def _generate_lofi_drums(bars: int, variation: int) -> Dict[str, List[Tuple[float, int]]]:
    """Generate lo-fi drum pattern."""
    pattern = {
        "kick": [],
        "snare": [],
        "hihat": [],
        "open_hihat": [],
        "rim": []
    }
    
    for bar in range(bars):
        bar_offset = bar * 4
        
        # Softer kick
        pattern["kick"].append((bar_offset + 0, 80))
        pattern["kick"].append((bar_offset + 2.5, 75))
        
        # Snare on 2 and 4 (softer)
        pattern["snare"].append((bar_offset + 1, 85))
        pattern["snare"].append((bar_offset + 3, 85))
        
        # Loose hihats
        for i in range(4):
            vel = 50 + np.random.randint(-10, 15)
            pattern["hihat"].append((bar_offset + i, vel))
    
    return pattern


def _generate_afrobeats_drums(bars: int, variation: int) -> Dict[str, List[Tuple[float, int]]]:
    """Generate afrobeats drum pattern."""
    pattern = {
        "kick": [],
        "snare": [],
        "hihat": [],
        "tom": [],
        "shaker": []
    }
    
    for bar in range(bars):
        bar_offset = bar * 4
        
        # Kick pattern (afrobeats bounce)
        pattern["kick"].append((bar_offset + 0, 100))
        pattern["kick"].append((bar_offset + 1.5, 90))
        pattern["kick"].append((bar_offset + 2.75, 85))
        
        # Snare
        pattern["snare"].append((bar_offset + 1, 95))
        pattern["snare"].append((bar_offset + 3, 95))
        
        # Shaker on 16ths
        for i in range(16):
            vel = 60 + np.random.randint(-10, 10)
            pattern["shaker"].append((bar_offset + i * 0.25, vel))
    
    return pattern


def drum_pattern_to_midi(pattern: Dict[str, List[Tuple[float, int]]], 
                         bpm: int = 140, ppq: int = 480) -> MidiFile:
    """Convert drum pattern dict to MIDI file."""
    midi = create_midi_file(bpm, ppq)
    
    # Standard GM drum map
    drum_notes = {
        "kick": 36,
        "snare": 38,
        "hihat": 42,
        "open_hihat": 46,
        "clap": 39,
        "rim": 37,
        "tom": 45,
        "shaker": 82,
        "crash": 49,
        "ride": 51
    }
    
    track = add_track(midi, "Drums")
    set_tempo(track, bpm)
    
    # Channel 9 (10) for drums
    drum_channel = 9
    
    for drum_name, hits in pattern.items():
        note = drum_notes.get(drum_name, 36)
        
        for beat_pos, velocity in hits:
            tick_pos = int(beat_pos * ppq)
            duration = int(0.1 * ppq)  # Short drum hits
            
            track.append(Message('note_on', note=note, velocity=velocity,
                                 time=tick_pos, channel=drum_channel))
            track.append(Message('note_off', note=note, velocity=0,
                                 time=duration, channel=drum_channel))
    
    return midi


def save_midi(midi: MidiFile, path: str) -> str:
    """Save MIDI file to disk."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    midi.save(path)
    return path


def midi_to_notes(midi_path: str) -> Dict[str, Any]:
    """Extract note data from MIDI file."""
    midi = MidiFile(midi_path)
    
    notes = []
    for i, track in enumerate(midi.tracks):
        track_notes = []
        current_time = 0
        
        for msg in track:
            current_time += msg.time
            
            if msg.type == 'note_on' and msg.velocity > 0:
                track_notes.append({
                    'note': msg.note,
                    'velocity': msg.velocity,
                    'time': current_time,
                    'channel': msg.channel
                })
        
        notes.append({
            'track': i,
            'track_name': _get_track_name(track),
            'notes': track_notes
        })
    
    return {
        'ticks_per_beat': midi.ticks_per_beat,
        'tracks': notes
    }


def _get_track_name(track: MidiTrack) -> str:
    """Extract track name from MIDI track."""
    for msg in track:
        if msg.type == 'track_name':
            return msg.name
    return ""


def transpose_midi(midi_path: str, semitones: int, output_path: str) -> str:
    """Transpose all notes in a MIDI file."""
    midi = MidiFile(midi_path)
    
    for track in midi.tracks:
        for msg in track:
            if msg.type in ['note_on', 'note_off']:
                msg.note = max(0, min(127, msg.note + semitones))
    
    midi.save(output_path)
    return output_path
