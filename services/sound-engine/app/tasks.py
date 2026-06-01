"""Celery tasks for sound engine — Sample-Based Rendering."""

import os
import uuid
import asyncio
from typing import Dict, Any

import structlog

from shared.celery_config import celery_app
from shared.db.database import AsyncSessionLocal
from shared.db.models import Beat
from app.sound_selector import SoundSelector
from app.sample_engine import SampleEngine

logger = structlog.get_logger()

# Initialize components
sound_selector = SoundSelector()
sample_engine = SampleEngine()


async def _update_beat_status(beat_id: str, status: str, error: str = None):
    """Update beat status in the database."""
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        result = await session.execute(
            select(Beat).where(Beat.id == uuid.UUID(beat_id))
        )
        beat = result.scalar_one_or_none()
        if beat:
            beat.status = status
            await session.commit()
            logger.info("beat_status_updated", beat_id=beat_id, status=status)
        else:
            logger.warning("beat_not_found_for_status_update", beat_id=beat_id)


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
def render_audio(self, state: Dict[str, Any]) -> Dict[str, Any]:
    """Render composition to audio using sample-based engine.
    
    Expects `state` from generate_midi containing at least:
      - beat_id
      - composition
      - genre
      - bpm
    """
    beat_id = state["beat_id"]
    composition_data = state.get("composition", {})
    genre = state.get("genre", "trap")
    bpm = state.get("bpm", 140)
    humanize_ms = state.get("humanize_ms", 5.0)
    
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
        
        # Update beat status: rendering → mixing
        asyncio.run(_update_beat_status(beat_id, 'mixing'))
        
        # Update state for downstream tasks
        state["audio_path"] = mix_path
        state["stem_paths"] = stem_paths
        state["sample_rate"] = sample_engine.sample_rate
        state["stem_count"] = len(stems)
        return state
    
    except Exception as e:
        logger.error("audio_render_failed", beat_id=beat_id, error=str(e))
        asyncio.run(_update_beat_status(beat_id, 'failed'))
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
