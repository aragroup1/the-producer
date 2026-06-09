"""Professional effects processing using Pedalboard.

Replaces the need for external VST plugins with high-quality
built-in effects from Spotify's Pedalboard library.
"""

import numpy as np
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
import structlog

logger = structlog.get_logger()

try:
    from pedalboard import (
        Pedalboard, Compressor, Limiter, Reverb, Delay,
        HighpassFilter, LowpassFilter, Gain, Distortion,
        Chorus, Phaser, PitchShift, LadderFilter,
        Clipping, NoiseGate, Bitcrush, Mix
    )
    PEDALBOARD_AVAILABLE = True
except ImportError:
    PEDALBOARD_AVAILABLE = False
    logger.warning("pedalboard_not_installed", 
                   message="Install with: pip install pedalboard")


class StemEffects:
    """Effects chains for individual stems."""
    
    @staticmethod
    def drum_bus() -> Optional[Any]:
        """Drum bus processing — punch and glue."""
        if not PEDALBOARD_AVAILABLE:
            return None
        
        return Pedalboard([
            # Remove mud below kick fundamental
            HighpassFilter(cutoff_frequency_hz=50),
            
            # Punch compression
            Compressor(
                threshold_db=-12,
                ratio=3.0,
                attack_ms=3,      # Fast attack for punch
                release_ms=60
            ),
            
            # Gentle saturation
            Distortion(drive_db=2.0),
            
            # Makeup gain
            Gain(gain_db=3.0),
        ])
    
    @staticmethod
    def bass_bus() -> Optional[Any]:
        """Bass/808 bus processing — controlled low end."""
        if not PEDALBOARD_AVAILABLE:
            return None
        
        return Pedalboard([
            # Remove sub-rumble
            HighpassFilter(cutoff_frequency_hz=25),
            
            # Control dynamics (808s can be wild)
            Compressor(
                threshold_db=-10,
                ratio=3.5,
                attack_ms=8,
                release_ms=120
            ),
            
            # Saturation for harmonics (helps on small speakers)
            Distortion(drive_db=3.0),
            
            # Makeup gain
            Gain(gain_db=2.0),
        ])
    
    @staticmethod
    def melody_bus() -> Optional[Any]:
        """Melody bus — space and width."""
        if not PEDALBOARD_AVAILABLE:
            return None
        
        return Pedalboard([
            # Remove low-end buildup
            HighpassFilter(cutoff_frequency_hz=120),
            
            # Gentle compression
            Compressor(
                threshold_db=-16,
                ratio=2.0,
                attack_ms=12,
                release_ms=100
            ),
            
            # Subtle chorus for width
            Chorus(rate_hz=0.5, depth=0.3, mix=0.2),
            
            # Makeup gain
            Gain(gain_db=4.0),
        ])
    
    @staticmethod
    def vocal_chops_bus() -> Optional[Any]:
        """Vocal chops — character and space."""
        if not PEDALBOARD_AVAILABLE:
            return None
        
        return Pedalboard([
            HighpassFilter(cutoff_frequency_hz=80),
            
            # Heavy compression for consistency
            Compressor(
                threshold_db=-14,
                ratio=3.0,
                attack_ms=5,
                release_ms=80
            ),
            
            # Reverb for space
            Reverb(
                room_size=0.4,
                damping=0.5,
                wet_level=0.15,
                dry_level=0.85
            ),
            
            Gain(gain_db=3.0),
        ])
    
    @staticmethod
    def guitar_bus() -> Optional[Any]:
        """Guitar bus — warmth and presence."""
        if not PEDALBOARD_AVAILABLE:
            return None
        
        return Pedalboard([
            HighpassFilter(cutoff_frequency_hz=80),
            
            Compressor(
                threshold_db=-14,
                ratio=2.5,
                attack_ms=8,
                release_ms=90
            ),
            
            # Chorus for width
            Chorus(rate_hz=0.3, depth=0.4, mix=0.25),
            
            Gain(gain_db=3.0),
        ])
    
    @staticmethod
    def piano_bus() -> Optional[Any]:
        """Piano bus — clarity and body."""
        if not PEDALBOARD_AVAILABLE:
            return None
        
        return Pedalboard([
            HighpassFilter(cutoff_frequency_hz=60),
            
            Compressor(
                threshold_db=-16,
                ratio=2.0,
                attack_ms=10,
                release_ms=120
            ),
            
            # Gentle reverb for space
            Reverb(
                room_size=0.3,
                damping=0.6,
                wet_level=0.1,
                dry_level=0.9
            ),
            
            Gain(gain_db=3.0),
        ])
    
    @staticmethod
    def pad_bus() -> Optional[Any]:
        """Pad bus — smooth, atmospheric."""
        if not PEDALBOARD_AVAILABLE:
            return None
        
        return Pedalboard([
            HighpassFilter(cutoff_frequency_hz=100),
            
            # Heavy compression for smoothness
            Compressor(
                threshold_db=-12,
                ratio=2.5,
                attack_ms=20,
                release_ms=200
            ),
            
            # Lots of reverb for atmosphere
            Reverb(
                room_size=0.6,
                damping=0.4,
                wet_level=0.25,
                dry_level=0.75
            ),
            
            # Makeup gain
            Gain(gain_db=4.0),
        ])


