"""Beat management API endpoints — Production Ready."""

import uuid
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, asc
from pydantic import BaseModel, Field
import structlog

from shared.models.beat import Beat, BeatCreate, BeatUpdate, BeatListResponse, BeatStatus
from shared.db.database import get_db
from shared.db.models import Beat as BeatModel, Genre, RenderJob
from shared.utils.security import validate_beat_id, BeatGenerationRequest, BatchGenerationRequest
from app.routers.auth import get_current_active_user
from shared.celery_config import celery_app

logger = structlog.get_logger()
router = APIRouter()


# ─── Endpoints ─────────────────────────────────────────────────────

@router.post("/generate", status_code=status.HTTP_202_ACCEPTED)
async def generate_beat(
    request: BeatGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Queue a new beat for generation."""
    
    # Validate genre exists
    result = await db.execute(select(Genre).where(Genre.id == uuid.UUID(request.genre_id)))
    genre = result.scalar_one_or_none()
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")
    
    beat_id = uuid.uuid4()
    
    # Create beat record in database
    beat = BeatModel(
        id=beat_id,
        title=request.title or f"{genre.name} Beat #{beat_id.hex[:8]}",
        slug=f"beat-{beat_id.hex[:12]}",
        genre_id=uuid.UUID(request.genre_id),
        bpm=request.bpm or genre.bpm_range_min + (genre.bpm_range_max - genre.bpm_range_min) // 2,
        key_signature=request.key_signature,
        mood=request.mood,
        duration_seconds=request.duration_seconds,
        status="draft",
        tags=request.tags,
        ai_model_version="1.0.0",
    )
    db.add(beat)
    await db.commit()
    
    logger.info(
        "beat_generation_requested",
        beat_id=str(beat_id),
        genre_id=request.genre_id,
        bpm=beat.bpm,
        user_id=str(current_user.id),
        priority=request.priority
    )
    
    # Queue Celery task
    celery_app.send_task(
        'tasks.generate_beat_workflow',
        args=[str(beat_id)],
        kwargs={
            'genre': genre.name.lower(),
            'bpm': beat.bpm,
            'key': request.key_signature or 'C',
            'mood': request.mood or 'dark',
            'duration_seconds': request.duration_seconds,
        },
        queue='midi',
        priority=request.priority
    )
    
    return {
        "beat_id": beat_id,
        "status": "queued",
        "message": "Beat generation has been queued",
        "estimated_time": "2-5 minutes"
    }


@router.post("/batch-generate", status_code=status.HTTP_202_ACCEPTED)
async def batch_generate_beats(
    request: BatchGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Queue multiple beats for batch generation."""
    
    # Validate all genres exist
    for genre_id in request.genre_ids:
        result = await db.execute(select(Genre).where(Genre.id == uuid.UUID(genre_id)))
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail=f"Genre not found: {genre_id}")
    
    batch_id = uuid.uuid4()
    total_beats = len(request.genre_ids) * request.count_per_genre
    
    logger.info(
        "batch_generation_requested",
        batch_id=str(batch_id),
        total_beats=total_beats,
        user_id=str(current_user.id),
        genres=request.genre_ids
    )
    
    # Queue batch task
    celery_app.send_task(
        'tasks.batch_generate_beats',
        args=[request.genre_ids, request.count_per_genre],
        kwargs={'batch_id': str(batch_id), 'priority': request.priority},
        queue='midi',
        priority=request.priority
    )
    
    return {
        "batch_id": batch_id,
        "total_beats": total_beats,
        "status": "queued",
        "message": f"Batch generation of {total_beats} beats has been queued"
    }


