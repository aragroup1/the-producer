"""Title performance optimizer.

Learns which title patterns, power words, and structures
produce the best click-through rates.
"""

import os
import json
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import defaultdict
import structlog

logger = structlog.get_logger()


class TitleOptimizer:
    """Optimize video titles for CTR."""
    
    def __init__(self, storage_path: str = "./output/title_learning.json"):
        self.storage_path = storage_path
        self.records: List[Dict[str, Any]] = []
        self.load()
    
    def load(self):
        """Load title performance data."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    self.records = json.load(f)
            except Exception as e:
                logger.warning("title_learning_load_failed", error=str(e))
    
    def save(self):
        """Save title performance data."""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, 'w') as f:
            json.dump(self.records, f, indent=2)
    
    def record_title_performance(self, video_id: str,
                                  title: str,
                                  features: Dict[str, Any],
                                  ctr: float, views: int):
        """Record performance of a title.
        
        Args:
            video_id: Video ID
            title: The title text
            features: Parsed features (power_words, length, has_year, etc.)
            ctr: Click-through rate
            views: Total views
        """
        record = {
            'video_id': video_id,
            'title': title,
            'features': features,
            'ctr': ctr,
            'views': views,
            'recorded_at': datetime.now().isoformat()
        }
        
        self.records.append(record)
        self.save()
        
        logger.info("title_performance_recorded",
                   video_id=video_id,
                   ctr=round(ctr * 100, 2),
                   title=title[:50])
    
    def analyze_power_words(self) -> List[Dict[str, Any]]:
        """Analyze which power words perform best."""
        word_performance = defaultdict(list)
        
        power_words = [
            'free', 'new', 'hot', 'hard', 'dark', 'emotional', 'melodic',
            'aggressive', 'crazy', 'insane', 'must hear', 'trending',
            'viral', '2026', 'latest', 'exclusive'
        ]
        
        for record in self.records:
            title_lower = record['title'].lower()
            
            for word in power_words:
                if word in title_lower:
                    word_performance[word].append(record['ctr'])
        
        results = []
        for word, ctrs in word_performance.items():
            if len(ctrs) >= 3:
                avg_ctr = sum(ctrs) / len(ctrs)
                results.append({
                    'word': word,
                    'avg_ctr': round(avg_ctr * 100, 2),
                    'sample_size': len(ctrs)
                })
        
        results.sort(key=lambda x: x['avg_ctr'], reverse=True)
        return results
    
    def analyze_length_performance(self) -> List[Dict[str, Any]]:
        """Analyze title length vs performance."""
        length_buckets = {
            'very_short': (0, 30),
            'short': (30, 50),
            'optimal': (50, 70),
            'long': (70, 100),
            'very_long': (100, 999)
        }
        
        bucket_performance = defaultdict(list)
        
        for record in self.records:
            length = len(record['title'])
            
            for bucket, (min_len, max_len) in length_buckets.items():
                if min_len <= length < max_len:
                    bucket_performance[bucket].append(record['ctr'])
                    break
        
        results = []
        for bucket, ctrs in bucket_performance.items():
            if len(ctrs) >= 2:
                avg_ctr = sum(ctrs) / len(ctrs)
                results.append({
                    'length_bucket': bucket,
                    'avg_ctr': round(avg_ctr * 100, 2),
                    'sample_size': len(ctrs),
                    'range': length_buckets[bucket]
                })
        
        results.sort(key=lambda x: x['avg_ctr'], reverse=True)
        return results
    
    def analyze_title_patterns(self) -> List[Dict[str, Any]]:
        """Analyze which title patterns perform best."""
        patterns = {
            'artist_x_artist': r'\w+\s+x\s+\w+',
            'year_included': r'20\d{2}',
            'bpm_included': r'\d+\s*BPM',
            'key_included': r'[A-G]#?\s*(major|minor)',
            'free_mentioned': r'free',
            'type_beat_first': r'^\w+\s+type beat',
            'pipe_separator': r'\|',
            'dash_separator': r'—',
        }
        
        pattern_performance = defaultdict(list)
        
        for record in self.records:
            for pattern_name, pattern in patterns.items():
                if re.search(pattern, record['title'], re.IGNORECASE):
                    pattern_performance[pattern_name].append(record['ctr'])
        
        results = []
        for pattern, ctrs in pattern_performance.items():
            if len(ctrs) >= 2:
                avg_ctr = sum(ctrs) / len(ctrs)
                results.append({
                    'pattern': pattern,
                    'avg_ctr': round(avg_ctr * 100, 2),
                    'sample_size': len(ctrs)
                })
        
        results.sort(key=lambda x: x['avg_ctr'], reverse=True)
        return results
    
    def get_recommendations(self) -> Dict[str, Any]:
        """Get title optimization recommendations."""
        return {
            'total_samples': len(self.records),
            'best_power_words': self.analyze_power_words()[:5],
            'optimal_length': self.analyze_length_performance(),
            'best_patterns': self.analyze_title_patterns()[:5],
        }
    
    def score_title(self, title: str) -> Dict[str, Any]:
        """Score a title based on learned patterns."""
        score = 0
        factors = []
        
        # Length check
        length = len(title)
        if 50 <= length <= 70:
            score += 20
            factors.append("optimal_length")
        elif length < 50:
            score += 10
            factors.append("short_length")
        elif length > 100:
            score -= 10
            factors.append("too_long")
        
        # Power words
        power_words_found = []
        power_word_scores = {w['word']: w['avg_ctr'] for w in self.analyze_power_words()}
        
        for word in power_word_scores.keys():
            if word.lower() in title.lower():
                power_words_found.append(word)
                score += 5
        
        if power_words_found:
            factors.append(f"power_words: {', '.join(power_words_found)}")
        
        # Year
        if re.search(r'20\d{2}', title):
            score += 10
            factors.append("year_included")
        
        # BPM
        if re.search(r'\d+\s*BPM', title, re.IGNORECASE):
            score += 5
            factors.append("bpm_included")
        
        # Artist names
        if re.search(r'\w+\s+x\s+\w+', title):
            score += 10
            factors.append("artist_comparison")
        
        # Separators
        if '|' in title or '—' in title:
            score += 5
            factors.append("clean_structure")
        
        return {
            'title': title,
            'score': score,
            'max_score': 100,
            'factors': factors,
            'recommendations': self._get_title_recommendations(title, score)
        }
    
    def _get_title_recommendations(self, title: str, score: int) -> List[str]:
        """Get specific recommendations for a title."""
        recs = []
        
        if len(title) < 40:
            recs.append("Title is quite short. Add more detail (BPM, key, mood).")
        
        if len(title) > 90:
            recs.append("Title may be truncated. Consider shortening.")
        
        if not re.search(r'20\d{2}', title):
            recs.append("Add current year for freshness.")
        
        if 'free' not in title.lower():
            recs.append("Consider adding 'FREE' for higher CTR.")
        
        if not re.search(r'\w+\s+x\s+\w+', title):
            recs.append("Artist comparisons (Artist x Artist) boost CTR.")
        
        if score < 50:
            recs.append("Title needs improvement. Review best practices.")
        
        if not recs:
            recs.append("Title looks good!")
        
        return recs
