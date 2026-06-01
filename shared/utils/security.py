"""Security utilities for authentication and validation."""

import os
import re
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, field_validator
import structlog

logger = structlog.get_logger()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day

# Cache the secret key so encode/decode use the same key
_secret_key_cache: Optional[str] = None


def get_secret_key() -> str:
    """Get JWT secret key from environment."""
    global _secret_key_cache
    if _secret_key_cache is not None:
        return _secret_key_cache
    
    secret = os.getenv('SECRET_KEY')
    if not secret or secret == 'dev-secret-key-change-in-production':
        env = os.getenv('ENVIRONMENT', 'development')
        if env == 'production':
            raise RuntimeError(
                "SECRET_KEY must be set to a secure random value in production! "
                "Generate one with: python -c 'import secrets; print(secrets.token_hex(32))'"
            )
        # In development, generate a temporary key
        logger.warning("using_temporary_secret_key")
        _secret_key_cache = secrets.token_hex(32)
    else:
        _secret_key_cache = secret
    return _secret_key_cache


def set_secret_key(secret: str) -> None:
    """Set the secret key (for testing)."""
    global _secret_key_cache
    _secret_key_cache = secret


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "access"})
    
    secret = get_secret_key()
    return jwt.encode(to_encode, secret, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate a JWT access token."""
    try:
        secret = get_secret_key()
        payload = jwt.decode(token, secret, algorithms=[ALGORITHM])
        
        # Validate required claims
        if payload.get("type") != "access":
            return None
        if datetime.utcnow().timestamp() > payload.get("exp", 0):
            return None
        
        return payload
    except JWTError:
        return None


def validate_beat_id(beat_id: str) -> bool:
    """Validate a beat ID is a proper UUID."""
    try:
        UUID(beat_id, version=4)
        return True
    except ValueError:
        return False


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename to prevent path traversal."""
    # Remove any path components
    filename = os.path.basename(filename)
    # Remove any non-alphanumeric characters except safe ones
    filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
    # Prevent empty filenames
    if not filename:
        filename = 'unnamed'
    return filename


def validate_file_path(path: str, allowed_base: str) -> bool:
    """Validate a file path is within allowed base directory."""
    try:
        real_path = os.path.realpath(path)
        real_base = os.path.realpath(allowed_base)
        return real_path.startswith(real_base)
    except (OSError, ValueError):
        return False


# ─── Pydantic Validators ───────────────────────────────────────────

class UserRegistration(BaseModel):
    """User registration request validation."""
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    
    @field_validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v


class BeatGenerationRequest(BaseModel):
    """Beat generation request validation."""
    genre_id: str
    bpm: Optional[int] = None
    key_signature: Optional[str] = None
    mood: Optional[str] = None
    duration_seconds: int = 180
    title: Optional[str] = None
    tags: list = []
    priority: int = 5
    
    @field_validator('genre_id')
    def validate_genre_id(cls, v):
        if not validate_beat_id(v):
            raise ValueError('Invalid genre_id format')
        return v
    
    @field_validator('bpm')
    def validate_bpm(cls, v):
        if v is not None and not (60 <= v <= 200):
            raise ValueError('BPM must be between 60 and 200')
        return v
    
    @field_validator('duration_seconds')
    def validate_duration(cls, v):
        if not (60 <= v <= 300):
            raise ValueError('Duration must be between 60 and 300 seconds')
        return v
    
    @field_validator('priority')
    def validate_priority(cls, v):
        if not (1 <= v <= 10):
            raise ValueError('Priority must be between 1 and 10')
        return v


class BatchGenerationRequest(BaseModel):
    """Batch generation request validation."""
    genre_ids: list[str]
    count_per_genre: int = 5
    bpm_range: Optional[list[int]] = None
    priority: int = 5
    
    @field_validator('genre_ids')
    def validate_genre_ids(cls, v):
        if not v:
            raise ValueError('At least one genre_id is required')
        for gid in v:
            if not validate_beat_id(gid):
                raise ValueError(f'Invalid genre_id format: {gid}')
        return v
    
    @field_validator('count_per_genre')
    def validate_count(cls, v):
        if not (1 <= v <= 50):
            raise ValueError('count_per_genre must be between 1 and 50')
        return v
    
    @field_validator('bpm_range')
    def validate_bpm_range(cls, v):
        if v is not None:
            if len(v) != 2:
                raise ValueError('bpm_range must be [min, max]')
            if not (60 <= v[0] <= v[1] <= 200):
                raise ValueError('Invalid BPM range')
        return v