class MixEffects:
    """Professional mix bus effects — applied to the full mix."""
    
    @staticmethod
    def trap_mastering() -> Optional[Any]:
        """Mastering chain optimized for trap beats.
        
        Chain: Highpass -> Compressor -> Limiter
        """
        if not PEDALBOARD_AVAILABLE:
            return None
        
        return Pedalboard([
            # Remove sub-bass rumble below 30Hz
            HighpassFilter(cutoff_frequency_hz=30),
            
            # Gentle compression for glue
            Compressor(
                threshold_db=-18,
                ratio=2.5,
                attack_ms=10,
                release_ms=100
            ),
            
            # Final limiter to prevent clipping
            Limiter(threshold_db=-1.0, release_ms=50),
        ])
    
    @staticmethod
    def aggressive_mastering() -> Optional[Any]:
        """Aggressive mastering for hard trap/drill.
        
        Chain: Highpass -> Compressor -> Clipper -> Limiter
        """
        if not PEDALBOARD_AVAILABLE:
            return None
        
        return Pedalboard([
            HighpassFilter(cutoff_frequency_hz=35),
            
            # Heavy compression
            Compressor(
                threshold_db=-14,
                ratio=4.0,
                attack_ms=5,
                release_ms=80
            ),
            
            # Soft clipping for aggression
            Clipping(threshold_db=-3.0),
            
            # Brickwall limiter
            Limiter(threshold_db=-0.5, release_ms=30),
        ])
    
    @staticmethod
    def lofi_mastering() -> Optional[Any]:
        """Lo-fi mastering with warmth and character.
        
        Chain: Highpass -> Bitcrush -> Compressor -> Limiter
        """
        if not PEDALBOARD_AVAILABLE:
            return None
        
        return Pedalboard([
            HighpassFilter(cutoff_frequency_hz=40),
            
            # Subtle bitcrush for texture
            Bitcrush(bit_depth=12),
            
            # Gentle compression
            Compressor(
                threshold_db=-20,
                ratio=2.0,
                attack_ms=15,
                release_ms=150
            ),
            
            Limiter(threshold_db=-1.5, release_ms=60),
        ])


class CreativeEffects:
    """Creative effects for sound design and ear candy."""
    
    @staticmethod
    def trap_riser(duration_seconds: float = 4.0, 
                   sample_rate: int = 44100) -> np.ndarray:
        """Generate a trap riser (white noise sweep up)."""
        samples = int(duration_seconds * sample_rate)
        
        # White noise
        noise = np.random.randn(samples)
        
        # Volume ramp up
        volume = np.linspace(0, 1, samples) ** 2
        
        # Filter sweep up
        if PEDALBOARD_AVAILABLE:
            # Use lowpass with increasing cutoff
            sweeps = []
            chunk_size = sample_rate // 10  # Process in 100ms chunks
            for i in range(0, samples, chunk_size):
                chunk = noise[i:i + chunk_size]
                progress = i / samples
                cutoff = 200 + progress * 18000  # 200Hz to 18kHz
                
                board = Pedalboard([
                    LowpassFilter(cutoff_frequency_hz=cutoff),
                    Gain(gain_db=-6),
                ])
                
                processed = board(chunk, sample_rate)
                sweeps.append(processed)
            
            riser = np.concatenate(sweeps)
        else:
            riser = noise
        
        return riser * volume
    
    @staticmethod
    def reverse_cymbal(sample: np.ndarray,
                       sample_rate: int = 44100) -> np.ndarray:
        """Create reverse cymbal effect from a cymbal sample."""
        # Reverse the sample
        reversed_sample = sample[::-1]
        
        # Apply volume ramp
        volume = np.linspace(0, 1, len(reversed_sample)) ** 1.5
        
        return reversed_sample * volume
    
    @staticmethod
    def tape_stop(audio: np.ndarray,
                  sample_rate: int = 44100,
                  duration_seconds: float = 2.0) -> np.ndarray:
        """Simulate tape stop effect (pitch down + slow down)."""
        if not PEDALBOARD_AVAILABLE:
            return audio
        
        samples = int(duration_seconds * sample_rate)
        audio = audio[:samples] if len(audio) > samples else audio
        
        # Process in chunks with decreasing pitch
        chunk_size = sample_rate // 20  # 50ms chunks
        result = []
        
        for i in range(0, len(audio), chunk_size):
            chunk = audio[i:i + chunk_size]
            progress = i / len(audio)
            
            # Pitch drops from 0 to -12 semitones
            semitones = -progress * 12
            
            board = Pedalboard([
                PitchShift(semitones=semitones),
            ])
            
            processed = board(chunk, sample_rate)
            result.append(processed)
        
        return np.concatenate(result)


