"""Video retention analysis.

Analyzes watch time, audience retention curves, and drop-off points
to optimize video content and length.
"""

import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
import structlog

logger = structlog.get_logger()


@dataclass
class RetentionPoint:
    """Retention at a specific time point."""
    time_seconds: float
    percentage: float  # 0-100
    drop_rate: float   # Drop-off rate at this point


class RetentionAnalyzer:
    """Analyze video retention patterns."""
    
    def __init__(self, storage_path: str = "./output/retention_data.json"):
        self.storage_path = storage_path
        self.retention_curves: Dict[str, List[RetentionPoint]] = {}
        self.load()
    
    def load(self):
        """Load retention data."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    for video_id, points in data.items():
                        self.retention_curves[video_id] = [
                            RetentionPoint(
                                time_seconds=p['time_seconds'],
                                percentage=p['percentage'],
                                drop_rate=p.get('drop_rate', 0)
                            )
                            for p in points
                        ]
            except Exception as e:
                logger.warning("retention_data_load_failed", error=str(e))
    
    def save(self):
        """Save retention data."""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        
        data = {}
        for video_id, points in self.retention_curves.items():
            data[video_id] = [
                {
                    'time_seconds': p.time_seconds,
                    'percentage': p.percentage,
                    'drop_rate': p.drop_rate
                }
                for p in points
            ]
        
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def record_retention(self, video_id: str, 
                         curve_data: List[Dict[str, float]]):
        """Record retention curve for a video.
        
        Args:
            video_id: Video identifier
            curve_data: List of {time_seconds, percentage} dicts
        """
        points = []
        
        for i, data in enumerate(curve_data):
            time_sec = data['time_seconds']
            percentage = data['percentage']
            
            # Calculate drop rate
            if i > 0:
                prev_pct = curve_data[i - 1]['percentage']
                time_diff = time_sec - curve_data[i - 1]['time_seconds']
                drop_rate = (prev_pct - percentage) / max(time_diff, 1)
            else:
                drop_rate = 0
            
            points.append(RetentionPoint(
                time_seconds=time_sec,
                percentage=percentage,
                drop_rate=drop_rate
            ))
        
        self.retention_curves[video_id] = points
        self.save()
        
        # Log analysis
        analysis = self.analyze_video(video_id)
        logger.info("retention_recorded",
                   video_id=video_id,
                   avg_retention=analysis.get('average_retention'))
    
    def analyze_video(self, video_id: str) -> Dict[str, Any]:
        """Analyze retention for a specific video."""
        points = self.retention_curves.get(video_id, [])
        
        if not points:
            return {'video_id': video_id, 'error': 'No data'}
        
        # Key metrics
        initial_retention = points[0].percentage if points else 100
        final_retention = points[-1].percentage if points else 0
        avg_retention = sum(p.percentage for p in points) / len(points)
        
        # Find drop-off points
        drop_points = [
            p for p in points
            if p.drop_rate > 5  # More than 5% per second drop
        ]
        
        # Find worst drop-off
        worst_drop = max(points, key=lambda p: p.drop_rate) if points else None
        
        # Retention at key milestones
        retention_30s = self._get_retention_at(points, 30)
        retention_60s = self._get_retention_at(points, 60)
        retention_half = self._get_retention_at(points, points[-1].time_seconds / 2)
        
        return {
            'video_id': video_id,
            'initial_retention': round(initial_retention, 1),
            'final_retention': round(final_retention, 1),
            'average_retention': round(avg_retention, 1),
            'retention_at_30s': round(retention_30s, 1),
            'retention_at_60s': round(retention_60s, 1),
            'retention_at_halfway': round(retention_half, 1),
            'drop_off_points': len(drop_points),
            'worst_drop': {
                'time': worst_drop.time_seconds if worst_drop else 0,
                'rate': round(worst_drop.drop_rate, 2) if worst_drop else 0
            } if worst_drop else None,
            'curve_length': len(points)
        }
    
    def _get_retention_at(self, points: List[RetentionPoint], 
                          target_time: float) -> float:
        """Get retention percentage at a specific time."""
        for p in points:
            if p.time_seconds >= target_time:
                return p.percentage
        
        return points[-1].percentage if points else 0
    
    def get_genre_retention_profile(self, genre: str) -> Dict[str, Any]:
        """Get average retention profile for a genre.
        
        This would require genre metadata per video.
        """
        # Placeholder - would aggregate by genre
        return {
            'genre': genre,
            'sample_size': 0,
            'average_retention': 0,
            'note': 'Requires genre metadata linkage'
        }
    
    def get_optimization_suggestions(self, video_id: str) -> List[str]:
        """Get suggestions to improve retention."""
        analysis = self.analyze_video(video_id)
        suggestions = []
        
        if analysis.get('retention_at_30s', 100) < 50:
            suggestions.append("Major drop-off in first 30s. Improve hook/opening.")
        
        if analysis.get('average_retention', 100) < 40:
            suggestions.append("Overall retention is low. Consider shorter videos.")
        
        worst_drop = analysis.get('worst_drop')
        if worst_drop and worst_drop['rate'] > 10:
            suggestions.append(
                f"Sharp drop at {worst_drop['time']}s. "
                f"Check what's happening at this timestamp."
            )
        
        if not suggestions:
            suggestions.append("Retention looks good. No major issues detected.")
        
        return suggestions
    
    def compare_videos(self, video_id_1: str, 
                       video_id_2: str) -> Dict[str, Any]:
        """Compare retention between two videos."""
        analysis_1 = self.analyze_video(video_id_1)
        analysis_2 = self.analyze_video(video_id_2)
        
        return {
            'video_1': analysis_1,
            'video_2': analysis_2,
            'winner': video_id_1 if analysis_1.get('average_retention', 0) > analysis_2.get('average_retention', 0) else video_id_2,
            'difference': round(
                abs(analysis_1.get('average_retention', 0) - analysis_2.get('average_retention', 0)), 
                1
            )
        }
