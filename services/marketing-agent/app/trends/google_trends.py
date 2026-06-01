"""Google Trends integration.

Uses pytrends or direct API to track search interest over time.
"""

import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import structlog

logger = structlog.get_logger()


class GoogleTrendDetector:
    """Detect trends using Google Trends data."""
    
    def __init__(self, cache_path: str = "./output/google_trends.json"):
        self.cache_path = cache_path
        self.cache: Dict[str, Any] = {}
        self.load_cache()
    
    def load_cache(self):
        """Load cached trend data."""
        if os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, 'r') as f:
                    self.cache = json.load(f)
            except Exception as e:
                logger.warning("google_trends_cache_load_failed", error=str(e))
    
    def save_cache(self):
        """Save trend cache."""
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        with open(self.cache_path, 'w') as f:
            json.dump(self.cache, f, indent=2)
    
    def get_interest_over_time(self, keywords: List[str],
                                timeframe: str = "today 3-m") -> Dict[str, Any]:
        """Get Google Trends interest over time.
        
        Args:
            keywords: List of keywords to compare
            timeframe: Time range (e.g., "today 3-m", "today 12-m")
        
        Returns:
            Interest data by keyword
        """
        try:
            from pytrends.request import TrendReq
            
            pytrends = TrendReq(hl='en-GB', tz=0)
            pytrends.build_payload(keywords, cat=0, timeframe=timeframe)
            
            data = pytrends.interest_over_time()
            
            if data.empty:
                return {}
            
            result = {}
            for keyword in keywords:
                if keyword in data.columns:
                    values = data[keyword].tolist()
                    result[keyword] = {
                        'current_interest': values[-1] if values else 0,
                        'average_interest': sum(values) / len(values) if values else 0,
                        'peak_interest': max(values) if values else 0,
                        'trend_direction': 'up' if len(values) > 1 and values[-1] > values[0] else 'down',
                        'data_points': len(values)
                    }
            
            return result
        
        except ImportError:
            logger.warning("pytrends_not_installed")
            return self._get_mock_trends(keywords)
        
        except Exception as e:
            logger.error("google_trends_failed", error=str(e))
            return self._get_mock_trends(keywords)
    
    def get_related_queries(self, keyword: str) -> Dict[str, List[str]]:
        """Get related queries for a keyword."""
        try:
            from pytrends.request import TrendReq
            
            pytrends = TrendReq(hl='en-GB', tz=0)
            pytrends.build_payload([keyword], cat=0, timeframe='today 3-m')
            
            related = pytrends.related_queries()
            
            if keyword in related:
                top = related[keyword].get('top', [])
                rising = related[keyword].get('rising', [])
                
                return {
                    'top': [item['query'] for item in top[:10]] if isinstance(top, list) else [],
                    'rising': [item['query'] for item in rising[:10]] if isinstance(rising, list) else []
                }
            
            return {'top': [], 'rising': []}
        
        except Exception as e:
            logger.warning("related_queries_failed", error=str(e))
            return {'top': [], 'rising': []}
    
    def get_trending_searches(self, country: str = "united_kingdom") -> List[str]:
        """Get current trending searches."""
        try:
            from pytrends.request import TrendReq
            
            pytrends = TrendReq(hl='en-GB', tz=0)
            trending = pytrends.trending_searches(pn=country)
            
            return trending[0].tolist()[:20]
        
        except Exception as e:
            logger.warning("trending_searches_failed", error=str(e))
            return []
    
    def analyze_genre_trend(self, genre: str) -> Dict[str, Any]:
        """Analyze trend data for a specific genre."""
        keywords = [
            f"{genre} type beat",
            f"{genre} beat",
            f"free {genre} beat",
        ]
        
        interest = self.get_interest_over_time(keywords)
        related = self.get_related_queries(f"{genre} type beat")
        
        # Calculate overall trend score
        scores = []
        for kw_data in interest.values():
            if isinstance(kw_data, dict):
                current = kw_data.get('current_interest', 0)
                avg = kw_data.get('average_interest', 1)
                scores.append(current / max(avg, 1))
        
        avg_score = sum(scores) / len(scores) if scores else 1.0
        
        return {
            'genre': genre,
            'interest_data': interest,
            'related_queries': related,
            'trend_score': round(avg_score, 3),
            'is_trending': avg_score > 1.2,
            'is_declining': avg_score < 0.8,
            'analyzed_at': datetime.now().isoformat()
        }
    
    def _get_mock_trends(self, keywords: List[str]) -> Dict[str, Any]:
        """Generate mock trend data when pytrends is unavailable."""
        import random
        
        result = {}
        for keyword in keywords:
            base = random.randint(30, 70)
            result[keyword] = {
                'current_interest': base + random.randint(-10, 10),
                'average_interest': base,
                'peak_interest': base + random.randint(20, 40),
                'trend_direction': random.choice(['up', 'down', 'stable']),
                'data_points': 90,
                'note': 'mock_data'
            }
        
        return result
