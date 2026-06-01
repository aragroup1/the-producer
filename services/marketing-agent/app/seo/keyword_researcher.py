"""Keyword research engine for YouTube SEO.

Discovers trending keywords, estimates search volume,
and identifies ranking opportunities.
"""

import json
import urllib.request
import urllib.parse
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import structlog

logger = structlog.get_logger()


@dataclass
class KeywordData:
    """Keyword research data."""
    keyword: str
    search_volume: int = 0
    competition: float = 0.0  # 0-1, higher = more competitive
    trend_score: float = 0.0  # Growth rate
    cpc: float = 0.0  # Estimated cost per click
    difficulty: float = 0.0  # Ranking difficulty 0-100
    related_keywords: List[str] = None
    last_updated: datetime = None


class KeywordResearcher:
    """Research keywords for beat marketing."""
    
    # High-value base keywords for beat marketing
    BASE_KEYWORDS = [
        "type beat", "free type beat", "instrumental", "beats for sale",
        "hip hop beat", "rap beat", "trap beat", "drill beat",
        "rnb beat", "lofi beat", "afrobeats instrumental",
    ]
    
    # Seasonal/trending modifiers
    TRENDING_MODIFIERS = [
        "2026", "new", "hot", "trending", "viral",
        "emotional", "dark", "melodic", "aggressive",
    ]
    
    def __init__(self, cache_path: str = "./output/keyword_cache.json"):
        self.cache_path = cache_path
        self.cache: Dict[str, KeywordData] = {}
        self.load_cache()
    
    def load_cache(self):
        """Load cached keyword data."""
        import os
        if os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, 'r') as f:
                    data = json.load(f)
                    for kw, item in data.items():
                        self.cache[kw] = KeywordData(
                            keyword=kw,
                            search_volume=item.get('search_volume', 0),
                            competition=item.get('competition', 0),
                            trend_score=item.get('trend_score', 0),
                            cpc=item.get('cpc', 0),
                            difficulty=item.get('difficulty', 0),
                            related_keywords=item.get('related_keywords', []),
                            last_updated=datetime.fromisoformat(item['last_updated']) if item.get('last_updated') else None
                        )
            except Exception as e:
                logger.warning("keyword_cache_load_failed", error=str(e))
    
    def save_cache(self):
        """Save keyword cache."""
        import os
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        
        data = {}
        for kw, kd in self.cache.items():
            data[kw] = {
                'search_volume': kd.search_volume,
                'competition': kd.competition,
                'trend_score': kd.trend_score,
                'cpc': kd.cpc,
                'difficulty': kd.difficulty,
                'related_keywords': kd.related_keywords,
                'last_updated': kd.last_updated.isoformat() if kd.last_updated else None
            }
        
        with open(self.cache_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_youtube_suggestions(self, query: str, max_results: int = 10) -> List[str]:
        """Get YouTube search autocomplete suggestions.
        
        Uses Google's suggest API which powers YouTube search.
        """
        try:
            encoded = urllib.parse.quote(query)
            url = f"http://suggestqueries.google.com/complete/search?client=youtube&ds=yt&q={encoded}"
            
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                suggestions = [item[0] for item in data[1]]
                return suggestions[:max_results]
        
        except Exception as e:
            logger.warning("youtube_suggestions_failed", query=query, error=str(e))
            return []
    
    def research_genre_keywords(self, genre: str) -> List[KeywordData]:
        """Research keywords for a specific genre.
        
        Returns list of KeywordData with volume and competition estimates.
        """
        queries = [
            f"{genre} type beat",
            f"free {genre} beat",
            f"{genre} instrumental",
            f"{genre} beat 2026",
            f"best {genre} beats",
        ]
        
        all_keywords = []
        
        for query in queries:
            suggestions = self.get_youtube_suggestions(query, max_results=10)
            
            for suggestion in suggestions:
                if suggestion not in self.cache:
                    # Estimate metrics
                    kd = self._estimate_metrics(suggestion, genre)
                    self.cache[suggestion] = kd
                
                all_keywords.append(self.cache[suggestion])
        
        self.save_cache()
        
        # Sort by opportunity score (volume / difficulty)
        all_keywords.sort(key=lambda k: k.search_volume / max(k.difficulty, 1), reverse=True)
        
        return all_keywords[:20]
    
    def _estimate_metrics(self, keyword: str, genre: str) -> KeywordData:
        """Estimate search metrics for a keyword.
        
        Uses heuristics since we don't have direct API access to search volumes.
        """
        # Base volume estimate based on keyword characteristics
        volume = self._estimate_volume(keyword)
        
        # Competition estimate (more specific = less competitive)
        words = keyword.split()
        competition = max(0.1, min(1.0, 1.0 - (len(words) - 2) * 0.15))
        
        # Difficulty (combination of competition and specificity)
        difficulty = competition * 80 + (1 - competition) * 20
        
        # Trend score (higher for recent year mentions)
        trend_score = 0.5
        if '2026' in keyword or '2025' in keyword:
            trend_score = 0.9
        elif 'new' in keyword.lower() or 'hot' in keyword.lower():
            trend_score = 0.8
        
        # Related keywords
        related = self.get_youtube_suggestions(keyword, max_results=5)
        
        return KeywordData(
            keyword=keyword,
            search_volume=volume,
            competition=competition,
            trend_score=trend_score,
            difficulty=difficulty,
            related_keywords=related,
            last_updated=datetime.now()
        )
    
    def _estimate_volume(self, keyword: str) -> int:
        """Estimate monthly search volume."""
        # Heuristic based on keyword characteristics
        base_volume = 1000
        
        # Popular terms boost
        popular_terms = ['type beat', 'free', 'instrumental', 'hip hop', 'trap']
        for term in popular_terms:
            if term in keyword.lower():
                base_volume += 2000
        
        # Artist names boost
        artists = ['travis scott', 'drake', 'central cee', 'pop smoke', 'burna boy']
        for artist in artists:
            if artist in keyword.lower():
                base_volume += 3000
        
        # Year boost
        if '2026' in keyword:
            base_volume += 1500
        
        # Long-tail penalty (more specific = fewer searches)
        word_count = len(keyword.split())
        if word_count > 6:
            base_volume = int(base_volume * 0.3)
        elif word_count > 4:
            base_volume = int(base_volume * 0.6)
        
        # Add some randomness
        import random
        base_volume = int(base_volume * random.uniform(0.8, 1.2))
        
        return max(100, base_volume)
    
    def find_opportunities(self, genre: str, min_volume: int = 500,
                           max_difficulty: float = 60) -> List[KeywordData]:
        """Find keyword opportunities (high volume, low competition).
        
        Args:
            genre: Genre to research
            min_volume: Minimum estimated monthly searches
            max_difficulty: Maximum ranking difficulty (0-100)
        
        Returns:
            List of opportunity keywords
        """
        keywords = self.research_genre_keywords(genre)
        
        opportunities = [
            kw for kw in keywords
            if kw.search_volume >= min_volume
            and kw.difficulty <= max_difficulty
        ]
        
        # Sort by opportunity score
        opportunities.sort(
            key=lambda k: (k.search_volume * k.trend_score) / max(k.difficulty, 1),
            reverse=True
        )
        
        logger.info("opportunities_found",
                   genre=genre,
                   count=len(opportunities),
                   top_keyword=opportunities[0].keyword if opportunities else None)
        
        return opportunities[:10]
    
    def get_trending_keywords(self, genre: str, 
                              days: int = 7) -> List[str]:
        """Get currently trending keywords for a genre.
        
        Combines multiple data sources to find what's hot right now.
        """
        trending = []
        
        # YouTube suggestions for trending queries
        trending_queries = [
            f"trending {genre} beat",
            f"viral {genre} type beat",
            f"{genre} beat 2026",
        ]
        
        for query in trending_queries:
            suggestions = self.get_youtube_suggestions(query, max_results=5)
            trending.extend(suggestions)
        
        # Deduplicate
        trending = list(dict.fromkeys(trending))
        
        # Score and filter
        scored = []
        for kw in trending:
            if kw in self.cache:
                kd = self.cache[kw]
                if kd.trend_score > 0.6:
                    scored.append(kw)
            else:
                # New keyword, likely trending
                scored.append(kw)
        
        return scored[:10]
    
    def generate_title_keywords(self, beat_info: Dict[str, Any]) -> List[str]:
        """Generate recommended keywords for a specific beat's title."""
        genre = beat_info.get('genre', 'trap')
        mood = beat_info.get('mood', 'dark')
        bpm = beat_info.get('bpm', 140)
        
        keywords = []
        
        # Genre-specific opportunities
        opportunities = self.find_opportunities(genre, min_volume=300)
        keywords.extend([kw.keyword for kw in opportunities[:5]])
        
        # Trending
        trending = self.get_trending_keywords(genre)
        keywords.extend(trending[:3])
        
        # Mood-based
        mood_keywords = [
            f"{mood} {genre} beat",
            f"{mood} type beat",
        ]
        keywords.extend(mood_keywords)
        
        # BPM-based (for specific ranges)
        if bpm > 140:
            keywords.append("fast type beat")
        elif bpm < 90:
            keywords.append("slow type beat")
        
        # Deduplicate
        return list(dict.fromkeys(keywords))[:10]
