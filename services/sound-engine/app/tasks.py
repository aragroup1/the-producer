"""Celery tasks for sound engine — Sample-Based Rendering."""

import os
from typing import Dict, Any

from celery import Celery
import structlog

from app.sound_selector import SoundSelector
from app.sample_engine import SampleEngine

logger = structlog.get_logger()

# Initialize Celery
celery_app = Celery('sound')
celery_app.conf.broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
celery_app.conf.result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Initialize components
sound_selector = SoundSelector()
sample_engine = SampleEngine()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def assign_sounds(self, beat_id: str, composition_data: Dict[str, Any]) -> Dict[str, Any]:
    """Assign sounds to a composition."""
    logger.info("sound_assignment_started", beat_id=beat_id)
    
    try:
        genre = composition_data.get('genre', 'trap')
        mood = composition_data.get('mood', 'dark')
        
        # Assign sounds
        sound_map = sound_selector.assign_sounds(
            genre=genre,
            mood=mood,
            composition_data=composition_data
        )
        
        logger.info("sound_assignment_completed", beat_id=beat_id)
        
        return {
            "beat_id": beat_id,
            "status": "completed",
            "sound_map": sound_map
        }
    
    except Exception as e:
        logger.error("sound_assignment_failed", beat_id=beat_id, error=str(e))
        self.retry(exc=e)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=30)
def render_audio(self, beat_id: str, composition_data: Dict[str, Any],
                 genre: str = 'trap', bpm: int = 140,
                 humanize_ms: float = 5.0) -> Dict[str, Any]:
    """Render composition to audio using sample-based engine.
    
    Replaces the old FluidSynth/VST rendering with high-quality
    sample-based rendering that produces professional-sounding beats.
    """
    logger.info("audio_render_started", beat_id=beat_id, genre=genre, bpm=bpm)
    
    try:
        output_dir = os.path.join(os.getenv('OUTPUT_PATH', '/app/output'), 'beats')
        stems_dir = os.path.join(os.getenv('OUTPUT_PATH', '/app/output'), 'stems')
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(stems_dir, exist_ok=True)
        
        # Render all stems using sample engine
        stems = sample_engine.render_beat(
            composition_data,
            genre=genre,
            bpm=bpm,
            humanize_ms=humanize_ms
        )
        
        if not stems:
            raise RuntimeError("No stems rendered")
        
        # Save individual stems
        stem_paths = sample_engine.save_stems(stems, beat_id, stems_dir)
        
        # Mix to stereo
        mix = sample_engine.mix_stems(stems)
        
        # Save mixed audio
        import soundfile as sf
        mix_path = os.path.join(output_dir, f'{beat_id}_raw.wav')
        sf.write(mix_path, mix.T, sample_engine.sample_rate, subtype='PCM_24')
        
        logger.info("audio_render_completed", 
                   beat_id=beat_id, 
                   output=mix_path,
                   stems=list(stem_paths.keys()))
        
        return {
            "beat_id": beat_id,
            "status": "completed",
            "audio_path": mix_path,
            "stem_paths": stem_paths,
            "sample_rate": sample_engine.sample_rate,
            "stem_count": len(stems)
        }
    
    except Exception as e:
        logger.error("audio_render_failed", beat_id=beat_id, error=str(e))
        self.retry(exc=e)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=30)
def render_vst_audio(self, beat_id: str, midi_path: str, 
                     sound_map: Dict[str, Any]) -> Dict[str, Any]:
    """Legacy: Render MIDI to audio using VST/soundfonts.
    
    DEPRECATED: Use render_audio() for new beats.
    Kept for backward compatibility.
    """
    logger.info("vst_render_started", beat_id=beat_id, midi=midi_path)
    
    try:
        from app.vst_host import FluidSynthHost
        fluidsynth = FluidSynthHost()
        
        output_dir = os.path.join(os.getenv('OUTPUT_PATH', '/app/output'), 'beats')
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, f'{beat_id}_raw.wav')
        
        # Render with FluidSynth
        rendered_path = fluidsynth.render_midi(midi_path, output_path)
        
        logger.info("vst_render_completed", beat_id=beat_id, output=rendered_path)
        
        return {
            "beat_id": beat_id,
            "status": "completed",
            "audio_path": rendered_path,
            "sample_rate": fluidsynth.sample_rate
        }
    
    except Exception as e:
        logger.error("vst_render_failed", beat_id=beat_id, error=str(e))
        self.retry(exc=e)


@celery_app.task
def list_available_sounds() -> Dict[str, Any]:
    """List all available sounds and samples."""
    soundfonts = sound_selector.get_available_soundfonts()
    
    # List sample categories
    sample_categories = {}
    sample_base = sample_engine.sample_base
    
    for parent in ['drums', 'melodic', 'fx']:
        parent_path = os.path.join(sample_base, parent)
        if os.path.exists(parent_path):
            for category in os.listdir(parent_path):
                cat_path = os.path.join(parent_path, category)
                if os.path.isdir(cat_path):
                    genres = [g for g in os.listdir(cat_path) 
                             if os.path.isdir(os.path.join(cat_path, g))]
                    sample_categories.setdefault(parent, {})[category] = genres
    
    return {
        "soundfonts": soundfonts,
        "sample_categories": sample_categories,
        "sample_base": sample_base
    }
