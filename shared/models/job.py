"""Render job model definitions."""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    """Render job statuses."""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class RenderJob(BaseModel):
    """A render job in the processing queue."""
    id: Optional[UUID] = None
    beat_id: Optional[UUID] = None
    job_type: str  # midi_generation, sound_assignment, vst_render, mixing, mastering, export, qc, shopify
    status: JobStatus = JobStatus.QUEUED
    worker_id: Optional[str] = None
    priority: int = 5
    retry_count: int = 0
    error_message: Optional[str] = None
    result_data: Dict[str, Any] = Field(default_factory=dict)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class JobCreate(BaseModel):
    """Request model for creating a render job."""
    beat_id: UUID
    job_type: str
    priority: int = 5


class JobUpdate(BaseModel):
    """Request model for updating a render job."""
    status: Optional[JobStatus] = None
    worker_id: Optional[str] = None
    error_message: Optional[str] = None
    result_data: Optional[Dict[str, Any]] = None
