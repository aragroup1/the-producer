"""Multi-Channel Management System.

Manages multiple YouTube channels, each targeting a specific niche.
Handles channel assignment, upload frequency, and algorithm overlap avoidance.
"""

import os
import json
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import structlog

logger = structlog.get_logger()


class ChannelPlatform(Enum):
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"


@dataclass
class Channel:
    """A content channel definition."""
    id: str
    name: str
    platform: ChannelPlatform
    niche: str  # Genre focus, e.g., "drill", "emotional_guitar"
    description: str
    channel_id: str  # Platform channel ID
    credentials: Dict[str, str] = None
    upload_frequency: int = 3  # uploads per day
    active_hours: List[int] = None  # Hours to upload (24h format)
    target_audience: str = ""
    content_types: List[str] = None  # full, short, teaser
    is_active: bool = True
    created_at: str = None
    
    def __post_init__(self):
        if self.credentials is None:
            self.credentials = {}
        if self.active_hours is None:
            self.active_hours = [9, 12, 15, 18, 21]
        if self.content_types is None:
            self.content_types = ["full", "short"]
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


@dataclass
class UploadRecord:
    """Record of an upload to a channel."""
    upload_id: str
    channel_id: str
    beat_id: str
    video_type: str
    uploaded_at: datetime
    platform_video_id: Optional[str] = None
    status: str = "pending"  # pending, uploaded, failed