class EffectsEngine:
    """Main effects engine — applies processing to stems and mix."""
    
    # Default effects chains by stem type
    DEFAULT_CHAINS: Dict[str, Callable] = {
        'drums': StemEffects.drum_bus,
        'bass': StemEffects.bass_bus,
        'melody': StemEffects.melody_bus,
        'pads': StemEffects.pad_bus,
        'guitar': StemEffects.guitar_bus,
        'piano': StemEffects.piano_bus,
        'vocal': StemEffects.vocal_chops_bus,
        'counter_melody': StemEffects.melody_bus,
    }
    
    # Mastering chains by genre
    MASTERING_CHAINS: Dict[str, Callable] = {
        'trap': MixEffects.trap_mastering,
        'drill': MixEffects.aggressive_mastering,
        'lofi': MixEffects.lofi_mastering,
        'default': MixEffects.trap_mastering,
    }
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.pedalboard_available = PEDALBOARD_AVAILABLE
        
        if not self.pedalboard_available:
            logger.warning("effects_engine_disabled", 
                          reason="pedalboard_not_installed")
    
    def process_stem(self, audio: np.ndarray, stem_name: str,
                     custom_chain: Optional[Any] = None) -> np.ndarray:
        """Apply effects to a single stem.
        
        Args:
            audio: Stereo audio array (channels, samples)
            stem_name: Name of the stem (drums, bass, etc.)
            custom_chain: Optional custom Pedalboard instance
        
        Returns:
            Processed audio
        """
        if not self.pedalboard_available:
            return audio
        
        # Use custom chain or look up default
        if custom_chain is not None:
            board = custom_chain
        elif stem_name in self.DEFAULT_CHAINS:
            board = self.DEFAULT_CHAINS[stem_name]()
        else:
            return audio
        
        if board is None:
            return audio
        
        try:
            # Pedalboard expects (samples,) or (channels, samples)
            # Our audio is (2, samples), which is correct
            processed = board(audio, self.sample_rate)
            return processed
        except Exception as e:
            logger.error("stem_processing_failed", 
                        stem=stem_name, error=str(e))
            return audio
    
    def process_stems(self, stems: Dict[str, np.ndarray],
                      custom_chains: Optional[Dict[str, Any]] = None
                      ) -> Dict[str, np.ndarray]:
        """Apply effects to all stems.
        
        Args:
            stems: Dict of stem_name → audio_array
            custom_chains: Optional dict of stem_name → Pedalboard
        
        Returns:
            Processed stems
        """
        processed = {}
        
        for name, audio in stems.items():
            chain = custom_chains.get(name) if custom_chains else None
            processed[name] = self.process_stem(audio, name, chain)
        
        return processed
    
    def master_mix(self, mix: np.ndarray, genre: str = 'trap',
                   custom_chain: Optional[Any] = None) -> np.ndarray:
        """Apply mastering to the final mix.
        
        Args:
            mix: Stereo mix array
            genre: Genre for genre-specific mastering
            custom_chain: Optional custom mastering chain
        
        Returns:
            Mastered mix
        """
        if not self.pedalboard_available:
            return mix
        
        # Use custom chain or look up genre-specific
        if custom_chain is not None:
            board = custom_chain
        else:
            chain_fn = self.MASTERING_CHAINS.get(
                genre, self.MASTERING_CHAINS['default']
            )
            board = chain_fn()
        
        if board is None:
            return mix
        
        try:
            mastered = board(mix, self.sample_rate)
            
            # Log final levels
            peak = np.max(np.abs(mastered))
            rms = np.sqrt(np.mean(mastered**2))
            logger.info("mix_mastered", 
                       peak_db=20*np.log10(peak),
                       rms_db=20*np.log10(rms),
                       genre=genre)
            
            return mastered
        except Exception as e:
            logger.error("mastering_failed", error=str(e))
            return mix
    
    def create_full_mix(self, stems: Dict[str, np.ndarray],
                        genre: str = 'trap',
                        gains: Optional[Dict[str, float]] = None
                        ) -> np.ndarray:
        """Full pipeline: process stems → mix → master.
        
        This is the one-call solution for final beat rendering.
        
        Args:
            stems: Raw stem audio
            genre: Genre for processing decisions
            gains: Optional per-stem gain adjustments (dB)
        
        Returns:
            Final mastered mix
        """
        # Step 1: Process individual stems
        processed_stems = self.process_stems(stems)
        
        # Step 2: Mix stems together
        from sample_engine import SampleEngine
        engine = SampleEngine(sample_rate=self.sample_rate)
        mix = engine.mix_stems(processed_stems, gains=gains, apply_effects=False)
        
        # Step 3: Master the mix
        final = self.master_mix(mix, genre=genre)
        
        return final
