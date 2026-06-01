"""YouTube Trend Detection.

Scrapes YouTube trending page and search suggestions to detect
viral content patterns in the beat-making space.
"""

import json
import urllib.request
import urllib.parse
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
import structlog

logger = structlog.get_logger()


@dataclass
class TrendingVideo:
    """A trending video entry."""
    title: str
    video_id: str
    channel: str
    view_count: str
    category: str
    rank: int


class YouTubeTrendDetector:
    """Detect trends from YouTube."""
    
    def __init__(self, cache_path: str = "./output/youtube_trends.json"):
        self.cache_path = cache_path
        self.trending_cache: List[TrendingVideo] = []
        self.last_update: Optional[datetime] = None
    
    def get_trending(self, category: str = "music", 
                     max_results: int = 50) -> List[TrendingVideo]:
        """Get trending videos from YouTube.
        
        Scrapes YouTube's trending page.
        """
        try:
            # YouTube trending URL
            url = f"https://www.youtube.com/feed/trending?gl=GB"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=15) as response:
                html = response.read().decode('utf-8')
            
            # Extract video data from initial data script
            script_pattern = r'var ytInitialData = ({.+?});</script>'
            match = re.search(script_pattern, html)
            
            if not match:
                logger.warning("no_yt_initial_data_found")
                return []
            
            data = json.loads(match.group(1))
            
            # Navigate to trending videos
            videos = []
            try:
                contents = data['contents']['twoColumnBrowseResultsRenderer']['tabs'][0]['tabRenderer']['content']['sectionListRenderer']['contents']
                
                rank = 1
                for section in contents:
                    item_section = section.get('itemSectionRenderer', {})
                    for item in item_section.get('contents', []):
                        video_renderer = item.get('videoRenderer', {})
                        
                        if video_renderer:
                            title = video_renderer.get('title', {}).get('runs', [{}])[0].get('text', '')
                            video_id = video_renderer.get('videoId', '')
                            channel = video_renderer.get('ownerText', {}).get('runs', [{}])[0].get('text', '')
                            view_count = video_renderer.get('viewCountText', {}).get('simpleText', '')
                            
                            videos.append(TrendingVideo(
                                title=title,
                                video_id=video_id,
                                channel=channel,
                                view_count=view_count,
                                category='music',
                                rank=rank
                            ))
                            rank += 1
            
            except (KeyError, IndexError) as e:
                logger.warning("trending_parse_error", error=str(e))
            
            self.trending_cache = videos[:max_results]
            self.last_update = datetime.now()
            
            logger.info("youtube_trending_fetched", count=len(videos))
            return self.trending_cache
        
        except Exception as e:
            logger.error("youtube_trending_failed", error=str(e))
            return []
    
    def get_trending_keywords(self, genre: str = None) -> List[Dict[str, Any]]:
        """Extract trending keywords from trending videos."""
        videos = self.get_trending()
        
        if not videos:
            return []
        
        # Extract keywords from titles
        keyword_counts = {}
        
        for video in videos:
            title = video.title.lower()
            words = re.findall(r'\b\w+\b', title)
            
            for word in words:
                if len(word) > 3 and word not in ['this', 'that', 'with', 'from', 'have', 'been']:
                    keyword_counts[word] = keyword_counts.get(word, 0) + 1
        
        # Sort by frequency
        sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
        
        results = []
        for keyword, count in sorted_keywords[:20]:
            results.append({
                'keyword': keyword,
                'mentions': count,
                'trend_score': min(1.0, count / 10),
                'source': 'youtube_trending'
            })
        
        return results
    
    def get_search_trends(self, query: str = "type beat") -> List[str]:
        """Get trending search queries related to type beats."""
        try:
            encoded = urllib.parse.quote(query)
            url = f"http://suggestqueries.google.com/complete/search?client=youtube&ds=yt&q={encoded}"
            
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                suggestions = [item[0] for item in data[1]]
                return suggestions
        
        except Exception as e:
            logger.warning("search_trends_failed", error=str(e))
            return []
    
    def analyze_trend(self, keyword: str) -> Dict[str, Any]:
        """Analyze a specific keyword's trend status."""
        # Get search suggestions
        suggestions = self.get_search_trends(keyword)
        
        # Check if keyword appears in trending
        trending = self.get_trending()
        in_trending = any(keyword.lower() in v.title.lower() for v in trending)
        
        # Estimate momentum from suggestion count
        momentum = min(1.0, len(suggestions) / 10)
        
        return {
            'keyword': keyword,
            'is_trending': in_trending,
            'suggestion_count': len(suggestions),
            'momentum': round(momentum, 2),
            'related_queries': suggestions[:5],
            'analyzed_at': datetime.now().isoformat()
        }
