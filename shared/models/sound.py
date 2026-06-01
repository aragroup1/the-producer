"""Sound library model definitions."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field


class SoundLibrary(BaseModel):
    """A sound/preset in the library."""
    id: Optional[UUID] = None
    name: str
    vst_type: str  # kontakt, serum, omnisphere, massive_x, fluidsynth, sampler
    category: str  # drums, bass, synth, piano, orchestral, fx, vocal
    genre_tags: List[str] = Field(default_factory=list)
    file_path: Optional[str] = None
    preset_data: Dict[str, Any] = Field(default_factory=dict)
    quality_score: float = 0.0
    usage_count: int = 0
    is_active: bool = True
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class MixChain(BaseModel):
    """A reusable mixing chain template."""
    id: Optional[UUID] = None
    name: str
    genre_id: Optional[UUID] = None
    category: str  # drums, bass, synth, piano, master_bus
    chain_config: Dict[str, Any]
    quality_score: float = 0.0
    usage_count: int = 0
    is_active: bool = True
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
