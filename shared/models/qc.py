"""Quality control model definitions."""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field


class QCLog(BaseModel):
    """A quality control check result."""
    id: Optional[UUID] = None
    beat_id: Optional[UUID] = None
    check_type: str  # spectral_analysis, loudness, repetition, clipping, arrangement, drum_punch
    score: Optional[float] = None
    passed: Optional[bool] = None
    details: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class QCThresholds(BaseModel):
    """Quality control thresholds."""
    min_loudness_lufs: float = -16.0
    max_true_peak_db: float = -1.0
    min_quality_score: float = 6.0
    max_repetition_score: float = 0.7
    min_drum_punch: float = 0.5
    min_arrangement_score: float = 0.6
