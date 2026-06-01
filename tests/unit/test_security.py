"""Unit tests for security utilities."""

import os
import pytest
from pydantic import ValidationError

from shared.utils.security import (
    get_password_hash, verify_password, create_access_token,
    decode_access_token, validate_beat_id, sanitize_filename,
    validate_file_path, UserRegistration, BeatGenerationRequest
)


class TestPasswordHashing:
    """Test password hashing functions."""
    
    def test_hash_password(self):
        """Test password hashing."""
        password = "SecurePass123!"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert hashed.startswith("$2")
    
    def test_verify_password_correct(self):
        """Test verifying correct password."""
        password = "SecurePass123!"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test verifying incorrect password."""
        password = "SecurePass123!"
        wrong_password = "WrongPass456!"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False


class TestJWT:
    """Test JWT token functions."""
    
    def test_create_and_decode_token(self):
        """Test creating and decoding a valid token."""
        os.environ['SECRET_KEY'] = 'test-secret-key-for-unit-tests-only'
        
        data = {"sub": "user-123", "email": "test@example.com"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        decoded = decode_access_token(token)
        assert decoded is not None
        assert decoded["sub"] == "user-123"
        assert decoded["email"] == "test@example.com"
    
    def test_decode_invalid_token(self):
        """Test decoding an invalid token."""
        decoded = decode_access_token("invalid.token.here")
        assert decoded is None
    
    def test_decode_expired_token(self):
        """Test decoding an expired token."""
        from datetime import timedelta
        
        os.environ['SECRET_KEY'] = 'test-secret-key'
        token = create_access_token(
            {"sub": "user-123"},
            expires_delta=timedelta(seconds=-1)
        )
        
        decoded = decode_access_token(token)
        assert decoded is None


class TestValidation:
    """Test validation functions."""
    
    def test_validate_beat_id_valid(self):
        """Test validating a valid UUID."""
        assert validate_beat_id("550e8400-e29b-41d4-a716-446655440000") is True
    
    def test_validate_beat_id_invalid(self):
        """Test validating an invalid UUID."""
        assert validate_beat_id("not-a-uuid") is False
        assert validate_beat_id("") is False
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        assert sanitize_filename("test.wav") == "test.wav"
        assert sanitize_filename("../../../etc/passwd") == "passwd"
        assert sanitize_filename("test<file>.wav") == "testfile.wav"
    
    def test_validate_file_path(self, tmp_path):
        """Test file path validation."""
        base = str(tmp_path)
        valid_path = str(tmp_path / "test.wav")
        invalid_path = "/etc/passwd"
        
        assert validate_file_path(valid_path, base) is True
        assert validate_file_path(invalid_path, base) is False


class TestPydanticValidators:
    """Test Pydantic model validators."""
    
    def test_user_registration_valid(self):
        """Test valid user registration."""
        user = UserRegistration(
            email="test@example.com",
            password="SecurePass123!",
            full_name="Test User"
        )
        assert user.email == "test@example.com"
    
    def test_user_registration_weak_password(self):
        """Test weak password rejection."""
        with pytest.raises(ValidationError):
            UserRegistration(
                email="test@example.com",
                password="weak"
            )
    
    def test_user_registration_no_uppercase(self):
        """Test password without uppercase."""
        with pytest.raises(ValidationError):
            UserRegistration(
                email="test@example.com",
                password="lowercase123!"
            )
    
    def test_beat_generation_valid(self):
        """Test valid beat generation request."""
        request = BeatGenerationRequest(
            genre_id="550e8400-e29b-41d4-a716-446655440000",
            bpm=140,
            duration_seconds=180
        )
        assert request.bpm == 140
    
    def test_beat_generation_invalid_bpm(self):
        """Test invalid BPM."""
        with pytest.raises(ValidationError):
            BeatGenerationRequest(
                genre_id="550e8400-e29b-41d4-a716-446655440000",
                bpm=300
            )
    
    def test_beat_generation_invalid_genre_id(self):
        """Test invalid genre ID."""
        with pytest.raises(ValidationError):
            BeatGenerationRequest(
                genre_id="not-a-uuid"
            )
