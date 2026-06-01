"""Scheduling system for automated beat promotion.

Manages:
- Optimal posting times per platform
- Content calendar
- Queue management
- Analytics tracking
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import structlog

logger = structlog.get_logger()


@dataclass
class PostSchedule:
    """Schedule for a single post."""
    beat_id: str
    platform: str
    scheduled_time: datetime
    content: Dict[str, Any]
    status: str = "pending"  # pending, ready, posted, failed
    posted_at: Optional[datetime] = None
    post_url: Optional[str] = None
    engagement: Optional[Dict[str, int]] = None


class ContentCalendar:
    """Manages posting schedule across platforms."""
    
    # Optimal posting times (local time, 24h format)
    # Based on general social media best practices
    OPTIMAL_TIMES = {
        "youtube": ["14:00", "17:00", "20:00"],  # Afternoon/evening
        "tiktok": ["09:00", "12:00", "19:00"],   # Morning, lunch, evening
        "instagram": ["11:00", "13:00", "19:00"], # Midday, evening
        "beatstars": ["10:00", "15:00"],          # Business hours
        "airbit": ["10:00", "15:00"]
    }
    
    # Posting frequency (posts per day max)
    DAILY_LIMITS = {
        "youtube": 1,
        "tiktok": 3,
        "instagram": 2,
        "beatstars": 5,
        "airbit": 5
    }
    
    def __init__(self, calendar_path: str = "./output/content_calendar.json"):
        self.calendar_path = calendar_path
        self.schedules: List[PostSchedule] = []
        self.load_calendar()
    
    def load_calendar(self):
        """Load existing calendar."""
        if os.path.exists(self.calendar_path):
            with open(self.calendar_path, 'r') as f:
                data = json.load(f)
                self.schedules = [
                    PostSchedule(
                        beat_id=s["beat_id"],
                        platform=s["platform"],
                        scheduled_time=datetime.fromisoformat(s["scheduled_time"]),
                        content=s["content"],
                        status=s.get("status", "pending"),
                        posted_at=datetime.fromisoformat(s["posted_at"]) if s.get("posted_at") else None,
                        post_url=s.get("post_url"),
                        engagement=s.get("engagement")
                    )
                    for s in data
                ]
    
    def save_calendar(self):
        """Save calendar to disk."""
        os.makedirs(os.path.dirname(self.calendar_path), exist_ok=True)
        with open(self.calendar_path, 'w') as f:
            json.dump([asdict(s) for s in self.schedules], f, 
                     default=str, indent=2)
    
    def schedule_beat(self, beat_id: str, platforms: List[str],
                      metadata: Dict[str, Any],
                      start_date: Optional[datetime] = None) -> List[PostSchedule]:
        """Schedule a beat across multiple platforms.
        
        Staggers posts to avoid spam and maximize reach.
        """
        if start_date is None:
            start_date = datetime.now() + timedelta(hours=1)
        
        schedules = []
        current_date = start_date
        
        for platform in platforms:
            # Check daily limit
            daily_posts = self._count_posts_for_date(platform, current_date)
            
            if daily_posts >= self.DAILY_LIMITS.get(platform, 1):
                # Move to next day
                current_date = current_date + timedelta(days=1)
                current_date = current_date.replace(hour=9, minute=0)
            
            # Pick optimal time
            optimal_times = self.OPTIMAL_TIMES.get(platform, ["12:00"])
            time_str = optimal_times[daily_posts % len(optimal_times)]
            hour, minute = map(int, time_str.split(":"))
            
            scheduled_time = current_date.replace(hour=hour, minute=minute)
            
            # Ensure it's in the future
            if scheduled_time < datetime.now():
                scheduled_time = scheduled_time + timedelta(days=1)
            
            schedule = PostSchedule(
                beat_id=beat_id,
                platform=platform,
                scheduled_time=scheduled_time,
                content={
                    "title": metadata.get("title", ""),
                    "description": metadata.get("description", ""),
                    "tags": metadata.get("tags", []),
                    "hashtags": metadata.get("hashtags", "")
                }
            )
            
            self.schedules.append(schedule)
            schedules.append(schedule)
            
            logger.info("scheduled_post",
                       beat_id=beat_id,
                       platform=platform,
                       time=scheduled_time.isoformat())
        
        self.save_calendar()
        return schedules
    
    def _count_posts_for_date(self, platform: str, date: datetime) -> int:
        """Count scheduled posts for a platform on a given date."""
        date_start = date.replace(hour=0, minute=0, second=0)
        date_end = date_start + timedelta(days=1)
        
        return sum(
            1 for s in self.schedules
            if s.platform == platform
            and date_start <= s.scheduled_time < date_end
            and s.status in ("pending", "ready", "posted")
        )
    
    def get_ready_posts(self) -> List[PostSchedule]:
        """Get posts that are ready to be published."""
        now = datetime.now()
        ready = [
            s for s in self.schedules
            if s.status == "pending" and s.scheduled_time <= now
        ]
        
        # Mark as ready
        for post in ready:
            post.status = "ready"
        
        if ready:
            self.save_calendar()
        
        return ready
    
    def mark_posted(self, beat_id: str, platform: str, 
                    post_url: str):
        """Mark a post as successfully published."""
        for schedule in self.schedules:
            if schedule.beat_id == beat_id and schedule.platform == platform:
                schedule.status = "posted"
                schedule.posted_at = datetime.now()
                schedule.post_url = post_url
                break
        
        self.save_calendar()
    
    def mark_failed(self, beat_id: str, platform: str):
        """Mark a post as failed."""
        for schedule in self.schedules:
            if schedule.beat_id == beat_id and schedule.platform == platform:
                schedule.status = "failed"
                break
        
        self.save_calendar()
    
    def get_upcoming(self, days: int = 7) -> List[PostSchedule]:
        """Get upcoming scheduled posts."""
        now = datetime.now()
        end = now + timedelta(days=days)
        
        return [
            s for s in self.schedules
            if s.status in ("pending", "ready")
            and now <= s.scheduled_time <= end
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get posting statistics."""
        total = len(self.schedules)
        posted = sum(1 for s in self.schedules if s.status == "posted")
        pending = sum(1 for s in self.schedules if s.status == "pending")
        failed = sum(1 for s in self.schedules if s.status == "failed")
        
        platform_breakdown = {}
        for platform in self.OPTIMAL_TIMES.keys():
            platform_posts = [s for s in self.schedules if s.platform == platform]
            platform_breakdown[platform] = {
                "total": len(platform_posts),
                "posted": sum(1 for s in platform_posts if s.status == "posted"),
                "pending": sum(1 for s in platform_posts if s.status == "pending"),
                "failed": sum(1 for s in platform_posts if s.status == "failed")
            }
        
        return {
            "total_posts": total,
            "posted": posted,
            "pending": pending,
            "failed": failed,
            "success_rate": posted / total if total > 0 else 0,
            "platforms": platform_breakdown
        }


