"""YouTube search rank tracker.

Monitors where videos rank for target keywords over time.
"""

import os
import json
import time
import urllib.request
import urllib.parse
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
import structlog

logger = structlog.get_logger()


@dataclass
class RankEntry:
    """A single rank measurement."""
    keyword: str
    position: int  # 1 = top result
    video_title: str
    video_id: str
    checked_at: datetime


class RankTracker:
    """Track YouTube search rankings."""
    
    def __init__(self, storage_path: str = "./output/rank_data.json"):
        self.storage_path = storage_path
        self.history: Dict[str, List[RankEntry]] = {}  # keyword -> entries
        self.load()
    
    def load(self):
        """Load rank history."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    for keyword, entries in data.items():
                        self.history[keyword] = [
                            RankEntry(
                                keyword=e['keyword'],
                                position=e['position'],
                                video_title=e['video_title'],
                                video_id=e['video_id'],
                                checked_at=datetime.fromisoformat(e['checked_at'])
                            )
                            for e in entries
                        ]
            except Exception as e:
                logger.warning("rank_data_load_failed", error=str(e))
    
    def save(self):
        """Save rank history."""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        
        data = {}
        for keyword, entries in self.history.items():
            data[keyword] = [
                {
                    'keyword': e.keyword,
                    'position': e.position,
                    'video_title': e.video_title,
                    'video_id': e.video_id,
                    'checked_at': e.checked_at.isoformat()
                }
                for e in entries
            ]
        
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def check_rank(self, keyword: str, target_video_id: str,
                   max_results: int = 50) -> Optional[RankEntry]:
        """Check ranking position for a keyword.
        
        Uses YouTube search scraping (no API required).
        
        Args:
            keyword: Search keyword
            target_video_id: Video ID to find
            max_results: Max results to check
        
        Returns:
            RankEntry if found, None otherwise
        """
        try:
            # YouTube search URL
            encoded = urllib.parse.quote(keyword)
            url = f"https://www.youtube.com/results?search_query={encoded}&sp=CAI%253D"  # Sort by upload date
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=15) as response:
                html = response.read().decode('utf-8')
            
            # Extract video IDs from search results
            import re
            video_pattern = r'"videoId":"([^"]+)"'
            video_ids = re.findall(video_pattern, html)
            
            # Also extract titles
            title_pattern = r'"title":\{"runs":\[\{"text":"([^"]+)"\}'
            titles = re.findall(title_pattern, html)
            
            # Find target video
            for i, vid in enumerate(video_ids[:max_results]):
                if vid == target_video_id:
                    title = titles[i] if i < len(titles) else "Unknown"
                    
                    entry = RankEntry(
                        keyword=keyword,
                        position=i + 1,
                        video_title=title,
                        video_id=vid,
                        checked_at=datetime.now()
                    )
                    
                    # Store
                    if keyword not in self.history:
                        self.history[keyword] = []
                    self.history[keyword].append(entry)
                    self.save()
                    
                    logger.info("rank_checked",
                               keyword=keyword,
                               position=entry.position,
                               video_id=target_video_id)
                    
                    return entry
            
            # Not found in results
            logger.info("rank_not_found",
                       keyword=keyword,
                       video_id=target_video_id,
                       checked_results=len(video_ids))
            
            return None
        
        except Exception as e:
            logger.error("rank_check_failed", keyword=keyword, error=str(e))
            return None
    
    def get_rank_history(self, keyword: str) -> List[RankEntry]:
        """Get rank history for a keyword."""
        return self.history.get(keyword, [])
    
    def get_rank_trend(self, keyword: str, 
                       days: int = 30) -> Dict[str, Any]:
        """Get rank trend for a keyword.
        
        Returns:
            Dict with trend analysis
        """
        entries = self.get_rank_history(keyword)
        
        if not entries:
            return {'keyword': keyword, 'entries': 0, 'trend': 'no_data'}
        
        # Filter to recent entries
        cutoff = datetime.now() - timedelta(days=days)
        recent = [e for e in entries if e.checked_at > cutoff]
        
        if len(recent) < 2:
            return {
                'keyword': keyword,
                'entries': len(recent),
                'current_position': recent[-1].position if recent else None,
                'trend': 'insufficient_data'
            }
        
        # Calculate trend
        positions = [e.position for e in recent]
        avg_position = sum(positions) / len(positions)
        
        # Linear regression for trend direction
        x = list(range(len(positions)))
        n = len(x)
        
        sum_x = sum(x)
        sum_y = sum(positions)
        sum_xy = sum(xi * yi for xi, yi in zip(x, positions))
        sum_x2 = sum(xi ** 2 for xi in x)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2) if (n * sum_x2 - sum_x ** 2) != 0 else 0
        
        if slope < -0.5:
            trend = 'improving'
        elif slope > 0.5:
            trend = 'declining'
        else:
            trend = 'stable'
        
        return {
            'keyword': keyword,
            'entries': len(recent),
            'current_position': positions[-1],
            'average_position': round(avg_position, 1),
            'best_position': min(positions),
            'worst_position': max(positions),
            'trend': trend,
            'slope': round(slope, 3)
        }
    
    def get_all_keywords(self) -> List[str]:
        """Get all tracked keywords."""
        return list(self.history.keys())
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get overall ranking performance summary."""
        total_keywords = len(self.history)
        
        if total_keywords == 0:
            return {'total_keywords': 0}
        
        # Get latest position for each keyword
        latest_positions = []
        for keyword, entries in self.history.items():
            if entries:
                latest_positions.append(entries[-1].position)
        
        if not latest_positions:
            return {'total_keywords': total_keywords}
        
        # Calculate metrics
        top_3 = sum(1 for p in latest_positions if p <= 3)
        top_10 = sum(1 for p in latest_positions if p <= 10)
        top_20 = sum(1 for p in latest_positions if p <= 20)
        
        return {
            'total_keywords': total_keywords,
            'tracked_videos': len(set(
                e.video_id 
                for entries in self.history.values() 
                for e in entries
            )),
            'average_position': round(sum(latest_positions) / len(latest_positions), 1),
            'top_3_count': top_3,
            'top_10_count': top_10,
            'top_20_count': top_20,
            'top_3_percentage': round(top_3 / len(latest_positions) * 100, 1),
            'top_10_percentage': round(top_10 / len(latest_positions) * 100, 1),
        }
