"""AI model definitions."""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field


class AIModel(BaseModel):
    """A trained AI model version."""
    id: Optional[UUID] = None
    name: str
    model_type: str  # composition, sound_selection, mixing, arrangement, quality
    version: str
    file_path: Optional[str] = None
    config: Dict[str, Any] = Field(default_factory=dict)
    training_data_summary: Dict[str, Any] = Field(default_factory=dict)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = False
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class LearningFeedback(BaseModel):
    """Feedback data for adaptive learning."""
    id: Optional[UUID] = None
    beat_id: Optional[UUID] = None
    feedback_type: str  # sale, view, play, wishlist, skip, return, cart_add
    weight: float = 1.0
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