@router.get("", response_model=BeatListResponse)
async def list_beats(
    status: Optional[str] = None,
    genre_id: Optional[uuid.UUID] = None,
    bpm_min: Optional[int] = Query(None, ge=60),
    bpm_max: Optional[int] = Query(None, le=200),
    mood: Optional[str] = None,
    quality_min: Optional[float] = Query(None, ge=0, le=10),
    qc_passed: Optional[bool] = None,
    shopify_status: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List beats with filtering and pagination."""
    
    query = select(BeatModel)
    
    # Apply filters
    if status:
        query = query.where(BeatModel.status == status)
    if genre_id:
        query = query.where(BeatModel.genre_id == genre_id)
    if bpm_min:
        query = query.where(BeatModel.bpm >= bpm_min)
    if bpm_max:
        query = query.where(BeatModel.bpm <= bpm_max)
    if mood:
        query = query.where(BeatModel.mood == mood)
    if quality_min:
        query = query.where(BeatModel.quality_score >= quality_min)
    if qc_passed is not None:
        query = query.where(BeatModel.qc_passed == qc_passed)
    if shopify_status:
        query = query.where(BeatModel.shopify_status == shopify_status)
    if search:
        query = query.where(BeatModel.title.ilike(f"%{search}%"))
    
    # Get total count
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()
    
    # Apply sorting
    sort_column = getattr(BeatModel, sort_by, BeatModel.created_at)
    if sort_order == 'desc':
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    result = await db.execute(query)
    beats = result.scalars().all()
    
    return BeatListResponse(
        items=[Beat.model_validate(b) for b in beats],
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size
    )


@router.get("/{beat_id}")
async def get_beat(
    beat_id: uuid.UUID,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a single beat by ID."""
    result = await db.execute(select(BeatModel).where(BeatModel.id == beat_id))
    beat = result.scalar_one_or_none()
    
    if not beat:
        raise HTTPException(status_code=404, detail="Beat not found")
    
    return Beat.model_validate(beat)


@router.patch("/{beat_id}")
async def update_beat(
    beat_id: uuid.UUID,
    update: BeatUpdate,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update beat metadata."""
    result = await db.execute(select(BeatModel).where(BeatModel.id == beat_id))
    beat = result.scalar_one_or_none()
    
    if not beat:
        raise HTTPException(status_code=404, detail="Beat not found")
    
    # Update fields
    update_data = update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(beat, field, value)
    
    await db.commit()
    await db.refresh(beat)
    
    return Beat.model_validate(beat)


@router.delete("/{beat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_beat(
    beat_id: uuid.UUID,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a beat and associated files."""
    result = await db.execute(select(BeatModel).where(BeatModel.id == beat_id))
    beat = result.scalar_one_or_none()
    
    if not beat:
        raise HTTPException(status_code=404, detail="Beat not found")
    
    # TODO: Delete associated files from storage
    
    await db.delete(beat)
    await db.commit()
    
    logger.info("beat_deleted", beat_id=str(beat_id), user_id=str(current_user.id))


@router.post("/{beat_id}/approve")
async def approve_beat(
    beat_id: uuid.UUID,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Approve a beat for publishing."""
    result = await db.execute(select(BeatModel).where(BeatModel.id == beat_id))
    beat = result.scalar_one_or_none()
    
    if not beat:
        raise HTTPException(status_code=404, detail="Beat not found")
    
    beat.status = "approved"
    beat.qc_passed = True
    await db.commit()
    
    logger.info("beat_approved", beat_id=str(beat_id), user_id=str(current_user.id))
    
    # Trigger Shopify upload
    celery_app.send_task(
        'tasks.upload_beat_to_shopify',
        args=[str(beat_id)],
        queue='shopify'
    )
    
    return {"beat_id": beat_id, "status": "approved"}


@router.post("/{beat_id}/reject")
async def reject_beat(
    beat_id: uuid.UUID,
    reason: Optional[str] = None,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Reject a beat."""
    result = await db.execute(select(BeatModel).where(BeatModel.id == beat_id))
    beat = result.scalar_one_or_none()
    
    if not beat:
        raise HTTPException(status_code=404, detail="Beat not found")
    
    beat.status = "rejected"
    beat.qc_passed = False
    await db.commit()
    
    logger.info("beat_rejected", beat_id=str(beat_id), reason=reason, user_id=str(current_user.id))
    
    return {"beat_id": beat_id, "status": "rejected", "reason": reason}


@router.post("/{beat_id}/regenerate")
async def regenerate_beat(
    beat_id: uuid.UUID,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Regenerate a beat with same parameters."""
    result = await db.execute(select(BeatModel).where(BeatModel.id == beat_id))
    beat = result.scalar_one_or_none()
    
    if not beat:
        raise HTTPException(status_code=404, detail="Beat not found")
    
    # Reset status and re-queue
    beat.status = "draft"
    await db.commit()
    
    logger.info("beat_regenerate_requested", beat_id=str(beat_id), user_id=str(current_user.id))
    
    # Re-queue generation
    celery_app.send_task(
        'tasks.generate_beat_workflow',
        args=[str(beat_id)],
        queue='midi'
    )
    
    return {"beat_id": beat_id, "status": "queued_for_regeneration"}
