"""Celery tasks for export pipeline."""

import os
import uuid
import asyncio
import subprocess
from typing import Dict, Any
from pathlib import Path

import numpy as np
import structlog

from shared.celery_config import celery_app
from shared.db.database import AsyncSessionLocal
from shared.db.models import Beat
from shared.utils.audio import (
    load_audio, save_audio, create_preview, generate_watermark,
    normalize_audio
)

logger = structlog.get_logger()


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


class ExportPipeline:
    """Handle all export formats and file generation."""
    
    def __init__(self, output_base: str = None):
        self.output_base = output_base or os.getenv('OUTPUT_PATH', '/app/output')
    
    def export_wav(self, audio: np.ndarray, sr: int, beat_id: str,
                   subtype: str = "PCM_24") -> str:
        """Export WAV file."""
        output_dir = os.path.join(self.output_base, 'beats')
        os.makedirs(output_dir, exist_ok=True)
        
        path = os.path.join(output_dir, f'{beat_id}.wav')
        save_audio(audio, path, sr=sr, subtype=subtype)
        
        logger.info("wav_exported", beat_id=beat_id, path=path)
        return path
    
    def export_mp3(self, audio: np.ndarray, sr: int, beat_id: str,
                   bitrate: str = "320k") -> str:
        """Export MP3 file using FFmpeg, pydub, or lameenc fallback."""
        output_dir = os.path.join(self.output_base, 'beats')
        os.makedirs(output_dir, exist_ok=True)
        
        mp3_path = os.path.join(output_dir, f'{beat_id}.mp3')
        
        # Try FFmpeg first
        try:
            import shutil
            if shutil.which('ffmpeg'):
                wav_path = os.path.join(output_dir, f'{beat_id}_temp.wav')
                save_audio(audio, wav_path, sr=sr)
                cmd = [
                    'ffmpeg', '-y', '-i', wav_path,
                    '-codec:a', 'libmp3lame',
                    '-b:a', bitrate,
                    '-q:a', '0',
                    mp3_path
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)
                os.remove(wav_path)
                if result.returncode == 0:
                    logger.info("mp3_exported", beat_id=beat_id, path=mp3_path)
                    return mp3_path
        except Exception:
            pass
        
        # Fallback: use lameenc directly
        try:
            import lameenc
            
            # Convert to int16
            if audio.ndim > 1:
                # Interleave stereo channels
                audio_int16 = (audio.T * 32767).astype(np.int16)
            else:
                audio_int16 = (audio * 32767).astype(np.int16)
            
            encoder = lameenc.Encoder()
            encoder.set_bit_rate(int(bitrate.replace('k', '')))
            encoder.set_in_sample_rate(sr)
            encoder.set_channels(2 if audio.ndim > 1 else 1)
            encoder.set_quality(2)
            
            mp3_data = encoder.encode(audio_int16.tobytes())
            mp3_data += encoder.flush()
            
            with open(mp3_path, 'wb') as f:
                f.write(mp3_data)
            
            logger.info("mp3_exported", beat_id=beat_id, path=mp3_path)
            return mp3_path
        except Exception as e:
            logger.error("mp3_export_failed", error=str(e))
            raise RuntimeError(f"MP3 export failed: {str(e)}")
    
    def export_preview(self, audio: np.ndarray, sr: int, beat_id: str,
                       duration: float = 30.0, watermarked: bool = True) -> str:
        """Export preview clip."""
        output_dir = os.path.join(self.output_base, 'previews')
        os.makedirs(output_dir, exist_ok=True)
        
        # Create preview
        preview = create_preview(audio, sr, duration=duration)
        
        if watermarked:
            preview = generate_watermark(preview, sr)
        
        path = os.path.join(output_dir, f'{beat_id}_preview.mp3')
        
        # Use same MP3 export logic
        try:
            import shutil
            temp_wav = os.path.join(output_dir, f'{beat_id}_temp.wav')
            save_audio(preview, temp_wav, sr=sr)
            
            if shutil.which('ffmpeg'):
                cmd = [
                    'ffmpeg', '-y', '-i', temp_wav,
                    '-codec:a', 'libmp3lame',
                    '-b:a', '192k',
                    path
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)
                os.remove(temp_wav)
                if result.returncode == 0:
                    logger.info("preview_exported", beat_id=beat_id, path=path)
                    return path
            else:
                os.remove(temp_wav)
                raise RuntimeError("No encoder available")
        except Exception:
            pass
        
        # Fallback: use lameenc
        try:
            import lameenc
            
            if preview.ndim > 1:
                audio_int16 = (preview.T * 32767).astype(np.int16)
            else:
                audio_int16 = (preview * 32767).astype(np.int16)
            
            encoder = lameenc.Encoder()
            encoder.set_bit_rate(192)
            encoder.set_in_sample_rate(sr)
            encoder.set_channels(2 if preview.ndim > 1 else 1)
            encoder.set_quality(2)
            
            mp3_data = encoder.encode(audio_int16.tobytes())
            mp3_data += encoder.flush()
            
            with open(path, 'wb') as f:
                f.write(mp3_data)
            
            logger.info("preview_exported", beat_id=beat_id, path=path)
            return path
        except Exception as e:
            raise RuntimeError(f"Preview export failed: {str(e)}")
    
    def export_stems(self, stems: Dict[str, np.ndarray], sr: int, 
                     beat_id: str) -> str:
        """Export individual stems as ZIP."""
        import zipfile
        
        output_dir = os.path.join(self.output_base, 'stems')
        os.makedirs(output_dir, exist_ok=True)
        
        zip_path = os.path.join(output_dir, f'{beat_id}_stems.zip')
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for stem_name, stem_audio in stems.items():
                stem_path = os.path.join(output_dir, f'{beat_id}_{stem_name}.wav')
                save_audio(stem_audio, stem_path, sr=sr)
                zf.write(stem_path, f'{stem_name}.wav')
                os.remove(stem_path)
        
        logger.info("stems_exported", beat_id=beat_id, path=zip_path)
        return zip_path
    
    def copy_midi(self, midi_path: str, beat_id: str) -> str:
        """Copy MIDI file to output."""
        output_dir = os.path.join(self.output_base, 'midi')
        os.makedirs(output_dir, exist_ok=True)
        
        import shutil
        dest = os.path.join(output_dir, f'{beat_id}.mid')
        shutil.copy2(midi_path, dest)
        
        logger.info("midi_copied", beat_id=beat_id, path=dest)
        return dest
    
    def get_file_sizes(self, beat_id: str) -> Dict[str, float]:
        """Get file sizes for all exported formats."""
        sizes = {}
        
        for ext, subdir in [
            ('.wav', 'beats'),
            ('.mp3', 'beats'),
            ('_preview.mp3', 'previews'),
            ('_stems.zip', 'stems'),
            ('.mid', 'midi')
        ]:
            path = os.path.join(self.output_base, subdir, f'{beat_id}{ext}')
            if os.path.exists(path):
                sizes[ext.lstrip('_').replace('.', '')] = round(
                    os.path.getsize(path) / (1024 * 1024), 2
                )
        
        return sizes