class AnalyticsTracker:
    """Track engagement and performance metrics."""
    
    def __init__(self, analytics_path: str = "./output/analytics.json"):
        self.analytics_path = analytics_path
        self.data: Dict[str, Any] = {}
        self.load()
    
    def load(self):
        """Load analytics data."""
        if os.path.exists(self.analytics_path):
            with open(self.analytics_path, 'r') as f:
                self.data = json.load(f)
    
    def save(self):
        """Save analytics data."""
        os.makedirs(os.path.dirname(self.analytics_path), exist_ok=True)
        with open(self.analytics_path, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def record_post(self, beat_id: str, platform: str, post_url: str):
        """Record a new post."""
        if beat_id not in self.data:
            self.data[beat_id] = {}
        
        self.data[beat_id][platform] = {
            "post_url": post_url,
            "posted_at": datetime.now().isoformat(),
            "engagement": {
                "views": 0,
                "likes": 0,
                "comments": 0,
                "shares": 0
            }
        }
        
        self.save()
    
    def update_engagement(self, beat_id: str, platform: str,
                          metrics: Dict[str, int]):
        """Update engagement metrics for a post."""
        if beat_id in self.data and platform in self.data[beat_id]:
            self.data[beat_id][platform]["engagement"].update(metrics)
            self.data[beat_id][platform]["last_updated"] = datetime.now().isoformat()
            self.save()
    
    def get_beat_performance(self, beat_id: str) -> Dict[str, Any]:
        """Get performance summary for a beat."""
        if beat_id not in self.data:
            return {}
        
        platforms = self.data[beat_id]
        total_views = sum(p["engagement"].get("views", 0) for p in platforms.values())
        total_likes = sum(p["engagement"].get("likes", 0) for p in platforms.values())
        
        return {
            "beat_id": beat_id,
            "platforms": platforms,
            "total_views": total_views,
            "total_likes": total_likes,
            "platform_count": len(platforms)
        }
    
    def get_top_performers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top performing beats."""
        performances = []
        
        for beat_id in self.data:
            perf = self.get_beat_performance(beat_id)
            if perf:
                performances.append(perf)
        
        performances.sort(key=lambda x: x["total_views"], reverse=True)
        return performances[:limit]
