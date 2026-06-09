"""Professional sample-based audio rendering engine.

Replaces FluidSynth with a high-quality sampler that loads WAV samples
and renders MIDI tracks with ADSR envelopes, pitch shifting, and effects.
"""

import json
import os
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field

import numpy as np
import soundfile as sf
import structlog
from scipy import signal

logger = structlog.get_logger()

# Try to import effects engine
try:
    from effects_engine import EffectsEngine
    EFFECTS_AVAILABLE = True
except ImportError:
    EFFECTS_AVAILABLE = False

SAMPLE_RATE = 44100


@dataclass
class ADSR:
    """ADSR envelope parameters."""
    attack_ms: float = 5.0
    decay_ms: float = 50.0
    sustain_level: float = 0.7
    release_ms: float = 100.0
    
    def to_samples(self, sr: int = SAMPLE_RATE) -> Tuple[int, int, int]:
        """Convert ms to samples."""
        attack_samples = int(self.attack_ms * sr / 1000)
        decay_samples = int(self.decay_ms * sr / 1000)
        release_samples = int(self.release_ms * sr / 1000)
        return attack_samples, decay_samples, release_samples


@dataclass
class Sample:
    """A loaded audio sample with metadata."""
    name: str
    path: str
    data: np.ndarray
    sr: int
    root_note: Optional[int] = None  # MIDI note number
    genre: str = ""
    category: str = ""
    tags: List[str] = field(default_factory=list)
    
    @property
    def duration(self) -> float:
        """Duration in seconds."""
        return len(self.data) / self.sr
    
    @property
    def is_stereo(self) -> bool:
        return self.data.ndim > 1 and self.data.shape[0] == 2


@dataclass
class SampleMap:
    """Maps MIDI notes/velocities to samples for an instrument."""
    category: str  # e.g., 'kick', 'snare', '808', 'synth_lead'
    genre: str
    samples: List[Sample] = field(default_factory=list)
    # For melodic instruments: root_note → sample
    note_map: Dict[int, Sample] = field(default_factory=dict)
    # For drums: name → sample (round-robin)
    name_map: Dict[str, List[Sample]] = field(default_factory=dict)
    
    def get_drum_sample(self, drum_name: str) -> Optional[Sample]:
        """Get a random sample for a drum name (round-robin)."""
        samples = self.name_map.get(drum_name)
        if samples:
            return random.choice(samples)
        return None
    
    def get_melodic_sample(self, midi_note: int) -> Optional[Sample]:
        """Get sample closest to MIDI note, or pitch-shift."""
        if not self.note_map:
            # No root notes defined — use first sample and pitch-shift
            if self.samples:
                return self.samples[0]
            return None
        
        # Find closest root note
        if midi_note in self.note_map:
            return self.note_map[midi_note]
        
        closest = min(self.note_map.keys(), key=lambda n: abs(n - midi_note))
        return self.note_map[closest]


