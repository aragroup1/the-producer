"""Performance prediction model.

Learns which combinations of title, thumbnail, genre, and timing
produce the best results. Uses simple statistical models that
don't require heavy ML dependencies.
"""

import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import defaultdict
import structlog

logger = structlog.get_logger()


class PerformanceModel:
    """Learn and predict content performance."""
    
    def __init__(self, storage_path: str = "./output/performance_model.json"):
        self.storage_path = storage_path
        self.data: List[Dict[str, Any]] = []
        self.load()
    
    def load(self):
        """Load training data."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    self.data = json.load(f)
            except Exception as e:
                logger.warning("performance_model_load_failed", error=str(e))
    
    def save(self):
        """Save training data."""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def record_performance(self, video_id: str, features: Dict[str, Any],
                         metrics: Dict[str, float]):
        """Record performance data for learning.
        
        Args:
            video_id: Video identifier
            features: Content features (genre, title_style, thumbnail_style, etc.)
            metrics: Performance metrics (ctr, views, watch_time, etc.)
        """
        record = {
            'video_id': video_id,
            'features': features,
            'metrics': metrics,
            'recorded_at': datetime.now().isoformat()
        }
        
        self.data.append(record)
        self.save()
        
        logger.info("performance_recorded",
                   video_id=video_id,
                   ctr=metrics.get('ctr'),
                   views=metrics.get('views'))
    
    def predict_performance(self, features: Dict[str, Any]) -> Dict[str, float]:
        """Predict performance for given features.
        
        Uses nearest-neighbor matching on feature similarity.
        """
        if not self.data:
            return {'confidence': 0, 'predicted_ctr': 0.035, 'predicted_views': 5000}
        
        # Find similar past performances
        similarities = []
        for record in self.data:
            sim = self._calculate_similarity(features, record['features'])
            similarities.append((sim, record['metrics']))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[0], reverse=True)
        
        # Take top 5 most similar
        top_similar = similarities[:5]
        
        if not top_similar or top_similar[0][0] < 0.3:
            return {'confidence': 0, 'predicted_ctr': 0.035, 'predicted_views': 5000}
        
        # Weighted average by similarity
        total_weight = sum(sim for sim, _ in top_similar)
        
        predicted_ctr = sum(
            m.get('ctr', 0) * sim 
            for sim, m in top_similar
        ) / total_weight
        
        predicted_views = sum(
            m.get('views', 0) * sim
            for sim, m in top_similar
        ) / total_weight
        
        avg_similarity = sum(sim for sim, _ in top_similar) / len(top_similar)
        
        return {
            'confidence': round(avg_similarity, 3),
            'predicted_ctr': round(predicted_ctr, 4),
            'predicted_views': int(predicted_views),
            'similar_samples': len(top_similar)
        }
    
    def _calculate_similarity(self, features1: Dict, 
                              features2: Dict) -> float:
        """Calculate similarity between two feature sets."""
        if not features1 or not features2:
            return 0.0
        
        matches = 0
        total = 0
        
        for key in set(features1.keys()) | set(features2.keys()):
            total += 1
            
            if key in features1 and key in features2:
                if features1[key] == features2[key]:
                    matches += 1
                elif isinstance(features1[key], (int, float)) and isinstance(features2[key], (int, float)):
                    # Numeric similarity
                    max_val = max(abs(features1[key]), abs(features2[key]), 1)
                    diff = abs(features1[key] - features2[key]) / max_val
                    matches += 1 - diff
        
        return matches / total if total > 0 else 0.0
    
    def get_best_practices(self, genre: str = None) -> Dict[str, Any]:
        """Extract best practices from performance data."""
        if not self.data:
            return {'message': 'No data available yet'}
        
        # Filter by genre if specified
        records = self.data
        if genre:
            records = [
                r for r in records
                if r['features'].get('genre') == genre
            ]
        
        if not records:
            return {'message': f'No data for genre: {genre}'}
        
        # Analyze by feature
        feature_performance = defaultdict(list)
        
        for record in records:
            for feature, value in record['features'].items():
                key = f"{feature}:{value}"
                feature_performance[key].append(record['metrics'])
        
        # Find best performing combinations
        best_features = {}
        for key, metrics_list in feature_performance.items():
            if len(metrics_list) >= 3:  # Need enough samples
                avg_ctr = sum(m.get('ctr', 0) for m in metrics_list) / len(metrics_list)
                best_features[key] = avg_ctr
        
        # Sort by performance
        sorted_features = sorted(best_features.items(), 
                                key=lambda x: x[1], 
                                reverse=True)
        
        return {
            'genre': genre,
            'total_samples': len(records),
            'top_performing_features': [
                {'feature': k, 'avg_ctr': round(v * 100, 2)}
                for k, v in sorted_features[:10]
            ],
            'overall_avg_ctr': round(
                sum(r['metrics'].get('ctr', 0) for r in records) / len(records) * 100, 
                2
            ) if records else 0
        }
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Calculate feature importance based on variance in performance."""
        if len(self.data) < 10:
            return {}
        
        # For each feature, calculate how much it affects CTR
        feature_impact = {}
        
        all_features = set()
        for record in self.data:
            all_features.update(record['features'].keys())
        
        for feature in all_features:
            # Group by feature value
            groups = defaultdict(list)
            for record in self.data:
                value = record['features'].get(feature, 'unknown')
                groups[value].append(record['metrics'].get('ctr', 0))
            
            # Calculate variance between groups
            group_means = [sum(g) / len(g) for g in groups.values() if g]
            
            if len(group_means) > 1:
                overall_mean = sum(group_means) / len(group_means)
                variance = sum((m - overall_mean) ** 2 for m in group_means) / len(group_means)
                feature_impact[feature] = variance
        
        # Normalize
        max_impact = max(feature_impact.values()) if feature_impact else 1
        
        return {
            k: round(v / max_impact, 3)
            for k, v in sorted(feature_impact.items(), key=lambda x: x[1], reverse=True)
        }
