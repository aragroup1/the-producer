"""SQLAlchemy ORM models matching the database schema."""

import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text,
    ForeignKey, ARRAY, JSON, DECIMAL, Index, func
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


def generate_uuid() -> str:
    return str(uuid.uuid4())


class Genre(Base):
    __tablename__ = 'genres'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    parent_genre_id = Column(UUID(as_uuid=True), ForeignKey('genres.id'), nullable=True)
    bpm_range_min = Column(Integer, default=60)
    bpm_range_max = Column(Integer, default=200)
    key_signatures = Column(ARRAY(String), default=[])
    typical_structure = Column(JSON, default={})
    description = Column(Text)
    trending_score = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    parent = relationship("Genre", remote_side=[id], backref="subgenres")
    beats = relationship("Beat", back_populates="genre")


class Trend(Base):
    __tablename__ = 'trends'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(String(50), nullable=False)
    keyword = Column(String(255), nullable=False)
    genre_id = Column(UUID(as_uuid=True), ForeignKey('genres.id'), nullable=True)
    volume_score = Column(Float)
    growth_rate = Column(Float)
    rank = Column(Integer)
    trend_metadata = Column(JSON, default={})
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


class SoundLibrary(Base):
    __tablename__ = 'sound_libraries'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    vst_type = Column(String(100), nullable=False)
    category = Column(String(100), nullable=False)
    genre_tags = Column(ARRAY(String), default=[])
    file_path = Column(String(500))
    preset_data = Column(JSON, default={})
    quality_score = Column(Float, default=0.0)
    usage_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MixChain(Base):
    __tablename__ = 'mix_chains'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    genre_id = Column(UUID(as_uuid=True), ForeignKey('genres.id'), nullable=True)
    category = Column(String(100), nullable=False)
    chain_config = Column(JSON, nullable=False)
    quality_score = Column(Float, default=0.0)
    usage_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Beat(Base):
    __tablename__ = 'beats'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    genre_id = Column(UUID(as_uuid=True), ForeignKey('genres.id'), nullable=True)
    bpm = Column(Integer, nullable=False)
    key_signature = Column(String(10))
    duration_seconds = Column(Integer)
    mood = Column(String(50))
    
    status = Column(String(50), default='draft')
    midi_data = Column(JSON, default={})
    composition_params = Column(JSON, default={})
    sound_assignments = Column(JSON, default={})
    mix_chain_id = Column(UUID(as_uuid=True), ForeignKey('mix_chains.id'), nullable=True)
    mix_params = Column(JSON, default={})
    master_params = Column(JSON, default={})
    loudness_lufs = Column(Float)
    true_peak_db = Column(Float)
    
    quality_score = Column(Float)
    qc_results = Column(JSON, default={})
    qc_passed = Column(Boolean)
    
    wav_path = Column(String(500))
    mp3_path = Column(String(500))
    stems_path = Column(String(500))
    midi_path = Column(String(500))
    preview_path = Column(String(500))
    watermarked_preview_path = Column(String(500))
    cover_art_path = Column(String(500))
    
    tags = Column(ARRAY(String), default=[])
    description = Column(Text)
    seo_title = Column(String(255))
    seo_description = Column(Text)
    
    shopify_product_id = Column(String(255))
    shopify_status = Column(String(50))
    
    view_count = Column(Integer, default=0)
    play_count = Column(Integer, default=0)
    wishlist_count = Column(Integer, default=0)
    cart_add_count = Column(Integer, default=0)
    sales_count = Column(Integer, default=0)
    revenue = Column(DECIMAL(10, 2), default=0.0)
    
    generation_cost = Column(DECIMAL(8, 4))
    generation_time_seconds = Column(Integer)
    ai_model_version = Column(String(50))
    batch_id = Column(UUID(as_uuid=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    genre = relationship("Genre", back_populates="beats")
    sections = relationship("BeatSection", back_populates="beat", cascade="all, delete-orphan")
    jobs = relationship("RenderJob", back_populates="beat", cascade="all, delete-orphan")
    sales = relationship("Sale", back_populates="beat")
    qc_logs = relationship("QCLog", back_populates="beat", cascade="all, delete-orphan")


class BeatSection(Base):
    __tablename__ = 'beat_sections'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    beat_id = Column(UUID(as_uuid=True), ForeignKey('beats.id'), nullable=False)
    section_type = Column(String(50), nullable=False)
    start_bar = Column(Integer, nullable=False)
    end_bar = Column(Integer, nullable=False)
    bpm = Column(Integer)
    key_signature = Column(String(10))
    midi_events = Column(JSON, default={})
    automation_data = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    beat = relationship("Beat", back_populates="sections")


class RenderJob(Base):
    __tablename__ = 'render_jobs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    beat_id = Column(UUID(as_uuid=True), ForeignKey('beats.id'), nullable=True)
    job_type = Column(String(50), nullable=False)
    status = Column(String(50), default='queued')
    worker_id = Column(String(100))
    priority = Column(Integer, default=5)
    retry_count = Column(Integer, default=0)
    error_message = Column(Text)
    result_data = Column(JSON, default={})
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    beat = relationship("Beat", back_populates="jobs")


class Sale(Base):
    __tablename__ = 'sales'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    beat_id = Column(UUID(as_uuid=True), ForeignKey('beats.id'), nullable=True)
    license_type = Column(String(50), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    customer_email = Column(String(255))
    customer_name = Column(String(255))
    shopify_order_id = Column(String(255))
    shopify_line_item_id = Column(String(255))
    download_count = Column(Integer, default=0)
    downloaded_files = Column(ARRAY(String), default=[])
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    beat = relationship("Beat", back_populates="sales")


class QCLog(Base):
    __tablename__ = 'qc_logs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    beat_id = Column(UUID(as_uuid=True), ForeignKey('beats.id'), nullable=False)
    check_type = Column(String(100), nullable=False)
    score = Column(Float)
    passed = Column(Boolean)
    details = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    beat = relationship("Beat", back_populates="qc_logs")


class AIModel(Base):
    __tablename__ = 'ai_models'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    model_type = Column(String(100), nullable=False)
    version = Column(String(50), nullable=False)
    file_path = Column(String(500))
    config = Column(JSON, default={})
    training_data_summary = Column(JSON, default={})
    metrics = Column(JSON, default={})
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class LearningFeedback(Base):
    __tablename__ = 'learning_feedback'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    beat_id = Column(UUID(as_uuid=True), ForeignKey('beats.id'), nullable=False)
    feedback_type = Column(String(50), nullable=False)
    weight = Column(Float, default=1.0)
    preset_metadata = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class User(Base):
    __tablename__ = 'users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(50), default='user')
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
