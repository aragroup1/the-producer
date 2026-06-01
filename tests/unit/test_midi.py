"""Unit tests for MIDI utilities."""

import pytest
import numpy as np

from shared.utils.midi import (
    note_name_to_midi, midi_to_note_name, chord_to_notes,
    generate_chord_progression, generate_drum_pattern,
    create_midi_file, add_track, set_tempo, add_note, add_chord,
    save_midi, parse_chord
)


class TestMidiUtilities:
    """Test MIDI utility functions."""
    
    def test_note_name_to_midi(self):
        """Test note name to MIDI conversion."""
        assert note_name_to_midi("C", 4) == 60
        assert note_name_to_midi("A", 4) == 69
        assert note_name_to_midi("C#", 4) == 61
        assert note_name_to_midi("Bb", 3) == 58
    
    def test_midi_to_note_name(self):
        """Test MIDI to note name conversion."""
        assert midi_to_note_name(60) == "C4"
        assert midi_to_note_name(69) == "A4"
        assert midi_to_note_name(61) == "C#4"
    
    def test_parse_chord(self):
        """Test chord name parsing."""
        root, quality = parse_chord("Cm")
        assert root == "C"
        assert quality == "m"
        
        root, quality = parse_chord("F#maj7")
        assert root == "F#"
        assert quality == "maj7"
    
    def test_chord_to_notes(self):
        """Test chord to MIDI notes conversion."""
        notes = chord_to_notes("C", octave=4)
        assert notes == [60, 64, 67]  # C major triad
        
        notes = chord_to_notes("Am", octave=4)
        assert notes == [69, 72, 76]  # A minor triad
    
    def test_generate_chord_progression(self):
        """Test chord progression generation."""
        progression = generate_chord_progression("trap")
        
        assert len(progression) == 4
        for chord in progression:
            assert len(chord) == 3  # Triads
            assert all(0 <= note <= 127 for note in chord)
    
    def test_generate_drum_pattern(self):
        """Test drum pattern generation."""
        pattern = generate_drum_pattern("trap", bars=2)
        
        assert 'kick' in pattern
        assert 'snare' in pattern
        assert 'hihat' in pattern
        
        # Should have hits in each bar
        assert len(pattern['kick']) > 0
        assert len(pattern['snare']) > 0
    
    def test_create_midi_file(self):
        """Test MIDI file creation."""
        midi = create_midi_file(bpm=140)
        
        assert midi.type == 1
        assert midi.ticks_per_beat == 480
    
    def test_add_track(self):
        """Test adding a track to MIDI file."""
        midi = create_midi_file()
        track = add_track(midi, "Test Track")
        
        assert len(midi.tracks) == 1
        assert track.name == "Test Track"
    
    def test_save_midi(self, tmp_path):
        """Test saving MIDI file."""
        midi = create_midi_file(bpm=120)
        track = add_track(midi, "Test")
        set_tempo(track, 120)
        
        path = str(tmp_path / "test.mid")
        save_midi(midi, path)
        
        import os
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0
