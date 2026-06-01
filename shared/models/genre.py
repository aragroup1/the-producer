"""Genre model definitions."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field


class Genre(BaseModel):
    """Music genre with production parameters."""
    id: Optional[UUID] = None
    name: str
    slug: str
    parent_genre_id: Optional[UUID] = None
    bpm_range_min: int = 60
    bpm_range_max: int = 200
    key_signatures: List[str] = Field(default_factory=list)
    typical_structure: Dict[str, Any] = Field(default_factory=dict)
    description: Optional[str] = None
    trending_score: float = 0.0
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class GenreCreate(BaseModel):
    """Request model for creating a genre."""
    name: str
    slug: str
    bpm_range_min: int = 60
    bpm_range_max: int = 200
    key_signatures: List[str] = Field(default_factory=list)
    typical_structure: Dict[str, Any] = Field(default_factory=dict)
    description: Optional[str] = None


class Trend(BaseModel):
    """Trend data from external sources."""
    id: Optional[UUID] = None
    source: str  # google, youtube, tiktok, spotify, beatstars
    keyword: str
    genre_id: Optional[UUID] = None
    volume_score: Optional[float] = None
    growth_rate: Optional[float] = None
    rank: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: Optional[datetime] = None
    
    class Config:
        from_attributes = True
