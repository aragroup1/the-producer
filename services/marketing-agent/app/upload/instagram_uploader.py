"""Instagram Reels Upload Automation.

Uses Instagram Graph API for business/creator accounts.
"""

import os
import json
import structlog
from typing import Dict, Optional, Any
from datetime import datetime

logger = structlog.get_logger()


class InstagramUploader:
    """Upload videos to Instagram Reels."""
    
    DAILY_UPLOAD_LIMIT = 25
    
    def __init__(self, credentials_dir: str = "./credentials/instagram"):
        self.credentials_dir = credentials_dir
        self.access_token = None
        self.account_id = None
        os.makedirs(credentials_dir, exist_ok=True)
    
    def authenticate(self, access_token: str = None,
                     account_id: str = None) -> bool:
        """Authenticate with Instagram Graph API."""
        if not access_token:
            access_token = os.getenv('INSTAGRAM_ACCESS_TOKEN')
        if not account_id:
            account_id = os.getenv('INSTAGRAM_ACCOUNT_ID')
        
        creds_path = os.path.join(self.credentials_dir, 'credentials.json')
        if os.path.exists(creds_path) and not access_token:
            with open(creds_path, 'r') as f:
                data = json.load(f)
                access_token = data.get('access_token')
                account_id = data.get('account_id')
        
        if access_token and account_id:
            self.access_token = access_token
            self.account_id = account_id
            logger.info("instagram_authenticated")
            return True
        
        logger.warning("instagram_auth_required")
        return False
    
    def upload_reel(self, video_path: str,
                    metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Upload a Reel to Instagram.
        
        Instagram Graph API flow:
        1. Upload video to container
        2. Check container status
        3. Publish container
        """
        if not self.access_token:
            return {"status": "error", "message": "Not authenticated"}
        
        if not self._check_upload_limit():
            return {"status": "error", "message": "Daily upload limit reached"}
        
        caption = metadata.get('caption', '')
        share_to_feed = metadata.get('share_to_feed', True)
        
        try:
            import requests
            
            # Step 1: Create media container
            container_url = f"https://graph.facebook.com/v18.0/{self.account_id}/media"
            
            container_params = {
                'media_type': 'REELS',
                'video_url': video_path,  # Must be publicly accessible URL
                'caption': caption,
                'share_to_feed': share_to_feed,
                'access_token': self.access_token
            }
            
            # Note: Instagram requires a publicly accessible URL for the video
            # Local file paths won't work. You need to upload to a CDN first.
            
            logger.info("instagram_reel_upload_initiated",
                       caption=caption[:50])
            
            return {
                "status": "pending",
                "platform": "instagram",
                "message": "Instagram requires public URL for video. Upload to CDN first.",
                "video_path": video_path,
                "caption": caption,
                "next_steps": [
                    "1. Upload video to public CDN (S3, Cloudflare R2)",
                    "2. Use public URL in upload request",
                    "3. Poll container status",
                    "4. Publish when ready"
                ]
            }
        
        except Exception as e:
            logger.error("instagram_upload_failed", error=str(e))
            return {"status": "error", "message": str(e)}
    
    def _check_upload_limit(self) -> bool:
        """Check daily upload limit."""
        count_path = os.path.join(self.credentials_dir, 'upload_count.json')
        today = datetime.now().strftime('%Y-%m-%d')
        
        if os.path.exists(count_path):
            with open(count_path, 'r') as f:
                data = json.load(f)
            
            if data.get('date') == today:
                if data.get('count', 0) >= self.DAILY_UPLOAD_LIMIT:
                    return False
                data['count'] += 1
            else:
                data = {'date': today, 'count': 1}
        else:
            data = {'date': today, 'count': 1}
        
        with open(count_path, 'w') as f:
            json.dump(data, f)
        
        return True