class SampleEngine:
    """High-quality sample-based rendering engine.
    
    Loads WAV samples and renders MIDI compositions with:
    - ADSR envelopes
    - Pitch shifting for melodic content
    - Velocity sensitivity
    - Per-track stem rendering
    """
    
    # Default ADSR by instrument type
    DEFAULT_ADSR = {
        'kick': ADSR(attack_ms=2, decay_ms=80, sustain_level=0.0, release_ms=50),
        'snare': ADSR(attack_ms=2, decay_ms=100, sustain_level=0.0, release_ms=80),
        'hihat': ADSR(attack_ms=1, decay_ms=30, sustain_level=0.0, release_ms=20),
        'clap': ADSR(attack_ms=2, decay_ms=120, sustain_level=0.0, release_ms=100),
        '808': ADSR(attack_ms=5, decay_ms=200, sustain_level=0.8, release_ms=300),
        'synth_lead': ADSR(attack_ms=20, decay_ms=100, sustain_level=0.7, release_ms=200),
        'synth_pad': ADSR(attack_ms=200, decay_ms=300, sustain_level=0.6, release_ms=500),
        'piano': ADSR(attack_ms=5, decay_ms=200, sustain_level=0.5, release_ms=300),
        'bass': ADSR(attack_ms=10, decay_ms=150, sustain_level=0.8, release_ms=200),
        'pluck': ADSR(attack_ms=5, decay_ms=80, sustain_level=0.0, release_ms=100),
        'guitar': ADSR(attack_ms=10, decay_ms=200, sustain_level=0.4, release_ms=300),
        'violin': ADSR(attack_ms=100, decay_ms=200, sustain_level=0.8, release_ms=400),
        'strings': ADSR(attack_ms=150, decay_ms=300, sustain_level=0.7, release_ms=500),
        'brass': ADSR(attack_ms=30, decay_ms=150, sustain_level=0.7, release_ms=250),
        'flute': ADSR(attack_ms=50, decay_ms=100, sustain_level=0.6, release_ms=200),
        'vocal': ADSR(attack_ms=20, decay_ms=100, sustain_level=0.8, release_ms=150),
    }
    
    def __init__(self, sample_base_path: Optional[str] = None, 
                 sample_rate: int = SAMPLE_RATE,
                 use_effects: bool = True):
        self.sample_rate = sample_rate
        self.sample_base = sample_base_path or os.getenv(
            'SAMPLE_PATH', 
            os.path.join(os.path.dirname(__file__), '..', '..', '..', 'samples')
        )
        self.sample_base = os.path.abspath(self.sample_base)
        
        # Loaded sample maps by (category, genre)
        self.sample_maps: Dict[Tuple[str, str], SampleMap] = {}
        
        # Track which categories are loaded
        self.loaded_categories: set = set()
        
        # Effects engine
        self.use_effects = use_effects and EFFECTS_AVAILABLE
        self.effects = EffectsEngine(sample_rate) if self.use_effects else None
        
        logger.info("sample_engine_initialized", 
                   base_path=self.sample_base,
                   effects_enabled=self.use_effects)
    
    def load_category(self, category: str, genre: str) -> SampleMap:
        """Load all samples for a category/genre."""
        key = (category, genre)
        if key in self.sample_maps:
            return self.sample_maps[key]
        
        # Map category names to directory names (some are plural in dirs)
        dir_name_map = {
            'kick': 'kicks', 'snare': 'snares', 
            'hihat': 'hihats', 'hihat_closed': 'hihats', 'hihat_open': 'hihats',
            '808': '808s', 'clap': 'claps', 'perc': 'percs', 'cymbals': 'cymbals',
            'synth_lead': 'synth_leads', 'synth_pad': 'synth_pads',
            'piano': 'pianos', 'bass': 'bass', 'pluck': 'plucks', 'guitar': 'guitars',
            'violin': 'violins', 'strings': 'strings', 'viola': 'violas', 'cello': 'cellos',
            'brass': 'brass', 'flute': 'flutes', 'sax': 'saxes', 'vocal': 'vocals',
        }
        dir_name = dir_name_map.get(category, category)
        
        parent_dir = 'drums' if category in [
            'kick', 'snare', 'hihat', 'hihat_closed', 'hihat_open', '808', 
            'clap', 'perc', 'cymbals'
        ] else 'melodic' if category in [
            'synth_lead', 'synth_pad', 'piano', 'bass', 'pluck', 'guitar',
            'violin', 'strings', 'viola', 'cello', 'brass', 'flute', 'sax', 'vocal'
        ] else 'fx'
        
        sample_dir = os.path.join(self.sample_base, parent_dir, dir_name, genre)
        
        sample_map = SampleMap(category=category, genre=genre)
        
        if not os.path.exists(sample_dir):
            logger.warning("sample_dir_not_found", path=sample_dir)
            self.sample_maps[key] = sample_map
            return sample_map
        
        # Load all WAV files
        for wav_file in sorted(Path(sample_dir).glob('*.wav')):
            try:
                data, sr = sf.read(str(wav_file))
                
                # Convert to stereo if mono
                if data.ndim == 1:
                    data = np.stack([data, data])
                elif data.ndim > 1 and data.shape[0] != 2:
                    data = data.T  # Ensure (channels, samples)
                
                # Resample if needed
                if sr != self.sample_rate:
                    data = self._resample(data, sr, self.sample_rate)
                
                # Parse root note from filename (e.g., "808_C.wav" → C=36)
                root_note = self._parse_root_note(wav_file.stem)
                
                sample = Sample(
                    name=wav_file.stem,
                    path=str(wav_file),
                    data=data,
                    sr=self.sample_rate,
                    root_note=root_note,
                    genre=genre,
                    category=category
                )
                
                sample_map.samples.append(sample)
                
                # Map by root note for melodic instruments
                if root_note is not None:
                    sample_map.note_map[root_note] = sample
                
                # Map by name for drums
                sample_map.name_map.setdefault(category, []).append(sample)
                
                logger.debug("sample_loaded", 
                           file=wav_file.name, 
                           category=category, 
                           genre=genre,
                           root_note=root_note)
                
            except Exception as e:
                logger.warning("sample_load_failed", file=str(wav_file), error=str(e))
        
        self.sample_maps[key] = sample_map
        self.loaded_categories.add(category)
        
        logger.info("category_loaded", 
                   category=category, 
                   genre=genre, 
                   count=len(sample_map.samples))
        
        return sample_map
    
    def _parse_root_note(self, filename: str) -> Optional[int]:
        """Parse root note from filename like '808_C.wav' or 'lead_A#3.wav'."""
        import re
        
        # Look for note name at end: C, C#, Db, D, etc. optionally with octave
        match = re.search(r'[_-]([A-G][#b]?)(\d)?$', filename)
        if match:
            note_name = match.group(1)
            octave = int(match.group(2)) if match.group(2) else 3
            
            note_to_midi = {
                'C': 0, 'C#': 1, 'Db': 1,
                'D': 2, 'D#': 3, 'Eb': 3,
                'E': 4,
                'F': 5, 'F#': 6, 'Gb': 6,
                'G': 7, 'G#': 8, 'Ab': 8,
                'A': 9, 'A#': 10, 'Bb': 10,
                'B': 11
            }
            
            if note_name in note_to_midi:
                return note_to_midi[note_name] + (octave + 1) * 12
        
        return None
    
    def _resample(self, audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
        """Resample audio to target sample rate."""
        ratio = target_sr / orig_sr
        new_length = int(len(audio[0]) * ratio)
        
        resampled = np.zeros((audio.shape[0], new_length))
        for ch in range(audio.shape[0]):
            resampled[ch] = signal.resample(audio[ch], new_length)
        
        return resampled
    
    def _pitch_shift(self, audio: np.ndarray, semitones: float) -> np.ndarray:
        """Pitch-shift audio by semitones using phase vocoder."""
        if abs(semitones) < 0.1:
            return audio
        
        # Simple time-stretch then resample approach
        ratio = 2 ** (semitones / 12)
        
        shifted = np.zeros((audio.shape[0], int(len(audio[0]) / ratio)))
        for ch in range(audio.shape[0]):
            # Stretch in time domain
            stretched = signal.resample(audio[ch], int(len(audio[ch]) / ratio))
            shifted[ch] = stretched
        
        return shifted
    
    def _apply_adsr(self, audio: np.ndarray, adsr: ADSR, 
                    note_duration: float) -> np.ndarray:
        """Apply ADSR envelope to audio."""
        attack_s, decay_s, release_s = adsr.to_samples(self.sample_rate)
        total_samples = len(audio[0])
        
        envelope = np.ones(total_samples)
        
        # Attack
        if attack_s > 0:
            attack_end = min(attack_s, total_samples)
            envelope[:attack_end] = np.linspace(0, 1, attack_end)
        
        # Decay
        if decay_s > 0:
            decay_start = attack_s
            decay_end = min(decay_start + decay_s, total_samples)
            if decay_end > decay_start:
                envelope[decay_start:decay_end] = np.linspace(
                    1, adsr.sustain_level, decay_end - decay_start
                )
        
        # Sustain
        sustain_start = attack_s + decay_s
        if sustain_start < total_samples:
            envelope[sustain_start:] = adsr.sustain_level
        
        # Release (at end of note duration)
        note_samples = int(note_duration * self.sample_rate)
        release_start = min(note_samples, total_samples)
        if release_start < total_samples and release_s > 0:
            release_end = min(release_start + release_s, total_samples)
            if release_end > release_start:
                envelope[release_start:release_end] = np.linspace(
                    envelope[release_start], 0, release_end - release_start
                )
            if release_end < total_samples:
                envelope[release_end:] = 0
        
        # Apply envelope
        return audio * envelope
    
    def _velocity_scale(self, audio: np.ndarray, velocity: int) -> np.ndarray:
        """Scale audio by MIDI velocity (0-127)."""
        # Velocity curve: exponential for more dynamic range
        scale = (velocity / 127) ** 1.5
        return audio * scale
    
    def render_note(self, sample: Sample, midi_note: int, velocity: int,
                    start_time: float, duration: float,
                    adsr: Optional[ADSR] = None) -> Tuple[np.ndarray, int]:
        """Render a single note with pitch/velocity/ADSR.
        
        Returns:
            (audio_array, start_sample)
        """
        # Get base audio
        audio = sample.data.copy()
        
        # Pitch shift if needed (for melodic instruments)
        if sample.root_note is not None and midi_note != sample.root_note:
            semitones = midi_note - sample.root_note
            audio = self._pitch_shift(audio, semitones)
        
        # Apply velocity
        audio = self._velocity_scale(audio, velocity)
        
        # Apply ADSR
        if adsr is None:
            adsr = ADSR()  # Default
        audio = self._apply_adsr(audio, adsr, duration)
        
        # Calculate start sample
        start_sample = int(start_time * self.sample_rate)
        
        return audio, start_sample
    
    # Per-drum gain compensation — samples vary wildly in loudness
    # These are multiplicative: applied AFTER velocity scaling
    DRUM_GAIN_COMPENSATION = {
        'kick': 8.0,       # Kicks need massive boost (raw samples ~0.05 peak)
        'snare': 6.0,      # Snares also very quiet
        'hihat': 4.0,      # Hihats need less but still significant
        'hihat_closed': 4.0,
        'hihat_open': 3.5,
        'clap': 5.0,       # Claps need strong boost
        '808': 3.0,        # 808s are quiet but sustained
        'perc': 4.0,
        'cymbals': 3.0,
    }
    
    def render_drum_hit(self, drum_name: str, genre: str, 
                        velocity: int = 100,
                        start_time: float = 0.0,
                        humanize_ms: float = 0.0) -> Optional[Tuple[np.ndarray, int]]:
        """Render a single drum hit.
        
        Args:
            drum_name: e.g., 'kick', 'snare', 'hihat_closed'
            genre: Genre for sample selection
            velocity: MIDI velocity (0-127)
            start_time: Start time in seconds
            humanize_ms: Random timing offset in ms
        
        Returns:
            (audio_array, start_sample) or None if no sample
        """
        # Map drum names to categories
        category_map = {
            'kick': 'kick', 'snare': 'snare',
            'hihat': 'hihat', 'hihat_closed': 'hihat', 'hihat_open': 'hihat',
            'clap': 'clap', '808': '808',
            'perc': 'perc', 'cymbals': 'cymbals'
        }
        category = category_map.get(drum_name, drum_name)
        
        sample_map = self.load_category(category, genre)
        sample = sample_map.get_drum_sample(category)
        
        if sample is None:
            logger.warning("no_sample_found", drum=drum_name, genre=genre)
            return None
        
        # Apply humanization
        if humanize_ms > 0:
            jitter = random.uniform(-humanize_ms, humanize_ms) / 1000
            start_time += jitter
        
        adsr = self.DEFAULT_ADSR.get(category, ADSR())
        audio, start_sample = self.render_note(sample, 60, velocity, start_time, 
                                sample.duration, adsr)
        
        # Apply category-specific gain compensation
        gain = self.DRUM_GAIN_COMPENSATION.get(drum_name, 1.0)
        audio *= gain
        
        return audio, start_sample
    
    def render_drum_pattern(self, pattern: Dict[str, List[Tuple[float, int]]],
                            genre: str, bars: int = 4,
                            humanize_ms: float = 5.0,
                            bpm: int = 140) -> np.ndarray:
        """Render a full drum pattern.
        
        Args:
            pattern: Dict of drum_name → [(time, velocity), ...]
            genre: Genre for sample selection
            bars: Number of bars
            humanize_ms: Timing jitter in milliseconds
            bpm: Tempo in BPM
        
        Returns:
            Stereo audio array
        """
        # Calculate total samples based on actual BPM
        seconds_per_beat = 60.0 / bpm
        total_duration = bars * 4 * seconds_per_beat
        total_samples = int(total_duration * self.sample_rate)
        output = np.zeros((2, total_samples))
        
        for drum_name, hits in pattern.items():
            for hit_time, velocity in hits:
                result = self.render_drum_hit(
                    drum_name, genre, velocity, hit_time, humanize_ms
                )
                if result:
                    audio, start_sample = result
                    end_sample = start_sample + audio.shape[1]
                    
                    if end_sample > output.shape[1]:
                        # Extend output to accommodate this hit
                        padding = end_sample - output.shape[1] + 100  # Small buffer
                        output = np.pad(output, ((0, 0), (0, padding)))
                    
                    # Mix in (handle negative start_sample from humanization)
                    if start_sample < 0:
                        # Trim audio start
                        audio = audio[:, -start_sample:]
                        start_sample = 0
                    
                    available = output.shape[1] - start_sample
                    if available > 0 and audio.shape[1] > 0:
                        mix_len = min(audio.shape[1], available)
                        output[:, start_sample:start_sample + mix_len] += audio[:, :mix_len]
        
        # Prevent clipping
        peak = np.max(np.abs(output))
        if peak > 0.9:
            output *= 0.9 / peak
        
        return output
    
    def render_melodic_track(self, notes: List[Dict[str, Any]], 
                             category: str, genre: str,
                             humanize_ms: float = 5.0) -> np.ndarray:
        """Render a melodic track (bass, lead, pad, etc.).
        
        Args:
            notes: List of {pitch, velocity, start_time, duration}
            category: e.g., 'synth_lead', 'bass', 'synth_pad'
            genre: Genre for sample selection
            humanize_ms: Timing jitter
        
        Returns:
            Stereo audio array
        """
        if not notes:
            return np.zeros((2, 0))
        
        # Calculate total duration
        max_end = max(n['start_time'] + n['duration'] for n in notes)
        total_samples = int(max_end * self.sample_rate) + int(self.sample_rate * 2)
        output = np.zeros((2, total_samples))
        
        sample_map = self.load_category(category, genre)
        adsr = self.DEFAULT_ADSR.get(category, ADSR())
        
        for note in notes:
            # Handle both single notes ('pitch') and chords ('pitches')
            if 'pitch' in note:
                midi_notes = [note['pitch']]
            elif 'pitches' in note:
                midi_notes = note['pitches']
            else:
                continue
            
            velocity = note.get('velocity', 100)
            start_time = note['start_time']
            duration = note.get('duration', 1.0)
            
            # Humanization
            if humanize_ms > 0:
                jitter = random.uniform(-humanize_ms, humanize_ms) / 1000
                start_time += jitter
            
            # Velocity variation
            if humanize_ms > 0:
                vel_jitter = random.randint(-5, 5)
                velocity = max(1, min(127, velocity + vel_jitter))
            
            # Render each note in the chord
            for midi_note in midi_notes:
                sample = sample_map.get_melodic_sample(midi_note)
                if sample is None:
                    continue
                
                audio, start_sample = self.render_note(
                    sample, midi_note, velocity, start_time, duration, adsr
                )
                
                end_sample = start_sample + audio.shape[1]
                
                if end_sample > output.shape[1]:
                    # Extend output to accommodate this hit
                    padding = end_sample - output.shape[1] + 100  # Small buffer
                    output = np.pad(output, ((0, 0), (0, padding)))
                
                # Mix in (handle negative start_sample from humanization)
                if start_sample < 0:
                    # Trim audio start
                    audio = audio[:, -start_sample:]
                    start_sample = 0
                
                available = output.shape[1] - start_sample
                if available > 0 and audio.shape[1] > 0:
                    mix_len = min(audio.shape[1], available)
                    output[:, start_sample:start_sample + mix_len] += audio[:, :mix_len]
        
        # Prevent clipping
        peak = np.max(np.abs(output))
        if peak > 0.9:
            output *= 0.9 / peak
        
        return output
    
    def render_beat(self, composition: Dict[str, Any], genre: str,
                    bpm: int = 140, humanize_ms: float = 5.0) -> Dict[str, np.ndarray]:
        """Render a full beat composition into stems.
        
        Args:
            composition: Output from CompositionEngine.compose_beat()
            genre: Genre for sample selection
            bpm: Tempo in BPM
            humanize_ms: Timing jitter amount
        
        Returns:
            Dict of stem_name → audio_array
        """
        logger.info("rendering_beat", genre=genre, bpm=bpm, 
                   tracks=list(composition.get('tracks', {}).keys()))
        
        stems = {}
        tracks = composition.get('tracks', {})
        
        # Render drums
        if 'drums' in tracks:
            drum_pattern = tracks['drums']
            # Convert to expected format if needed
            if isinstance(drum_pattern, dict):
                stems['drums'] = self.render_drum_pattern(
                    drum_pattern, genre, 
                    bars=composition.get('duration_bars', 16) // 4,
                    humanize_ms=humanize_ms
                )
        
        # Render bass
        if 'bass' in tracks:
            stems['bass'] = self.render_melodic_track(
                tracks['bass'], 'bass', genre, humanize_ms
            )
        
        # Render melody
        if 'melody' in tracks:
            stems['melody'] = self.render_melodic_track(
                tracks['melody'], 'synth_lead', genre, humanize_ms
            )
        
        # Render counter-melody
        if 'counter_melody' in tracks:
            stems['counter_melody'] = self.render_melodic_track(
                tracks['counter_melody'], 'pluck', genre, humanize_ms
            )
        
        # Render pads (if present)
        if 'pads' in tracks:
            stems['pads'] = self.render_melodic_track(
                tracks['pads'], 'synth_pad', genre, humanize_ms
            )
        
        # Render guitar (if present)
        if 'guitar' in tracks:
            stems['guitar'] = self.render_melodic_track(
                tracks['guitar'], 'guitar', genre, humanize_ms
            )
        
        # Render piano (if present)
        if 'piano' in tracks:
            stems['piano'] = self.render_melodic_track(
                tracks['piano'], 'piano', genre, humanize_ms
            )
        
        # Render violin/strings (if present)
        if 'violin' in tracks:
            stems['violin'] = self.render_melodic_track(
                tracks['violin'], 'violin', genre, humanize_ms
            )
        
        # Render brass (if present)
        if 'brass' in tracks:
            stems['brass'] = self.render_melodic_track(
                tracks['brass'], 'brass', genre, humanize_ms
            )
        
        # Render flute (if present)
        if 'flute' in tracks:
            stems['flute'] = self.render_melodic_track(
                tracks['flute'], 'flute', genre, humanize_ms
            )
        
        # Render vocals/vocal chops (if present)
        if 'vocal' in tracks:
            stems['vocal'] = self.render_melodic_track(
                tracks['vocal'], 'vocal', genre, humanize_ms
            )
        
        logger.info("beat_rendered", stems=list(stems.keys()))
        return stems
    
    def mix_stems(self, stems: Dict[str, np.ndarray], 
                  gains: Optional[Dict[str, float]] = None,
                  apply_effects: bool = True,
                  genre: str = 'trap') -> np.ndarray:
        """Mix stems into a single stereo track with optional effects processing.
        
        Args:
            stems: Dict of stem_name → audio_array
            gains: Optional gain adjustments in dB
            apply_effects: Whether to apply stem effects and mastering
            genre: Genre for effects processing
        
        Returns:
            Mixed stereo audio
        """
        if not stems:
            return np.zeros((2, 0))
        
        # Apply stem effects if enabled
        processed_stems = stems
        if apply_effects and self.effects:
            processed_stems = self.effects.process_stems(stems)
        
        # Find max length
        max_len = max(s.shape[1] for s in processed_stems.values())
        mix = np.zeros((2, max_len))
        
        default_gains = {
            'drums': 0, 'bass': -2, 'melody': -3, 
            'counter_melody': -6, 'pads': -9,
            'guitar': -5, 'piano': -4, 'violin': -4,
            'brass': -3, 'flute': -5, 'vocal': -4
        }
        gains = gains or default_gains
        
        for name, stem in processed_stems.items():
            gain_db = gains.get(name, 0)
            gain_linear = 10 ** (gain_db / 20)
            
            # Pad if needed
            if stem.shape[1] < max_len:
                pad = max_len - stem.shape[1]
                stem = np.pad(stem, ((0, 0), (0, pad)))
            
            mix += stem * gain_linear
        
        # Apply mastering if enabled
        if apply_effects and self.effects:
            mix = self.effects.master_mix(mix, genre=genre)
        else:
            # Basic clip prevention
            peak = np.max(np.abs(mix))
            if peak > 0.95:
                mix *= 0.95 / peak
        
        return mix
    
    def save_stems(self, stems: Dict[str, np.ndarray], beat_id: str,
                   output_dir: str) -> Dict[str, str]:
        """Save stems to files.
        
        Returns:
            Dict of stem_name → file_path
        """
        os.makedirs(output_dir, exist_ok=True)
        paths = {}
        
        for name, audio in stems.items():
            path = os.path.join(output_dir, f'{beat_id}_{name}.wav')
            sf.write(path, audio.T, self.sample_rate, subtype='PCM_24')
            paths[name] = path
            logger.debug("stem_saved", stem=name, path=path)
        
        return paths