# Initialize pipeline
pipeline = ExportPipeline()


@celery_app.task(bind=True, max_retries=2, default_retry_delay=30)
def export_beat(self, state: Dict[str, Any]) -> Dict[str, Any]:
    """Export a beat in all requested formats.
    
    Expects `state` from run_quality_control containing at least:
      - beat_id
      - mastered_path
      - midi_path (optional)
    """
    beat_id = state["beat_id"]
    audio_path = state.get("mastered_path")
    midi_path = state.get("midi_path")
    formats = state.get("export_formats", ['wav', 'mp3', 'preview'])
    
    logger.info("export_started", beat_id=beat_id, formats=formats)
    
    try:
        # Load audio
        audio, sr = load_audio(audio_path)
        
        exported = {}
        
        # Export WAV
        if 'wav' in formats:
            exported['wav'] = pipeline.export_wav(audio, sr, beat_id)
        
        # Export MP3
        if 'mp3' in formats:
            exported['mp3'] = pipeline.export_mp3(audio, sr, beat_id)
        
        # Export preview
        if 'preview' in formats:
            exported['preview'] = pipeline.export_preview(audio, sr, beat_id)
        
        # Copy MIDI
        if midi_path and 'midi' in formats:
            exported['midi'] = pipeline.copy_midi(midi_path, beat_id)
        
        # Get file sizes
        sizes = pipeline.get_file_sizes(beat_id)
        
        logger.info("export_completed", beat_id=beat_id, exported=list(exported.keys()))
        
        # Update beat status: approved → published
        asyncio.run(_update_beat_status(beat_id, 'published'))
        
        # Update state with final export info
        state["exported_files"] = exported
        state["file_sizes_mb"] = sizes
        state["status"] = "published"
        return state
    
    except Exception as e:
        logger.error("export_failed", beat_id=beat_id, error=str(e))
        asyncio.run(_update_beat_status(beat_id, 'failed'))
        self.retry(exc=e)
