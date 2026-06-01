"""User model definitions."""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class User(BaseModel):
    """Admin dashboard user."""
    id: Optional[UUID] = None
    email: str
    full_name: Optional[str] = None
    role: str = "user"  # user, admin, superadmin
    is_active: bool = True
    last_login: Optional[datetime] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    """Request model for creating a user."""
    email: str
    password: str
    full_name: Optional[str] = None
    role: str = "user"


class UserLogin(BaseModel):
    """Request model for user login."""
    email: str
    password: str
