"""YouTube Upload Automation.

Handles OAuth 2.0 authentication, video uploads, thumbnail uploads,
playlist management, and multi-channel support via YouTube Data API v3.
"""

import os
import json
import pickle
from typing import Dict, Optional, Any, List
from pathlib import Path
from datetime import datetime
import structlog

logger = structlog.get_logger()


class YouTubeUploader:
    """Upload videos to YouTube."""
    
    # YouTube API scopes
    SCOPES = [
        'https://www.googleapis.com/auth/youtube.upload',
        'https://www.googleapis.com/auth/youtube',
        'https://www.googleapis.com/auth/youtube.readonly'
    ]
    
    # Upload limits
    DAILY_UPLOAD_LIMIT = 100
    
    def __init__(self, credentials_dir: str = "./credentials/youtube"):
        self.credentials_dir = credentials_dir
        self.youtube_service = None
        self.channel_credentials: Dict[str, Any] = {}
        os.makedirs(credentials_dir, exist_ok=True)
    
    def authenticate(self, channel_id: str = "default",
                     client_secrets_path: str = None) -> bool:
        """Authenticate with YouTube API.
        
        Args:
            channel_id: Channel identifier
            client_secrets_path: Path to client_secrets.json
        
        Returns:
            True if authenticated successfully
        """
        try:
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build
        except ImportError:
            logger.error("google_api_not_installed",
                        message="Install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
            return False
        
        token_path = os.path.join(self.credentials_dir, f"{channel_id}_token.pickle")
        
        creds = None
        
        # Load existing token
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # Refresh or create new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not client_secrets_path or not os.path.exists(client_secrets_path):
                    logger.error("client_secrets_not_found",
                               path=client_secrets_path)
                    return False
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    client_secrets_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save token
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        # Build service
        self.youtube_service = build('youtube', 'v3', credentials=creds)
        self.channel_credentials[channel_id] = creds
        
        logger.info("youtube_authenticated", channel_id=channel_id)
        return True
    
    def upload_video(self, video_path: str, metadata: Dict[str, Any],
                     channel_id: str = "default") -> Dict[str, Any]:
        """Upload a video to YouTube.
        
        Args:
            video_path: Path to video file
            metadata: Video metadata dict
            channel_id: Target channel
        
        Returns:
            Upload result with video ID and URL
        """
        if not self.youtube_service:
            logger.error("not_authenticated", channel_id=channel_id)
            return {"status": "error", "message": "Not authenticated"}
        
        try:
            from googleapiclient.http import MediaFileUpload
            from googleapiclient.errors import HttpError
        except ImportError:
            return {"status": "error", "message": "Google API client not installed"}
        
        # Check rate limits
        if not self._check_upload_limit(channel_id):
            return {"status": "error", "message": "Daily upload limit reached"}
        
        title = metadata.get('title', 'Untitled')
        description = metadata.get('description', '')
        tags = metadata.get('tags', [])
        category = metadata.get('category', 'Music')
        privacy = metadata.get('privacy', 'public')
        made_for_kids = metadata.get('made_for_kids', False)
        
        # Build request body
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags[:15],  # Max 15 tags for best practice
                'categoryId': self._get_category_id(category)
            },
            'status': {
                'privacyStatus': privacy,
                'selfDeclaredMadeForKids': made_for_kids
            }
        }
        
        # Add shorts-specific settings
        if metadata.get('is_short', False):
            body['snippet']['title'] = title + ' #Shorts'
        
        # Upload
        try:
            media = MediaFileUpload(
                video_path,
                mimetype='video/mp4',
                resumable=True
            )
            
            request = self.youtube_service.videos().insert(
                part='snippet,status',
                body=body,
                media_body=media
            )
            
            response = request.execute()
            
            video_id = response['id']
            video_url = f"https://youtube.com/watch?v={video_id}"
            
            # Upload thumbnail if provided
            thumbnail_path = metadata.get('thumbnail_path')
            if thumbnail_path and os.path.exists(thumbnail_path):
                self._upload_thumbnail(video_id, thumbnail_path)
            
            # Add to playlist if specified
            playlist_id = metadata.get('playlist_id')
            if playlist_id:
                self._add_to_playlist(video_id, playlist_id)
            
            # Record upload
            self._record_upload(channel_id, video_id)
            
            logger.info("youtube_upload_complete",
                       channel_id=channel_id,
                       video_id=video_id,
                       title=title)
            
            return {
                "status": "success",
                "platform": "youtube",
                "video_id": video_id,
                "url": video_url,
                "title": title,
                "privacy": privacy
            }
        
        except HttpError as e:
            error_details = json.loads(e.content)
            error_reason = error_details.get('error', {}).get('errors', [{}])[0].get('reason', 'unknown')
            
            logger.error("youtube_upload_failed",
                        channel_id=channel_id,
                        reason=error_reason,
                        error=str(e))
            
            return {
                "status": "error",
                "message": f"YouTube API error: {error_reason}",
                "details": str(e)
            }
        
        except Exception as e:
            logger.error("youtube_upload_exception",
                        channel_id=channel_id, error=str(e))
            return {"status": "error", "message": str(e)}
    
    def _upload_thumbnail(self, video_id: str, thumbnail_path: str):
        """Upload thumbnail for a video."""
        try:
            from googleapiclient.http import MediaFileUpload
            
            media = MediaFileUpload(thumbnail_path, mimetype='image/png')
            
            self.youtube_service.thumbnails().set(
                videoId=video_id,
                media_body=media
            ).execute()
            
            logger.info("thumbnail_uploaded", video_id=video_id)
        
        except Exception as e:
            logger.error("thumbnail_upload_failed", 
                       video_id=video_id, error=str(e))
    
    def _add_to_playlist(self, video_id: str, playlist_id: str):
        """Add video to playlist."""
        try:
            self.youtube_service.playlistItems().insert(
                part='snippet',
                body={
                    'snippet': {
                        'playlistId': playlist_id,
                        'resourceId': {
                            'kind': 'youtube#video',
                            'videoId': video_id
                        }
                    }
                }
            ).execute()
            
            logger.info("added_to_playlist", 
                       video_id=video_id, playlist_id=playlist_id)
        
        except Exception as e:
            logger.error("playlist_add_failed",
                       video_id=video_id, error=str(e))
    
    def _get_category_id(self, category_name: str) -> str:
        """Get YouTube category ID from name."""
        categories = {
            'Music': '10',
            'Entertainment': '24',
            'Film & Animation': '1',
            'Gaming': '20',
        }
        return categories.get(category_name, '10')  # Default to Music
    
    def _check_upload_limit(self, channel_id: str) -> bool:
        """Check if channel has reached daily upload limit."""
        # Load daily upload count
        count_path = os.path.join(self.credentials_dir, f"{channel_id}_uploads.json")
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        if os.path.exists(count_path):
            with open(count_path, 'r') as f:
                data = json.load(f)
            
            if data.get('date') == today:
                if data.get('count', 0) >= self.DAILY_UPLOAD_LIMIT:
                    return False
                data['count'] = data.get('count', 0) + 1
            else:
                data = {'date': today, 'count': 1}
        else:
            data = {'date': today, 'count': 1}
        
        with open(count_path, 'w') as f:
            json.dump(data, f)
        
        return True
    
    def _record_upload(self, channel_id: str, video_id: str):
        """Record upload for tracking."""
        log_path = os.path.join(self.credentials_dir, 'upload_log.json')
        
        uploads = []
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                uploads = json.load(f)
        
        uploads.append({
            'channel_id': channel_id,
            'video_id': video_id,
            'uploaded_at': datetime.now().isoformat()
        })
        
        with open(log_path, 'w') as f:
            json.dump(uploads[-1000:], f, indent=2)  # Keep last 1000
    
    def get_upload_status(self, video_id: str) -> Dict[str, Any]:
        """Get status of an uploaded video."""
        if not self.youtube_service:
            return {"status": "error", "message": "Not authenticated"}
        
        try:
            response = self.youtube_service.videos().list(
                part='snippet,status,statistics',
                id=video_id
            ).execute()
            
            items = response.get('items', [])
            if not items:
                return {"status": "not_found"}
            
            video = items[0]
            
            return {
                "status": "success",
                "video_id": video_id,
                "title": video['snippet']['title'],
                "privacy": video['status']['privacyStatus'],
                "views": video['statistics'].get('viewCount', 0),
                "likes": video['statistics'].get('likeCount', 0),
                "comments": video['statistics'].get('commentCount', 0)
            }
        
        except Exception as e:
            logger.error("status_check_failed", video_id=video_id, error=str(e))
            return {"status": "error", "message": str(e)}
    
    def update_video(self, video_id: str, 
                     metadata_updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update video metadata."""
        if not self.youtube_service:
            return {"status": "error", "message": "Not authenticated"}
        
        try:
            body = {'id': video_id, 'snippet': {}}
            
            if 'title' in metadata_updates:
                body['snippet']['title'] = metadata_updates['title']
            if 'description' in metadata_updates:
                body['snippet']['description'] = metadata_updates['description']
            if 'tags' in metadata_updates:
                body['snippet']['tags'] = metadata_updates['tags']
            
            if 'privacy' in metadata_updates:
                body['status'] = {'privacyStatus': metadata_updates['privacy']}
            
            self.youtube_service.videos().update(
                part='snippet,status',
                body=body
            ).execute()
            
            return {"status": "success", "video_id": video_id}
        
        except Exception as e:
            logger.error("video_update_failed", video_id=video_id, error=str(e))
            return {"status": "error", "message": str(e)}
    
    def list_uploads(self, channel_id: str = "default",
                     max_results: int = 50) -> List[Dict[str, Any]]:
        """List recent uploads for a channel."""
        if not self.youtube_service:
            return []
        
        try:
            # Get uploads playlist ID
            channels_response = self.youtube_service.channels().list(
                part='contentDetails',
                mine=True
            ).execute()
            
            items = channels_response.get('items', [])
            if not items:
                return []
            
            uploads_playlist_id = items[0]['contentDetails']['relatedPlaylists']['uploads']
            
            # Get videos from uploads playlist
            playlist_response = self.youtube_service.playlistItems().list(
                part='snippet',
                playlistId=uploads_playlist_id,
                maxResults=max_results
            ).execute()
            
            videos = []
            for item in playlist_response.get('items', []):
                snippet = item['snippet']
                videos.append({
                    'video_id': snippet['resourceId']['videoId'],
                    'title': snippet['title'],
                    'published_at': snippet['publishedAt'],
                    'thumbnail': snippet['thumbnails'].get('default', {}).get('url', '')
                })
            
            return videos
        
        except Exception as e:
            logger.error("list_uploads_failed", error=str(e))
            return []
