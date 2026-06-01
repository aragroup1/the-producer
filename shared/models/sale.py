"""Sale/transaction model definitions."""

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field


class Sale(BaseModel):
    """A license sale transaction."""
    id: Optional[UUID] = None
    beat_id: Optional[UUID] = None
    license_type: str  # non_exclusive, premium, exclusive
    price: float
    customer_email: Optional[str] = None
    customer_name: Optional[str] = None
    shopify_order_id: Optional[str] = None
    shopify_line_item_id: Optional[str] = None
    download_count: int = 0
    downloaded_files: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class LicenseTier(BaseModel):
    """A license tier definition."""
    name: str
    price: float
    description: str
    includes: List[str]
    usage_terms: str
    is_exclusive: bool = False
