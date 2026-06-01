"""AI-powered YouTube title generator.

Generates click-optimized titles using:
- Trending keyword insertion
- Power word psychology
- Character count optimization
- A/B test variant generation
"""

import random
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import structlog

logger = structlog.get_logger()


class TitleGenerator:
    """Generate optimized YouTube titles for beats."""
    
    # YouTube title limit
    MAX_TITLE_LENGTH = 100
    OPTIMAL_TITLE_LENGTH = 60
    
    # Power words that increase CTR
    POWER_WORDS = {
        "urgency": ["FREE", "NEW", "HOT", "TRENDING", "VIRAL", "2026", "LATEST"],
        "intensity": ["HARD", "DARK", "AGGRESSIVE", "HEAVY", "INTENSE", "CRAZY"],
        "emotion": ["EMOTIONAL", "SAD", "MELODIC", "BEAUTIFUL", "DEEP"],
        "quality": ["PROFESSIONAL", "STUDIO", "HIGH QUALITY", "PREMIUM"],
        "action": ["MUST HEAR", "LISTEN", "CHECK OUT", "DON'T MISS"]
    }
    
    # Artist name mappings for type beats
    ARTIST_MAP = {
        "trap": ["Travis Scott", "Future", "Young Thug", "Lil Baby", "Gunna", "Playboi Carti"],
        "drill": ["Central Cee", "Headie One", "Digga D", "Pop Smoke", "Fivio Foreign", "Russ Millions"],
        "boom_bap": ["Joey Bada$$", "Griselda", "Conway", "Benny", "Westside Gunn"],
        "rnb": ["Bryson Tiller", "Drake", "PartyNextDoor", "Brent Faiyaz", "Giveon"],
        "afrobeats": ["Burna Boy", "Wizkid", "Davido", "Tems", "Rema", "Omah Lay"],
        "lofi": ["J Dilla", "Nujabes", "Tomppabeats", "Idealism"],
        "phonk": ["DJ Smokey", "Soudiere", "Mythic"],
        "jersey_club": ["Cookiee Kawaii", "Uniiqu3", "DJ Tameil"],
        "rage": ["Yeat", "Ken Carson", "Destroy Lonely"],
        "hyperpop": ["100 gecs", "SOPHIE", "A.G. Cook"],
    }
    
    # Title templates with placeholders
    TEMPLATES = [
        "{power} {genre} Type Beat {year} | {artist} x {artist2} Style",
        "{genre} Type Beat — '{key} {scale}' | {power} {mood} Instrumental {year}",
        "{artist} x {artist2} {genre} Type Beat | {power} {year}",
        "{power} {mood} {genre} Beat {year} | {key} {scale} | Free Type Beat",
        "{genre} Type Beat {year} | {power} | {artist} Style Instrumental",
        "{mood} {genre} Beat — {bpm} BPM | {key} {scale} | {year}",
        "FREE {genre} Type Beat | {artist} x {artist2} Style | {year}",
        "{power} {genre} Instrumental {year} | {mood} Type Beat | {key} {scale}",
        "{genre} Beat {year} | {power} {mood} | {bpm} BPM {key} {scale}",
        "{artist} Type Beat — {genre} {year} | {power} {mood} Instrumental",
    ]
    
    # Templates optimized for Shorts
    SHORTS_TEMPLATES = [
        "{genre} Type Beat 🔥 {power} {year}",
        "{power} {genre} Beat {year} ⚡",
        "{artist} x {artist2} {genre} 🔥 {year}",
        "{mood} {genre} Type Beat {year} 💯",
        "FREE {genre} Beat {year} 🎹",
    ]
    
    def __init__(self):
        self.title_history = set()
    
    def generate_title(self, beat_info: Dict[str, Any],
                       trending_keywords: List[str] = None,
                       platform: str = "youtube") -> str:
        """Generate a single optimized title.
        
        Args:
            beat_info: Beat metadata
            trending_keywords: Optional trending keywords to include
            platform: youtube or shorts
        
        Returns:
            Optimized title string
        """
        genre = beat_info.get('genre', 'trap')
        bpm = beat_info.get('bpm', 140)
        key = beat_info.get('key', 'C')
        scale = beat_info.get('scale', 'minor')
        mood = beat_info.get('mood', 'dark')
        year = datetime.now().year
        
        # Select template
        if platform == "shorts":
            template = random.choice(self.SHORTS_TEMPLATES)
        else:
            template = random.choice(self.TEMPLATES)
        
        # Get artists for genre
        artists = self.ARTIST_MAP.get(genre, ["Artist"])
        artist = random.choice(artists)
        other_artists = [a for a in artists if a != artist]
        artist2 = random.choice(other_artists) if other_artists else artist
        
        # Select power word
        power_category = random.choice(list(self.POWER_WORDS.keys()))
        power = random.choice(self.POWER_WORDS[power_category])
        
        # Format template
        title = template.format(
            genre=genre.replace('_', ' ').title(),
            bpm=bpm,
            key=key,
            scale=scale.title(),
            mood=mood.title(),
            power=power,
            artist=artist,
            artist2=artist2,
            year=year
        )
        
        # Insert trending keyword if provided and fits
        if trending_keywords:
            title = self._insert_trending_keyword(title, trending_keywords)
        
        # Add emoji for Shorts before length optimization
        if platform == "shorts" and not any(e in title for e in ['🔥', '⚡', '💯', '🎹']):
            title += " 🔥"
        
        # Ensure length constraints
        title = self._optimize_length(title)
        
        logger.info("title_generated", title=title, length=len(title), platform=platform)
        
        return title
    
    def generate_variants(self, beat_info: Dict[str, Any],
                          count: int = 3,
                          trending_keywords: List[str] = None) -> List[str]:
        """Generate multiple title variants for A/B testing.
        
        Args:
            beat_info: Beat metadata
            count: Number of variants (2-5)
            trending_keywords: Optional trending keywords
        
        Returns:
            List of title strings
        """
        variants = []
        attempts = 0
        max_attempts = count * 10
        
        while len(variants) < count and attempts < max_attempts:
            title = self.generate_title(beat_info, trending_keywords)
            
            # Ensure uniqueness
            if title not in self.title_history and title not in variants:
                variants.append(title)
                self.title_history.add(title)
            
            attempts += 1
        
        return variants
    
    def _insert_trending_keyword(self, title: str, 
                                  keywords: List[str]) -> str:
        """Insert a trending keyword into the title if it fits."""
        for keyword in keywords:
            # Check if keyword is already in title
            if keyword.lower() in title.lower():
                continue
            
            # Try to insert after the first word or at the end
            words = title.split()
            
            if len(words) > 2:
                # Insert after first 2-3 words
                insert_pos = min(3, len(words) - 1)
                new_title = ' '.join(words[:insert_pos] + [keyword] + words[insert_pos:])
                
                if len(new_title) <= self.MAX_TITLE_LENGTH:
                    return new_title
            
            # Try appending
            appended = f"{title} | {keyword}"
            if len(appended) <= self.MAX_TITLE_LENGTH:
                return appended
        
        return title
    
    def _optimize_length(self, title: str) -> str:
        """Optimize title length for YouTube."""
        if len(title) <= self.OPTIMAL_TITLE_LENGTH:
            return title
        
        if len(title) <= self.MAX_TITLE_LENGTH:
            return title
        
        # Truncate intelligently
        # Try removing less important words
        words = title.split()
        
        # Remove words from the end until it fits
        while len(' '.join(words)) > self.MAX_TITLE_LENGTH and len(words) > 3:
            words.pop()
        
        return ' '.join(words)
    
    def score_title(self, title: str, beat_info: Dict[str, Any]) -> Dict[str, float]:
        """Score a title for optimization.
        
        Returns scores for various factors.
        """
        scores = {}
        genre = beat_info.get('genre', '')
        
        # Length score (optimal: 50-70 chars)
        length = len(title)
        if 50 <= length <= 70:
            scores['length'] = 1.0
        elif length < 50:
            scores['length'] = 0.7
        elif length <= 100:
            scores['length'] = 0.8
        else:
            scores['length'] = 0.3
        
        # Power word score
        power_words_found = sum(1 for words in self.POWER_WORDS.values() 
                               for word in words if word.lower() in title.lower())
        scores['power_words'] = min(1.0, power_words_found / 2)
        
        # Genre mention score
        scores['genre_mention'] = 1.0 if genre.replace('_', ' ').lower() in title.lower() else 0.0
        
        # Year score (recent year mentioned)
        current_year = datetime.now().year
        scores['freshness'] = 1.0 if str(current_year) in title else 0.5
        
        # Emoji score (for Shorts)
        emoji_count = len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', title))
        scores['emoji'] = min(1.0, emoji_count / 2)
        
        # Readability score (no excessive caps)
        caps_ratio = sum(1 for c in title if c.isupper()) / max(len(title), 1)
        scores['readability'] = 1.0 - abs(caps_ratio - 0.3)  # Optimal ~30% caps
        
        # Overall score
        scores['overall'] = sum(scores.values()) / len(scores)
        
        return {k: round(v, 3) for k, v in scores.items()}
    
    def get_search_suggestions(self, query: str) -> List[str]:
        """Get YouTube search suggestions for a query.
        
        Uses YouTube's autocomplete API.
        """
        import urllib.request
        import urllib.parse
        import json
        
        try:
            encoded_query = urllib.parse.quote(query)
            url = f"http://suggestqueries.google.com/complete/search?client=youtube&ds=yt&q={encoded_query}"
            
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
                suggestions = [item[0] for item in data[1]]
                return suggestions[:10]
        except Exception as e:
            logger.warning("search_suggestions_failed", error=str(e))
            return []
    
    def research_titles(self, genre: str, count: int = 20) -> List[Dict[str, Any]]:
        """Research top-performing titles in a genre.
        
        Returns list of title examples with estimated performance.
        """
        queries = [
            f"{genre} type beat",
            f"free {genre} beat",
            f"{genre} instrumental",
        ]
        
        all_suggestions = []
        for query in queries:
            suggestions = self.get_search_suggestions(query)
            all_suggestions.extend(suggestions)
        
        # Deduplicate and score
        unique = list(set(all_suggestions))
        results = []
        
        for suggestion in unique[:count]:
            # Estimate popularity by position in suggestions
            score = 1.0 - (unique.index(suggestion) / max(len(unique), 1)) * 0.5
            
            results.append({
                'title': suggestion,
                'estimated_popularity': round(score, 3),
                'genre': genre
            })
        
        return results
