"""Beat-selling platform uploaders.

Handles BeatStars and Airbit integration for automated beat uploads.
"""

import os
import json
import structlog
from typing import Dict, Optional, Any, List
from datetime import datetime

logger = structlog.get_logger()


class BeatStarsUploader:
    """Upload beats to BeatStars marketplace."""
    
    def __init__(self, credentials_dir: str = "./credentials/beatstars"):
        self.credentials_dir = credentials_dir
        self.api_key = None
        os.makedirs(credentials_dir, exist_ok=True)
    
    def authenticate(self, api_key: str = None) -> bool:
        """Authenticate with BeatStars API."""
        if not api_key:
            api_key = os.getenv('BEATSTARS_API_KEY')
        
        creds_path = os.path.join(self.credentials_dir, 'credentials.json')
        if os.path.exists(creds_path) and not api_key:
            with open(creds_path, 'r') as f:
                data = json.load(f)
                api_key = data.get('api_key')
        
        if api_key:
            self.api_key = api_key
            logger.info("beatstars_authenticated")
            return True
        
        logger.warning("beatstars_auth_required")
        return False
    
    def upload_beat(self, audio_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Upload a beat to BeatStars.
        
        BeatStars API requires partner access.
        """
        if not self.api_key:
            return {"status": "error", "message": "Not authenticated"}
        
        title = metadata.get('title', 'Untitled Beat')
        description = metadata.get('description', '')
        tags = metadata.get('tags', [])
        bpm = metadata.get('bpm', 140)
        key = metadata.get('key', 'C')
        genre = metadata.get('genre', 'Hip Hop')
        
        # Pricing
        pricing = metadata.get('pricing', {
            'mp3_lease': 20,
            'wav_lease': 35,
            'trackout': 50,
            'exclusive': 200,
            'unlimited': 100
        })
        
        logger.info("beatstars_upload_initiated",
                   title=title,
                   genre=genre)
        
        # BeatStars API is partner-only
        # Return pending with metadata for manual upload
        return {
            "status": "pending_api",
            "platform": "beatstars",
            "message": "BeatStars requires partner API access",
            "audio_path": audio_path,
            "metadata": {
                'title': title,
                'description': description,
                'tags': tags,
                'bpm': bpm,
                'key': key,
                'genre': genre,
                'pricing': pricing
            },
            "instructions": "Apply for BeatStars Partner API at developer.beatstars.com"
        }


class AirbitUploader:
    """Upload beats to Airbit marketplace."""
    
    def __init__(self, credentials_dir: str = "./credentials/airbit"):
        self.credentials_dir = credentials_dir
        self.api_key = None
        os.makedirs(credentials_dir, exist_ok=True)
    
    def authenticate(self, api_key: str = None) -> bool:
        """Authenticate with Airbit API."""
        if not api_key:
            api_key = os.getenv('AIRBIT_API_KEY')
        
        creds_path = os.path.join(self.credentials_dir, 'credentials.json')
        if os.path.exists(creds_path) and not api_key:
            with open(creds_path, 'r') as f:
                data = json.load(f)
                api_key = data.get('api_key')
        
        if api_key:
            self.api_key = api_key
            logger.info("airbit_authenticated")
            return True
        
        logger.warning("airbit_auth_required")
        return False
    
    def upload_beat(self, audio_path: str, 
                    metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Upload a beat to Airbit."""
        if not self.api_key:
            return {"status": "error", "message": "Not authenticated"}
        
        title = metadata.get('title', 'Untitled Beat')
        
        logger.info("airbit_upload_initiated", title=title)
        
        return {
            "status": "pending_api",
            "platform": "airbit",
            "message": "Airbit API integration pending",
            "audio_path": audio_path,
            "metadata": metadata,
            "instructions": "Contact Airbit for API access"
        }