class ChannelManager:
    """Manage multiple content channels."""
    
    # Default channel configurations
    DEFAULT_CHANNELS = [
        Channel(
            id="drill_beats_yt",
            name="Drill Beats Daily",
            platform=ChannelPlatform.YOUTUBE,
            niche="drill",
            description="Hard UK and NY drill beats daily",
            channel_id="",
            upload_frequency=3,
            active_hours=[10, 14, 19],
            target_audience="UK drill fans, rappers",
            content_types=["full", "short"]
        ),
        Channel(
            id="trap_beats_yt",
            name="Trap Vault",
            platform=ChannelPlatform.YOUTUBE,
            niche="trap",
            description="Dark and melodic trap instrumentals",
            channel_id="",
            upload_frequency=4,
            active_hours=[9, 13, 17, 21],
            target_audience="Trap artists, producers",
            content_types=["full", "short"]
        ),
        Channel(
            id="emotional_guitar_yt",
            name="Emotional Guitar Beats",
            platform=ChannelPlatform.YOUTUBE,
            niche="emotional",
            description="Sad guitar type beats and emotional instrumentals",
            channel_id="",
            upload_frequency=2,
            active_hours=[11, 20],
            target_audience="Emotional rap fans",
            content_types=["full"]
        ),
        Channel(
            id="lofi_chill_yt",
            name="Lo-Fi Chill Station",
            platform=ChannelPlatform.YOUTUBE,
            niche="lofi",
            description="Chill lo-fi hip hop beats for study and relax",
            channel_id="",
            upload_frequency=2,
            active_hours=[8, 22],
            target_audience="Students, chill music fans",
            content_types=["full", "short"]
        ),
        Channel(
            id="afrobeats_vibes_yt",
            name="Afrobeats Vibes",
            platform=ChannelPlatform.YOUTUBE,
            niche="afrobeats",
            description="Hot afrobeats and amapiano instrumentals",
            channel_id="",
            upload_frequency=3,
            active_hours=[10, 15, 20],
            target_audience="Afrobeats fans, African diaspora",
            content_types=["full", "short"]
        ),
        Channel(
            id="rnb_smooth_yt",
            name="Smooth R&B Beats",
            platform=ChannelPlatform.YOUTUBE,
            niche="rnb",
            description="Smooth R&B and neo-soul type beats",
            channel_id="",
            upload_frequency=2,
            active_hours=[12, 19],
            target_audience="R&B artists, singers",
            content_types=["full"]
        ),
    ]
    
    def __init__(self, storage_path: str = "./output/channels.json"):
        self.storage_path = storage_path
        self.channels: Dict[str, Channel] = {}
        self.upload_history: List[UploadRecord] = []
        self.load()
        
        # Initialize default channels if none exist
        if not self.channels:
            self._init_defaults()
    
    def _init_defaults(self):
        """Initialize default channels."""
        for channel in self.DEFAULT_CHANNELS:
            self.channels[channel.id] = channel
        self.save()
    
    def load(self):
        """Load channels from storage."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    
                    # Load channels
                    for ch_data in data.get('channels', []):
                        channel = Channel(**ch_data)
                        self.channels[channel.id] = channel
                    
                    # Load upload history
                    for rec_data in data.get('upload_history', []):
                        record = UploadRecord(
                            upload_id=rec_data['upload_id'],
                            channel_id=rec_data['channel_id'],
                            beat_id=rec_data['beat_id'],
                            video_type=rec_data['video_type'],
                            uploaded_at=datetime.fromisoformat(rec_data['uploaded_at']),
                            platform_video_id=rec_data.get('platform_video_id'),
                            status=rec_data.get('status', 'pending')
                        )
                        self.upload_history.append(record)
            
            except Exception as e:
                logger.warning("channel_load_failed", error=str(e))
    
    def save(self):
        """Save channels to storage."""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        
        data = {
            'channels': [asdict(ch) for ch in self.channels.values()],
            'upload_history': [
                {
                    'upload_id': r.upload_id,
                    'channel_id': r.channel_id,
                    'beat_id': r.beat_id,
                    'video_type': r.video_type,
                    'uploaded_at': r.uploaded_at.isoformat(),
                    'platform_video_id': r.platform_video_id,
                    'status': r.status
                }
                for r in self.upload_history
            ]
        }
        
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def get_channel(self, channel_id: str) -> Optional[Channel]:
        """Get a channel by ID."""
        return self.channels.get(channel_id)
    
    def get_channels_for_genre(self, genre: str) -> List[Channel]:
        """Get channels that accept a specific genre."""
        return [
            ch for ch in self.channels.values()
            if ch.is_active and (ch.niche == genre or ch.niche == 'general')
        ]
    
    def assign_beat_to_channel(self, beat_info: Dict[str, Any],
                                video_type: str = "full") -> Optional[Channel]:
        """Intelligently assign a beat to the best channel.
        
        Considers:
        - Genre match
        - Channel upload frequency (don't overload)
        - Time since last upload
        - Content type compatibility
        
        Returns:
            Best channel or None if no suitable channel
        """
        genre = beat_info.get('genre', 'default')
        
        # Get candidate channels
        candidates = self.get_channels_for_genre(genre)
        
        if not candidates:
            # Fallback to general channels
            candidates = [
                ch for ch in self.channels.values()
                if ch.is_active and ch.niche == 'general'
            ]
        
        if not candidates:
            logger.warning("no_channel_for_genre", genre=genre)
            return None
        
        # Score each channel
        best_channel = None
        best_score = -1
        
        for channel in candidates:
            score = self._score_channel_for_beat(channel, genre, video_type)
            
            if score > best_score:
                best_score = score
                best_channel = channel
        
        if best_channel:
            logger.info("channel_assigned",
                       beat_id=beat_info.get('beat_id'),
                       channel=best_channel.id,
                       score=best_score)
        
        return best_channel
    
    def _score_channel_for_beat(self, channel: Channel, 
                                 genre: str, video_type: str) -> float:
        """Score how well a channel fits a beat."""
        score = 0.0
        
        # Genre match (highest weight)
        if channel.niche == genre:
            score += 50
        elif channel.niche in genre or genre in channel.niche:
            score += 30
        
        # Content type compatibility
        if video_type in channel.content_types:
            score += 20
        
        # Upload frequency check (penalize if over limit)
        today_uploads = self._count_today_uploads(channel.id)
        if today_uploads < channel.upload_frequency:
            score += 20 * (1 - today_uploads / channel.upload_frequency)
        else:
            score -= 30  # Over limit
        
        # Time since last upload (prefer channels that haven't uploaded recently)
        last_upload = self._get_last_upload_time(channel.id)
        if last_upload:
            hours_since = (datetime.now() - last_upload).total_seconds() / 3600
            if hours_since < 2:
                score -= 20  # Too recent
            elif hours_since > 6:
                score += 10  # Good gap
        
        # Platform-specific bonuses
        if channel.platform == ChannelPlatform.YOUTUBE:
            score += 5  # YouTube is primary
        
        return score
    
    def _count_today_uploads(self, channel_id: str) -> int:
        """Count uploads for a channel today."""
        today_start = datetime.now().replace(hour=0, minute=0, second=0)
        
        return sum(
            1 for r in self.upload_history
            if r.channel_id == channel_id
            and r.uploaded_at >= today_start
            and r.status in ('uploaded', 'pending')
        )
    
    def _get_last_upload_time(self, channel_id: str) -> Optional[datetime]:
        """Get last upload time for a channel."""
        channel_uploads = [
            r for r in self.upload_history
            if r.channel_id == channel_id
            and r.status in ('uploaded', 'pending')
        ]
        
        if not channel_uploads:
            return None
        
        return max(r.uploaded_at for r in channel_uploads)
    
    def record_upload(self, channel_id: str, beat_id: str,
                      video_type: str, platform_video_id: str = None):
        """Record an upload."""
        record = UploadRecord(
            upload_id=f"{channel_id}_{beat_id}_{datetime.now().timestamp()}",
            channel_id=channel_id,
            beat_id=beat_id,
            video_type=video_type,
            uploaded_at=datetime.now(),
            platform_video_id=platform_video_id,
            status='pending'
        )
        
        self.upload_history.append(record)
        self.save()
        
        logger.info("upload_recorded",
                   channel=channel_id,
                   beat_id=beat_id,
                   video_type=video_type)
    
    def update_upload_status(self, upload_id: str, status: str,
                             platform_video_id: str = None):
        """Update upload status."""
        for record in self.upload_history:
            if record.upload_id == upload_id:
                record.status = status
                if platform_video_id:
                    record.platform_video_id = platform_video_id
                break
        
        self.save()
    
    def get_channel_stats(self, channel_id: str) -> Dict[str, Any]:
        """Get statistics for a channel."""
        channel = self.channels.get(channel_id)
        if not channel:
            return {}
        
        today_uploads = self._count_today_uploads(channel_id)
        total_uploads = len([r for r in self.upload_history if r.channel_id == channel_id])
        
        # Uploads by type
        type_counts = {}
        for r in self.upload_history:
            if r.channel_id == channel_id:
                type_counts[r.video_type] = type_counts.get(r.video_type, 0) + 1
        
        # Recent uploads (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_uploads = len([
            r for r in self.upload_history
            if r.channel_id == channel_id
            and r.uploaded_at >= week_ago
        ])
        
        return {
            'channel_id': channel_id,
            'channel_name': channel.name,
            'niche': channel.niche,
            'platform': channel.platform.value,
            'is_active': channel.is_active,
            'upload_frequency': channel.upload_frequency,
            'today_uploads': today_uploads,
            'remaining_today': max(0, channel.upload_frequency - today_uploads),
            'total_uploads': total_uploads,
            'recent_7_days': recent_uploads,
            'uploads_by_type': type_counts,
            'last_upload': self._get_last_upload_time(channel_id)
        }
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get stats for all channels."""
        return {
            channel_id: self.get_channel_stats(channel_id)
            for channel_id in self.channels.keys()
        }
    
    def add_channel(self, channel: Channel):
        """Add a new channel."""
        self.channels[channel.id] = channel
        self.save()
        logger.info("channel_added", channel_id=channel.id, name=channel.name)
    
    def remove_channel(self, channel_id: str):
        """Remove a channel."""
        if channel_id in self.channels:
            del self.channels[channel_id]
            self.save()
            logger.info("channel_removed", channel_id=channel_id)
    
    def get_upload_schedule(self, channel_id: str, 
                           days: int = 7) -> List[Dict[str, Any]]:
        """Get upcoming upload schedule for a channel."""
        channel = self.channels.get(channel_id)
        if not channel:
            return []
        
        schedule = []
        now = datetime.now()
        
        for day_offset in range(days):
            day = now + timedelta(days=day_offset)
            
            for hour in channel.active_hours:
                scheduled_time = day.replace(hour=hour, minute=0, second=0)
                
                if scheduled_time > now:
                    schedule.append({
                        'channel_id': channel_id,
                        'channel_name': channel.name,
                        'scheduled_time': scheduled_time.isoformat(),
                        'available': True
                    })
        
        return schedule[:channel.upload_frequency * days]
