"""Thumbnail performance optimizer.

Learns which thumbnail styles, colors, and text configurations
produce the highest CTR.
"""

import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import defaultdict
import structlog

logger = structlog.get_logger()


class ThumbnailOptimizer:
    """Optimize thumbnail performance through learning."""
    
    def __init__(self, storage_path: str = "./output/thumbnail_learning.json"):
        self.storage_path = storage_path
        self.records: List[Dict[str, Any]] = []
        self.load()
    
    def load(self):
        """Load thumbnail performance data."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    self.records = json.load(f)
            except Exception as e:
                logger.warning("thumbnail_learning_load_failed", error=str(e))
    
    def save(self):
        """Save thumbnail performance data."""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, 'w') as f:
            json.dump(self.records, f, indent=2)
    
    def record_thumbnail_performance(self, video_id: str,
                                     thumbnail_features: Dict[str, Any],
                                     ctr: float, views: int):
        """Record performance of a thumbnail.
        
        Args:
            video_id: Video ID
            thumbnail_features: Dict with colors, text_effect, layout, etc.
            ctr: Click-through rate
            views: Total views
        """
        record = {
            'video_id': video_id,
            'features': thumbnail_features,
            'ctr': ctr,
            'views': views,
            'recorded_at': datetime.now().isoformat()
        }
        
        self.records.append(record)
        self.save()
        
        logger.info("thumbnail_performance_recorded",
                   video_id=video_id,
                   ctr=round(ctr * 100, 2))
    
    def get_best_colors(self, genre: str = None) -> List[Dict[str, Any]]:
        """Get best performing color combinations."""
        records = self.records
        
        if genre:
            records = [r for r in records if r['features'].get('genre') == genre]
        
        if not records:
            return []
        
        # Group by primary color
        color_performance = defaultdict(list)
        
        for record in records:
            primary = record['features'].get('primary_color', 'unknown')
            accent = record['features'].get('accent_color', 'unknown')
            key = f"{primary}+{accent}"
            color_performance[key].append(record['ctr'])
        
        # Calculate averages
        results = []
        for color_combo, ctrs in color_performance.items():
            if len(ctrs) >= 2:
                avg_ctr = sum(ctrs) / len(ctrs)
                results.append({
                    'color_combo': color_combo,
                    'avg_ctr': round(avg_ctr * 100, 2),
                    'sample_size': len(ctrs)
                })
        
        results.sort(key=lambda x: x['avg_ctr'], reverse=True)
        return results[:10]
    
    def get_best_text_effects(self) -> List[Dict[str, Any]]:
        """Get best performing text effects."""
        effect_performance = defaultdict(list)
        
        for record in self.records:
            effect = record['features'].get('text_effect', 'none')
            effect_performance[effect].append(record['ctr'])
        
        results = []
        for effect, ctrs in effect_performance.items():
            if len(ctrs) >= 2:
                avg_ctr = sum(ctrs) / len(ctrs)
                results.append({
                    'text_effect': effect,
                    'avg_ctr': round(avg_ctr * 100, 2),
                    'sample_size': len(ctrs)
                })
        
        results.sort(key=lambda x: x['avg_ctr'], reverse=True)
        return results
    
    def get_best_layouts(self) -> List[Dict[str, Any]]:
        """Get best performing layouts."""
        layout_performance = defaultdict(list)
        
        for record in self.records:
            layout = record['features'].get('layout', 'center')
            layout_performance[layout].append(record['ctr'])
        
        results = []
        for layout, ctrs in layout_performance.items():
            if len(ctrs) >= 2:
                avg_ctr = sum(ctrs) / len(ctrs)
                results.append({
                    'layout': layout,
                    'avg_ctr': round(avg_ctr * 100, 2),
                    'sample_size': len(ctrs)
                })
        
        results.sort(key=lambda x: x['avg_ctr'], reverse=True)
        return results
    
    def get_recommendations(self, genre: str = None) -> Dict[str, Any]:
        """Get thumbnail optimization recommendations."""
        recommendations = {
            'genre': genre,
            'total_samples': len(self.records),
            'color_recommendations': self.get_best_colors(genre)[:3],
            'text_effect_recommendations': self.get_best_text_effects()[:3],
            'layout_recommendations': self.get_best_layouts()[:3],
        }
        
        # Build specific advice
        advice = []
        
        colors = recommendations['color_recommendations']
        if colors:
            advice.append(f"Best color combo: {colors[0]['color_combo']} "
                         f"(CTR: {colors[0]['avg_ctr']}%)")
        
        effects = recommendations['text_effect_recommendations']
        if effects:
            advice.append(f"Best text effect: {effects[0]['text_effect']} "
                         f"(CTR: {effects[0]['avg_ctr']}%)")
        
        layouts = recommendations['layout_recommendations']
        if layouts:
            advice.append(f"Best layout: {layouts[0]['layout']} "
                         f"(CTR: {layouts[0]['avg_ctr']}%)")
        
        recommendations['advice'] = advice
        
        return recommendations
    
    def predict_thumbnail_ctr(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Predict CTR for a thumbnail design."""
        if not self.records:
            return {'predicted_ctr': 3.5, 'confidence': 0}
        
        # Find similar thumbnails
        similar = []
        for record in self.records:
            sim = self._similarity(features, record['features'])
            if sim > 0.5:
                similar.append((sim, record['ctr']))
        
        if not similar:
            return {'predicted_ctr': 3.5, 'confidence': 0}
        
        # Weighted average
        total_weight = sum(sim for sim, _ in similar)
        predicted = sum(ctr * sim for sim, ctr in similar) / total_weight
        
        avg_sim = sum(sim for sim, _ in similar) / len(similar)
        
        return {
            'predicted_ctr': round(predicted * 100, 2),
            'confidence': round(avg_sim, 3),
            'similar_samples': len(similar)
        }
    
    def _similarity(self, f1: Dict, f2: Dict) -> float:
        """Calculate feature similarity."""
        matches = 0
        total = 0
        
        for key in set(f1.keys()) | set(f2.keys()):
            total += 1
            if f1.get(key) == f2.get(key):
                matches += 1
        
        return matches / total if total > 0 else 0
