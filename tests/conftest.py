"""Pytest configuration and shared fixtures."""

import os
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

# Set test environment variables before imports
os.environ.setdefault("SECRET_KEY", "test-secret-key-12345678901234567890123456789012")
os.environ.setdefault("ENVIRONMENT", "testing")


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ─── Database Fixtures (mocked for unit tests) ───────────────────────────

@pytest.fixture
def mock_db_session():
    """Provide a mock database session for unit tests."""
    session = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    session.add = MagicMock()
    session.delete = AsyncMock()
    session.execute = AsyncMock()
    session.scalar = AsyncMock()
    session.scalars = AsyncMock()
    return session


@pytest.fixture
def mock_async_session_factory(mock_db_session):
    """Provide a mock async session factory."""
    factory = MagicMock()
    
    async def _async_context_manager():
        return mock_db_session
    
    factory.return_value.__aenter__ = AsyncMock(return_value=mock_db_session)
    factory.return_value.__aexit__ = AsyncMock(return_value=None)
    return factory


# ─── Security Fixtures ──────────────────────────────────────────────────

@pytest.fixture
def test_secret_key():
    """Provide a consistent test secret key."""
    return "test-secret-key-12345678901234567890123456789012"


@pytest.fixture
def sample_user_data():
    """Provide sample valid user registration data."""
    return {
        "email": "test@example.com",
        "password": "SecurePass123!",
        "full_name": "Test User"
    }


@pytest.fixture
def sample_beat_request():
    """Provide sample valid beat generation request data."""
    return {
        "genre_id": "550e8400-e29b-41d4-a716-446655440000",
        "bpm": 140,
        "duration_seconds": 180,
        "priority": 5
    }


@pytest.fixture
def sample_batch_request():
    """Provide sample valid batch generation request data."""
    return {
        "genre_ids": [
            "550e8400-e29b-41d4-a716-446655440000",
            "660e8400-e29b-41d4-a716-446655440001"
        ],
        "count_per_genre": 5,
        "priority": 5
    }
