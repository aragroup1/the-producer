"""Reference beat analyzer — extracts features from hit beats for training data."""

import os
import json
import structlog
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

logger = structlog.get_logger()


@dataclass
class BeatFeatures:
    """Extracted features from a reference beat."""
    # Timing
    bpm: float
    duration_seconds: float
    
    # Structure
    has_intro: bool
    has_hook: bool
    has_verse: bool
    has_bridge: bool
    has_outro: bool
    
    # Energy dynamics
    energy_curve: List[float]  # Per-bar energy
    drop_intensity: float  # 0-1
    
    # Spectral
    spectral_centroid_mean: float
    spectral_rolloff_mean: float
    spectral_bandwidth_mean: float
    
    # Low-end
    sub_bass_presence: float  # 0-1
    kick_808_clarity: float  # 0-1
    
    # Rhythm
    hihat_density: float  # Notes per bar
    kick_pattern_complexity: float  # 0-1
    snare_syncopation: float  # 0-1
    
    # Melodic
    melodic_range_semitones: int
    chord_progression_type: str
    
    # Metadata
    source: str  # Artist/producer name
    year: int
    genre_substyle: str
    
    def to_dict(self) -> Dict:
        return asdict(self)


class ReferenceBeatAnalyzer:
    """Analyze reference beats to build training dataset."""
    
    def __init__(self, reference_dir: str = "references"):
        self.reference_dir = Path(reference_dir)
        self.analyzed_beats: List[BeatFeatures] = []
        
    def analyze_audio_file(self, filepath: str) -> Optional[BeatFeatures]:
        """Analyze a single reference beat file.
        
        Uses librosa for feature extraction. Falls back to manual estimation
        if librosa is not available.
        """
        try:
            import librosa
            
            # Load audio
            y, sr = librosa.load(filepath, sr=44100, mono=True)
            
            # BPM detection
            tempo = librosa.beat.tempo(y=y, sr=sr)[0]
            
            # Duration
            duration = librosa.get_duration(y=y, sr=sr)
            
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            spectral_rolloffs = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
            spectral_bandwidths = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
            
            # Energy curve (per-bar)
            hop_length = 512
            rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]
            
            # Convert to bar-level energy (assuming 4/4)
            beats_per_second = tempo / 60
            samples_per_bar = int((sr / hop_length) * 4 / beats_per_second)
            
            energy_curve = []
            for i in range(0, len(rms), samples_per_bar):
                bar_rms = rms[i:i + samples_per_bar]
                if len(bar_rms) > 0:
                    energy_curve.append(float(np.mean(bar_rms)))
            
            # Detect structure from energy curve
            has_intro = len(energy_curve) > 4 and energy_curve[0] < np.mean(energy_curve) * 0.7
            has_hook = len(energy_curve) > 8 and max(energy_curve[4:8]) > np.mean(energy_curve) * 1.3
            
            # Low-end analysis
            stft = np.abs(librosa.stft(y))
            freqs = librosa.fft_frequencies(sr=sr)
            
            sub_bass_mask = (freqs >= 20) & (freqs <= 60)
            bass_mask = (freqs >= 60) & (freqs <= 250)
            
            sub_bass_energy = np.mean(stft[sub_bass_mask, :])
            bass_energy = np.mean(stft[bass_mask, :])
            
            sub_bass_presence = min(1.0, sub_bass_energy / (bass_energy + 1e-10))
            
            # Detect onset density for hihat estimation
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            onset_frames = librosa.onset.onset_detect(
                onset_envelope=onset_env, sr=sr, 
                wait=int(sr * 0.05 / hop_length)  # 50ms minimum
            )
            
            # Estimate hihat density from high-frequency onsets
            if len(onset_frames) > 0:
                hihat_density = len(onset_frames) / (duration / 60 * tempo / 4)
                hihat_density = min(16.0, hihat_density)  # Cap at 16th notes
            else:
                hihat_density = 4.0
            
            return BeatFeatures(
                bpm=float(tempo),
                duration_seconds=float(duration),
                has_intro=has_intro,
                has_hook=has_hook,
                has_verse=len(energy_curve) > 12,
                has_bridge=len(energy_curve) > 20,
                has_outro=duration > 120,
                energy_curve=energy_curve[:32],  # Limit to first 32 bars
                drop_intensity=max(energy_curve) / (np.mean(energy_curve) + 1e-10) if energy_curve else 1.0,
                spectral_centroid_mean=float(np.mean(spectral_centroids)),
                spectral_rolloff_mean=float(np.mean(spectral_rolloffs)),
                spectral_bandwidth_mean=float(np.mean(spectral_bandwidths)),
                sub_bass_presence=float(sub_bass_presence),
                kick_808_clarity=0.7,  # Would need more sophisticated analysis
                hihat_density=float(hihat_density),
                kick_pattern_complexity=0.5,  # Would need transient analysis
                snare_syncopation=0.3,  # Would need pattern detection
                melodic_range_semitones=24,  # Would need pitch detection
                chord_progression_type="unknown",
                source="reference",
                year=2024,
                genre_substyle="trap"
            )
            
        except ImportError:
            logger.warning("librosa not available, using manual estimation")
            return self._manual_estimate(filepath)
        except Exception as e:
            logger.error("Failed to analyze", filepath=filepath, error=str(e))
            return None
    
    def _manual_estimate(self, filepath: str) -> BeatFeatures:
        """Manual estimation without librosa."""
        import wave
        
        with wave.open(filepath, 'rb') as wf:
            duration = wf.getnframes() / wf.getframerate()
        
        # Default estimates
        return BeatFeatures(
            bpm=140.0,
            duration_seconds=duration,
            has_intro=duration > 30,
            has_hook=duration > 60,
            has_verse=duration > 90,
            has_bridge=duration > 120,
            has_outro=duration > 150,
            energy_curve=[0.5] * 8,
            drop_intensity=1.5,
            spectral_centroid_mean=3000.0,
            spectral_rolloff_mean=6000.0,
            spectral_bandwidth_mean=2000.0,
            sub_bass_presence=0.6,
            kick_808_clarity=0.7,
            hihat_density=8.0,
            kick_pattern_complexity=0.5,
            snare_syncopation=0.3,
            melodic_range_semitones=24,
            chord_progression_type="unknown",
            source="reference",
            year=2024,
            genre_substyle="trap"
        )
    
    def analyze_directory(self, directory: str, metadata_file: Optional[str] = None) -> List[BeatFeatures]:
        """Analyze all audio files in a directory."""
        directory = Path(directory)
        
        # Load metadata if provided
        metadata = {}
        if metadata_file and Path(metadata_file).exists():
            with open(metadata_file) as f:
                metadata = json.load(f)
        
        audio_extensions = {'.wav', '.mp3', '.flac', '.aiff'}
        
        for filepath in directory.rglob('*'):
            if filepath.suffix.lower() in audio_extensions:
                logger.info("Analyzing reference beat", filepath=str(filepath))
                
                features = self.analyze_audio_file(str(filepath))
                if features:
                    # Apply metadata if available
                    file_key = filepath.stem
                    if file_key in metadata:
                        meta = metadata[file_key]
                        features.source = meta.get('producer', 'unknown')
                        features.year = meta.get('year', 2024)
                        features.genre_substyle = meta.get('substyle', 'trap')
                    
                    self.analyzed_beats.append(features)
        
        logger.info("Analysis complete", count=len(self.analyzed_beats))
        return self.analyzed_beats
    
    def build_statistical_profile(self) -> Dict[str, any]:
        """Build statistical profile from analyzed beats."""
        if not self.analyzed_beats:
            logger.warning("No beats analyzed yet")
            return {}
        
        bpms = [b.bpm for b in self.analyzed_beats]
        durations = [b.duration_seconds for b in self.analyzed_beats]
        hihat_densities = [b.hihat_density for b in self.analyzed_beats]
        sub_bass_presences = [b.sub_bass_presence for b in self.analyzed_beats]
        
        profile = {
            "count": len(self.analyzed_beats),
            "bpm": {
                "mean": float(np.mean(bpms)),
                "std": float(np.std(bpms)),
                "min": float(np.min(bpms)),
                "max": float(np.max(bpms)),
                "median": float(np.median(bpms)),
            },
            "duration": {
                "mean": float(np.mean(durations)),
                "std": float(np.std(durations)),
                "min": float(np.min(durations)),
                "max": float(np.max(durations)),
            },
            "hihat_density": {
                "mean": float(np.mean(hihat_densities)),
                "std": float(np.std(hihat_densities)),
            },
            "sub_bass_presence": {
                "mean": float(np.mean(sub_bass_presences)),
                "std": float(np.std(sub_bass_presences)),
            },
            "structure_frequency": {
                "intro": sum(1 for b in self.analyzed_beats if b.has_intro) / len(self.analyzed_beats),
                "hook": sum(1 for b in self.analyzed_beats if b.has_hook) / len(self.analyzed_beats),
                "verse": sum(1 for b in self.analyzed_beats if b.has_verse) / len(self.analyzed_beats),
                "bridge": sum(1 for b in self.analyzed_beats if b.has_bridge) / len(self.analyzed_beats),
                "outro": sum(1 for b in self.analyzed_beats if b.has_outro) / len(self.analyzed_beats),
            },
            "source_breakdown": self._count_by_source(),
        }
        
        return profile
    
    def _count_by_source(self) -> Dict[str, int]:
        """Count beats by producer/source."""
        counts = {}
        for beat in self.analyzed_beats:
            counts[beat.source] = counts.get(beat.source, 0) + 1
        return counts
    
    def save_profile(self, output_path: str = "reference_profile.json"):
        """Save statistical profile to JSON."""
        profile = self.build_statistical_profile()
        
        # Also save individual features
        features_data = [b.to_dict() for b in self.analyzed_beats]
        
        output = {
            "statistical_profile": profile,
            "individual_features": features_data,
            "generated_at": str(np.datetime64('now')),
        }
        
        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2)
        
        logger.info("Profile saved", path=output_path, beats=len(features_data))
        return output_path
    
    def get_generation_guidelines(self) -> Dict[str, any]:
        """Get generation guidelines based on analyzed references."""
        profile = self.build_statistical_profile()
        
        if not profile:
            logger.warning("No data, using defaults")
            return self._default_guidelines()
        
        bpm_stats = profile["bpm"]
        
        return {
            "bpm_range": (
                max(120, bpm_stats["mean"] - bpm_stats["std"]),
                min(180, bpm_stats["mean"] + bpm_stats["std"])
            ),
            "target_bpm": bpm_stats["median"],
            "duration_range": (120, 240),
            "hihat_density_target": profile["hihat_density"]["mean"],
            "sub_bass_target": profile["sub_bass_presence"]["mean"],
            "structure_recommendations": {
                section: freq > 0.5 
                for section, freq in profile["structure_frequency"].items()
            },
            "confidence": min(1.0, len(self.analyzed_beats) / 100),
        }
    
    def _default_guidelines(self) -> Dict[str, any]:
        """Default guidelines when no references analyzed."""
        return {
            "bpm_range": (135, 150),
            "target_bpm": 142,
            "duration_range": (120, 240),
            "hihat_density_target": 8.0,
            "sub_bass_target": 0.6,
            "structure_recommendations": {
                "intro": True,
                "hook": True,
                "verse": True,
                "bridge": False,
                "outro": True,
            },
            "confidence": 0.0,
        }


