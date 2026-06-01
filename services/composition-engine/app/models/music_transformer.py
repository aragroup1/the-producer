"""Music Transformer-based composition model."""

import torch
import torch.nn as nn
from typing import List, Dict, Any, Optional
import numpy as np
import structlog

logger = structlog.get_logger()


class MusicTransformer(nn.Module):
    """Transformer model for symbolic music generation."""
    
    def __init__(
        self,
        vocab_size: int = 388,  # MIDI notes + special tokens
        d_model: int = 512,
        nhead: int = 8,
        num_layers: int = 6,
        dim_feedforward: int = 2048,
        dropout: float = 0.1,
        max_seq_len: int = 2048
    ):
        super().__init__()
        
        self.d_model = d_model
        self.vocab_size = vocab_size
        
        # Embeddings
        self.token_embedding = nn.Embedding(vocab_size, d_model)
        self.position_embedding = nn.Embedding(max_seq_len, d_model)
        
        # Transformer
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers)
        
        # Output
        self.output_projection = nn.Linear(d_model, vocab_size)
        
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Forward pass."""
        batch_size, seq_len = x.shape
        
        # Create position indices
        positions = torch.arange(0, seq_len, device=x.device).unsqueeze(0).expand(batch_size, -1)
        
        # Embeddings
        token_embed = self.token_embedding(x)
        pos_embed = self.position_embedding(positions)
        x = self.dropout(token_embed + pos_embed)
        
        # Transformer
        if mask is not None:
            x = self.transformer(x, src_key_padding_mask=mask)
        else:
            x = self.transformer(x)
        
        # Output
        logits = self.output_projection(x)
        
        return logits
    
    def generate(
        self,
        prompt: torch.Tensor,
        max_length: int = 512,
        temperature: float = 1.0,
        top_k: int = 50,
        top_p: float = 0.9
    ) -> torch.Tensor:
        """Generate sequence autoregressively."""
        self.eval()
        
        generated = prompt.clone()
        
        with torch.no_grad():
            for _ in range(max_length):
                # Forward pass
                logits = self.forward(generated)
                next_token_logits = logits[:, -1, :] / temperature
                
                # Top-k filtering
                if top_k > 0:
                    indices_to_remove = next_token_logits < torch.topk(next_token_logits, top_k)[0][..., -1, None]
                    next_token_logits[indices_to_remove] = float('-inf')
                
                # Top-p filtering
                if top_p < 1.0:
                    sorted_logits, sorted_indices = torch.sort(next_token_logits, descending=True)
                    cumulative_probs = torch.cumsum(torch.softmax(sorted_logits, dim=-1), dim=-1)
                    sorted_indices_to_remove = cumulative_probs > top_p
                    sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
                    sorted_indices_to_remove[..., 0] = 0
                    indices_to_remove = sorted_indices_to_remove.scatter(1, sorted_indices, sorted_indices_to_remove)
                    next_token_logits[indices_to_remove] = float('-inf')
                
                # Sample
                probs = torch.softmax(next_token_logits, dim=-1)
                next_token = torch.multinomial(probs, num_samples=1)
                
                generated = torch.cat([generated, next_token], dim=1)
                
                # Stop if end token (implement as needed)
                # if next_token.item() == END_TOKEN:
                #     break
        
        return generated


class CompositionEngine:
    """High-level composition engine using transformer models."""
    
    def __init__(self, model_path: Optional[str] = None, device: str = "cpu"):
        self.device = device
        self.model = MusicTransformer().to(device)
        
        if model_path:
            try:
                checkpoint = torch.load(model_path, map_location=device)
                self.model.load_state_dict(checkpoint['model_state_dict'])
                logger.info("model_loaded", path=model_path)
            except Exception as e:
                logger.warning("model_load_failed", error=str(e), path=model_path)
        
        self.model.eval()
    
    def generate_melody(
        self,
        key: str = "C",
        scale: str = "minor",
        length_bars: int = 8,
        bpm: int = 140,
        temperature: float = 0.8
    ) -> List[Dict[str, Any]]:
        """Generate a melody line."""
        from shared.utils.midi import SCALES, note_name_to_midi
        
        # Get scale notes
        root_note = note_name_to_midi(key, octave=4)
        scale_intervals = SCALES.get(scale, SCALES["minor"])
        scale_notes = [(root_note + interval) % 12 for interval in scale_intervals]
        
        notes = []
        current_time = 0
        beats_per_bar = 4
        
        for bar in range(length_bars):
            for beat in range(beats_per_bar):
                # Simple melody generation - random scale notes with rhythmic variation
                if np.random.random() > 0.3:  # 70% chance of note on beat
                    note_pitch = root_note + np.random.choice(scale_intervals) + np.random.choice([0, 12])
                    duration = np.random.choice([0.25, 0.5, 1.0])
                    velocity = np.random.randint(60, 110)
                    
                    notes.append({
                        "pitch": int(note_pitch),
                        "velocity": velocity,
                        "start_time": current_time,
                        "duration": duration
                    })
                
                current_time += 1.0  # Advance one beat
        
        return notes
    
    def generate_bassline(
        self,
        chord_progression: List[List[int]],
        bpm: int = 140,
        style: str = "trap"
    ) -> List[Dict[str, Any]]:
        """Generate a bassline following chord progression."""
        notes = []
        current_time = 0
        
        for chord in chord_progression:
            root = chord[0] - 12  # Bass octave
            
            if style in ["trap", "drill"]:
                # Trap bass: long sustained notes with occasional slides
                notes.append({
                    "pitch": root,
                    "velocity": 100,
                    "start_time": current_time,
                    "duration": 2.0  # Half note
                })
                
                # Add octave or fifth on beat 3
                notes.append({
                    "pitch": root + 12 if np.random.random() > 0.5 else root + 7,
                    "velocity": 90,
                    "start_time": current_time + 2.0,
                    "duration": 2.0
                })
            else:
                # Walking bass
                for i in range(4):
                    notes.append({
                        "pitch": root + np.random.choice([0, 3, 5, 7]),
                        "velocity": 85,
                        "start_time": current_time + i,
                        "duration": 0.75
                    })
            
            current_time += 4.0  # Next bar
        
        return notes
    
    def generate_counter_melody(
        self,
        melody: List[Dict[str, Any]],
        key: str = "C",
        scale: str = "minor"
    ) -> List[Dict[str, Any]]:
        """Generate a counter-melody that harmonizes with main melody."""
        from shared.utils.midi import SCALES, note_name_to_midi
        
        root_note = note_name_to_midi(key, octave=5)
        scale_intervals = SCALES.get(scale, SCALES["minor"])
        
        counter_notes = []
        
        for note in melody:
            # Harmonize: third or sixth below
            interval = np.random.choice([3, 4, 7, 8])  # third, fourth, fifth, sixth
            counter_pitch = note["pitch"] - interval
            
            counter_notes.append({
                "pitch": counter_pitch,
                "velocity": note["velocity"] - 20,  # Quieter
                "start_time": note["start_time"],
                "duration": note["duration"] * 2  # Longer, sustained
            })
        
        return counter_notes
    
    def compose_beat(
        self,
        genre: str = "trap",
        bpm: int = 140,
        key: str = "C",
        scale: str = "minor",
        duration_bars: int = 16
    ) -> Dict[str, Any]:
        """Compose a complete beat structure."""
        from shared.utils.midi import generate_chord_progression
        
        logger.info("composing_beat", genre=genre, bpm=bpm, key=key)
        
        # Generate chord progression
        chord_progression = generate_chord_progression(genre, key)
        
        # Generate melody
        melody = self.generate_melody(key, scale, duration_bars, bpm)
        
        # Generate bassline
        bassline = self.generate_bassline(chord_progression, bpm, genre)
        
        # Generate counter-melody
        counter_melody = self.generate_counter_melody(melody, key, scale)
        
        # Generate drum pattern
        from shared.utils.midi import generate_drum_pattern
        drum_pattern = generate_drum_pattern(genre, duration_bars // 4)
        
        composition = {
            "genre": genre,
            "bpm": bpm,
            "key": key,
            "scale": scale,
            "duration_bars": duration_bars,
            "chord_progression": chord_progression,
            "tracks": {
                "melody": melody,
                "bass": bassline,
                "counter_melody": counter_melody,
                "drums": drum_pattern
            }
        }
        
        logger.info("composition_complete", tracks=len(composition["tracks"]))
        
        return composition
