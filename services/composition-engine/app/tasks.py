"""Celery tasks for composition engine — Production Ready."""

import os
import uuid
from typing import Dict, Any

from celery import chain
import structlog

from shared.celery_config import celery_app
from shared.db.database import AsyncSessionLocal
from shared.db.models import Beat, RenderJob
from app.models.music_transformer import CompositionEngine
from app.models.drum_generator import DrumPatternGenerator
from app.models.chord_engine import ChordEngine
from shared.utils.midi import (
    create_midi_file, add_track, set_tempo, add_note, add_chord,
    save_midi, drum_pattern_to_midi
)

logger = structlog.get_logger()

# Initialize engines
composition_engine = CompositionEngine()
chord_engine = ChordEngine()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def generate_midi(self, beat_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Generate MIDI composition for a beat."""
    logger.info("midi_generation_started", beat_id=beat_id)
    
    try:
        genre = params.get('genre', 'trap')
        bpm = params.get('bpm', 140)
        key = params.get('key', 'C')
        mood = params.get('mood', 'dark')
        duration_bars = params.get('duration_bars', 16)
        
        # Generate chord progression
        progression = chord_engine.generate_progression(
            genre=genre,
            mood=mood,
            key=key,
            length=4
        )
        
        # Generate full composition
        composition = composition_engine.compose_beat(
            genre=genre,
            bpm=bpm,
            key=key,
            duration_bars=duration_bars
        )
        
        # Create MIDI file
        midi = create_midi_file(bpm=bpm)
        
        # Add chord track
        chord_track = add_track(midi, "Chords")
        set_tempo(chord_track, bpm)
        
        current_time = 0
        for chord in progression:
            add_chord(
                chord_track,
                chord['notes'],
                velocity=70,
                start_time=current_time,
                duration=480 * 4  # One bar
            )
            current_time += 480 * 4
        
        # Add melody track
        melody_track = add_track(midi, "Melody")
        for note in composition['tracks']['melody']:
            add_note(
                melody_track,
                note['pitch'],
                note['velocity'],
                int(note['start_time'] * 480 / 4 * 4),  # Convert to ticks
                int(note['duration'] * 480 / 4 * 4)
            )
        
        # Add bass track
        bass_track = add_track(midi, "Bass")
        for note in composition['tracks']['bass']:
            add_note(
                bass_track,
                note['pitch'],
                note['velocity'],
                int(note['start_time'] * 480 / 4 * 4),
                int(note['duration'] * 480 / 4 * 4)
            )
        
        # Add drum track
        drum_gen = DrumPatternGenerator(genre)
        drum_pattern = drum_gen.generate(bars=duration_bars // 4)
        
        drum_track = add_track(midi, "Drums")
        drum_midi = drum_pattern_to_midi(drum_pattern, bpm=bpm)
        midi.tracks.append(drum_midi.tracks[0])
        
        # Save MIDI file
        output_dir = os.getenv('OUTPUT_PATH', '/app/output')
        midi_path = os.path.join(output_dir, 'midi', f'{beat_id}.mid')
        save_midi(midi, midi_path)
        
        # Update database
        import asyncio
        asyncio.run(_update_beat_midi(beat_id, midi_path, composition, progression, bpm, key, duration_bars))
        
        logger.info("midi_generation_completed", beat_id=beat_id, path=midi_path)
        
        return {
            "beat_id": beat_id,
            "status": "completed",
            "midi_path": midi_path,
            "composition": composition,
            "progression": progression,
            "bpm": bpm,
            "key": key,
            "duration_bars": duration_bars
        }
    
    except Exception as e:
        logger.error("midi_generation_failed", beat_id=beat_id, error=str(e))
        # Update job status to failed
        import asyncio
        asyncio.run(_update_job_status(beat_id, 'midi_generation', 'failed', str(e)))
        self.retry(exc=e)


async def _update_beat_midi(beat_id: str, midi_path: str, composition: dict, 
                            progression: list, bpm: int, key: str, duration_bars: int):
    """Update beat record with MIDI data."""
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        result = await session.execute(
            select(Beat).where(Beat.id == uuid.UUID(beat_id))
        )
        beat = result.scalar_one_or_none()
        if beat:
            beat.midi_path = midi_path
            beat.composition_params = {
                'progression': progression,
                'tracks': list(composition['tracks'].keys()),
                'bpm': bpm,
                'key': key,
                'duration_bars': duration_bars
            }
            beat.status = 'rendering'
            await session.commit()


async def _update_job_status(beat_id: str, job_type: str, status: str, error: str = None):
    """Update render job status."""
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        result = await session.execute(
            select(RenderJob).where(
                RenderJob.beat_id == uuid.UUID(beat_id),
                RenderJob.job_type == job_type
            )
        )
        job = result.scalar_one_or_none()
        if job:
            job.status = status
            if error:
                job.error_message = error
            await session.commit()


@celery_app.task
def generate_chord_progression_task(
    genre: str,
    mood: str = "dark",
    key: str = "C",
    length: int = 4
) -> Dict[str, Any]:
    """Generate a chord progression."""
    progression = chord_engine.generate_progression(genre, mood, key, length)
    
    return {
        "genre": genre,
        "mood": mood,
        "key": key,
        "progression": progression
    }


@celery_app.task
def generate_drum_pattern_task(
    genre: str,
    bars: int = 4,
    variation_seed: int = None
) -> Dict[str, Any]:
    """Generate a drum pattern."""
    generator = DrumPatternGenerator(genre)
    pattern = generator.generate(bars, variation_seed)
    
    return {
        "genre": genre,
        "bars": bars,
        "pattern": pattern
    }


@celery_app.task(bind=True, max_retries=2)
def generate_beat_workflow(self, beat_id: str, **kwargs):
    """Orchestrate the full beat generation pipeline."""
    logger.info("beat_workflow_started", beat_id=beat_id)
    
    try:
        # Step 1: Generate MIDI
        midi_result = generate_midi.delay(beat_id, kwargs)
        
        # The pipeline continues via Celery callbacks
        # Each subsequent task is triggered by the previous task's success
        # This is handled by the task chaining in the individual services
        
        return {
            "beat_id": beat_id,
            "status": "workflow_started",
            "midi_task_id": midi_result.id
        }
    
    except Exception as e:
        logger.error("beat_workflow_failed", beat_id=beat_id, error=str(e))
        raise self.retry(exc=e)


@celery_app.task
def batch_generate_beats(genre_ids: list, count_per_genre: int, 
                         batch_id: str = None, priority: int = 5):
    """Generate beats in batches for cost efficiency."""
    logger.info("batch_generation_started", batch_id=batch_id, total=len(genre_ids) * count_per_genre)
    
    for genre_id in genre_ids:
        for i in range(count_per_genre):
            beat_id = str(uuid.uuid4())
            
            # Queue individual beat generation
            celery_app.send_task(
                'tasks.generate_beat_workflow',
                args=[beat_id],
                kwargs={
                    'genre_id': genre_id,
                    'variation_seed': i,
                    'batch_id': batch_id
                },
                queue='midi',
                priority=priority
            )
    
    return {
        "batch_id": batch_id,
        "status": "queued",
        "total_beats": len(genre_ids) * count_per_genre
    }