class ReferenceTrainingData:
    """Manage training data from reference beats."""
    
    def __init__(self, data_dir: str = "training_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
    def add_reference(self, features: BeatFeatures, label: str = "hit"):
        """Add a reference beat to training data."""
        data = {
            "features": features.to_dict(),
            "label": label,
            "timestamp": str(np.datetime64('now')),
        }
        
        # Save to file
        filename = f"{features.source}_{features.year}_{np.random.randint(10000)}.json"
        filepath = self.data_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        return filepath
    
    def load_training_set(self) -> Tuple[List[Dict], List[str]]:
        """Load all training data. Returns (features, labels)."""
        features = []
        labels = []
        
        for filepath in self.data_dir.glob('*.json'):
            with open(filepath) as f:
                data = json.load(f)
                features.append(data["features"])
                labels.append(data["label"])
        
        return features, labels
    
    def get_feature_vectors(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get numerical feature vectors for ML training."""
        features, labels = self.load_training_set()
        
        if not features:
            return np.array([]), np.array([])
        
        # Extract numerical features
        numerical_features = []
        for feat in features:
            vec = [
                feat["bpm"],
                feat["duration_seconds"],
                feat["drop_intensity"],
                feat["spectral_centroid_mean"],
                feat["sub_bass_presence"],
                feat["hihat_density"],
                feat["kick_pattern_complexity"],
                feat["snare_syncopation"],
                feat["melodic_range_semitones"],
                1.0 if feat["has_intro"] else 0.0,
                1.0 if feat["has_hook"] else 0.0,
                1.0 if feat["has_verse"] else 0.0,
            ]
            numerical_features.append(vec)
        
        # Encode labels
        label_map = {"hit": 1.0, "average": 0.5, "miss": 0.0}
        y = np.array([label_map.get(l, 0.5) for l in labels])
        
        return np.array(numerical_features), y
