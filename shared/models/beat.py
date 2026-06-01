"""Beat model definitions."""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field


class BeatStatus(str, Enum):
    """Beat production workflow statuses."""
    DRAFT = "draft"
    RENDERING = "rendering"
    MIXING = "mixing"
    MASTERING = "mastering"
    QC = "qc"
    APPROVED = "approved"
    REJECTED = "rejected"
    PUBLISHED = "published"
    FAILED = "failed"


class BeatSection(BaseModel):
    """A section within a beat arrangement."""
    id: Optional[UUID] = None
    beat_id: Optional[UUID] = None
    section_type: str  # intro, hook, verse, bridge, outro, fill
    start_bar: int
    end_bar: int
    bpm: Optional[int] = None
    key_signature: Optional[str] = None
    midi_events: Dict[str, Any] = Field(default_factory=dict)
    automation_data: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None


class Beat(BaseModel):
    """A generated beat/instrumental."""
    id: Optional[UUID] = None
    title: str
    slug: str
    genre_id: Optional[UUID] = None
    bpm: int
    key_signature: Optional[str] = None
    duration_seconds: Optional[int] = None
    mood: Optional[str] = None
    
    status: BeatStatus = BeatStatus.DRAFT
    
    # Composition
    midi_data: Dict[str, Any] = Field(default_factory=dict)
    composition_params: Dict[str, Any] = Field(default_factory=dict)
    
    # Sound
    sound_assignments: Dict[str, Any] = Field(default_factory=dict)
    
    # Mixing
    mix_chain_id: Optional[UUID] = None
    mix_params: Dict[str, Any] = Field(default_factory=dict)
    
    # Mastering
    master_params: Dict[str, Any] = Field(default_factory=dict)
    loudness_lufs: Optional[float] = None
    true_peak_db: Optional[float] = None
    
    # Quality
    quality_score: Optional[float] = None
    qc_results: Dict[str, Any] = Field(default_factory=dict)
    qc_passed: Optional[bool] = None
    
    # Files
    wav_path: Optional[str] = None
    mp3_path: Optional[str] = None
    stems_path: Optional[str] = None
    midi_path: Optional[str] = None
    preview_path: Optional[str] = None
    watermarked_preview_path: Optional[str] = None
    cover_art_path: Optional[str] = None
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    description: Optional[str] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    
    # Shopify
    shopify_product_id: Optional[str] = None
    shopify_status: Optional[str] = None
    
    # Analytics
    view_count: int = 0
    play_count: int = 0
    wishlist_count: int = 0
    cart_add_count: int = 0
    sales_count: int = 0
    revenue: float = 0.0
    
    # Generation
    generation_cost: Optional[float] = None
    generation_time_seconds: Optional[int] = None
    ai_model_version: Optional[str] = None
    batch_id: Optional[UUID] = None
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class BeatCreate(BaseModel):
    """Request model for creating a beat."""
    genre_id: UUID
    bpm: Optional[int] = None
    key_signature: Optional[str] = None
    mood: Optional[str] = None
    duration_seconds: Optional[int] = Field(default=180, ge=60, le=300)
    title: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class BeatUpdate(BaseModel):
    """Request model for updating a beat."""
    title: Optional[str] = None
    status: Optional[BeatStatus] = None
    tags: Optional[List[str]] = None
    description: Optional[str] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    qc_passed: Optional[bool] = None


class BeatListResponse(BaseModel):
    """Paginated beat list response."""
    items: List[Beat]
    total: int
    page: int
    page_size: int
    pages: int
