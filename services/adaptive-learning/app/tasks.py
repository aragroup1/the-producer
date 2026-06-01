"""Celery tasks for adaptive learning engine."""

import os
from typing import Dict, Any, List
from datetime import datetime, timedelta

from celery import Celery
import numpy as np
import structlog

logger = structlog.get_logger()

# Initialize Celery
celery_app = Celery('learning')
celery_app.conf.broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
celery_app.conf.result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')


class AdaptiveLearningEngine:
    """Learn from sales/engagement data to improve generation."""
    
    # Feedback weights
    FEEDBACK_WEIGHTS = {
        'sale': 100.0,
        'exclusive_sale': 500.0,
        'wishlist': 10.0,
        'full_play': 5.0,
        'partial_play': 2.0,
        'cart_add': 15.0,
        'skip': -3.0,
        'return': -10.0,
        'preview_play': 1.0
    }
    
    def __init__(self):
        self.model_version = "1.0.0"
    
    def calculate_beat_reward(self, beat_data: Dict[str, Any]) -> float:
        """Calculate composite reward for a beat."""
        reward = 0.0
        
        # Sales
        sales_count = beat_data.get('sales_count', 0)
        reward += sales_count * self.FEEDBACK_WEIGHTS['sale']
        
        # Wishlists
        wishlist_count = beat_data.get('wishlist_count', 0)
        reward += wishlist_count * self.FEEDBACK_WEIGHTS['wishlist']
        
        # Plays
        play_count = beat_data.get('play_count', 0)
        view_count = beat_data.get('view_count', 1)
        
        # Estimate full vs partial plays
        full_plays = int(play_count * 0.3)
        partial_plays = play_count - full_plays
        
        reward += full_plays * self.FEEDBACK_WEIGHTS['full_play']
        reward += partial_plays * self.FEEDBACK_WEIGHTS['partial_play']
        
        # Cart adds
        cart_adds = beat_data.get('cart_add_count', 0)
        reward += cart_adds * self.FEEDBACK_WEIGHTS['cart_add']
        
        # Normalize by views
        if view_count > 0:
            reward = reward / view_count
        
        return reward
    
    def extract_features(self, beat_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features from beat for learning."""
        composition = beat_data.get('composition_params', {})
        
        return {
            'bpm': beat_data.get('bpm', 140),
            'key': beat_data.get('key_signature', 'C'),
            'genre': beat_data.get('genre', 'trap'),
            'mood': beat_data.get('mood', 'dark'),
            'duration': beat_data.get('duration_seconds', 180),
            'quality_score': beat_data.get('quality_score', 0),
            'chord_complexity': len(composition.get('chord_progression', [])),
            'track_count': len(composition.get('tracks', {})),
        }
    
    def analyze_performance(self, beats_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance of generated beats."""
        if not beats_data:
            return {"error": "No beat data available"}
        
        # Calculate rewards
        rewards = []
        for beat in beats_data:
            reward = self.calculate_beat_reward(beat)
            rewards.append({
                'beat_id': beat.get('id'),
                'reward': reward,
                'features': self.extract_features(beat)
            })
        
        # Sort by reward
        rewards.sort(key=lambda x: x['reward'], reverse=True)
        
        # Analyze top performers
        top_performers = rewards[:min(20, len(rewards))]
        bottom_performers = rewards[-min(20, len(rewards)):]
        
        # Extract patterns from top performers
        top_features = [p['features'] for p in top_performers]
        bottom_features = [p['features'] for p in bottom_performers]
        
        # Calculate feature importance
        insights = self._extract_insights(top_features, bottom_features)
        
        return {
            'total_beats': len(beats_data),
            'avg_reward': np.mean([r['reward'] for r in rewards]),
            'top_performers': top_performers[:5],
            'bottom_performers': bottom_performers[:5],
            'insights': insights,
            'recommendations': self._generate_recommendations(insights)
        }
    
    def _extract_insights(self, top_features: List[Dict], 
                          bottom_features: List[Dict]) -> Dict[str, Any]:
        """Extract insights from comparing top vs bottom performers."""
        insights = {}
        
        # BPM analysis
        top_bpms = [f['bpm'] for f in top_features]
        bottom_bpms = [f['bpm'] for f in bottom_features]
        
        insights['bpm'] = {
            'top_avg': np.mean(top_bpms) if top_bpms else 0,
            'bottom_avg': np.mean(bottom_bpms) if bottom_bpms else 0,
            'optimal_range': [
                int(np.percentile(top_bpms, 25)) if top_bpms else 130,
                int(np.percentile(top_bpms, 75)) if top_bpms else 150
            ]
        }
        
        # Genre analysis
        top_genres = {}
        bottom_genres = {}
        
        for f in top_features:
            genre = f.get('genre', 'unknown')
            top_genres[genre] = top_genres.get(genre, 0) + 1
        
        for f in bottom_features:
            genre = f.get('genre', 'unknown')
            bottom_genres[genre] = bottom_genres.get(genre, 0) + 1
        
        insights['genres'] = {
            'top_performing': sorted(top_genres.items(), key=lambda x: x[1], reverse=True)[:3],
            'underperforming': sorted(bottom_genres.items(), key=lambda x: x[1], reverse=True)[:3]
        }
        
        # Key analysis
        top_keys = {}
        for f in top_features:
            key = f.get('key', 'unknown')
            top_keys[key] = top_keys.get(key, 0) + 1
        
        insights['keys'] = {
            'top_performing': sorted(top_keys.items(), key=lambda x: x[1], reverse=True)[:3]
        }
        
        return insights
    
    def _generate_recommendations(self, insights: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate production recommendations."""
        recommendations = []
        
        # BPM recommendation
        bpm_range = insights.get('bpm', {}).get('optimal_range', [130, 150])
        recommendations.append({
            'type': 'bpm',
            'recommendation': f"Focus on BPM range {bpm_range[0]}-{bpm_range[1]}",
            'confidence': 'medium'
        })
        
        # Genre recommendation
        top_genres = insights.get('genres', {}).get('top_performing', [])
        if top_genres:
            recommendations.append({
                'type': 'genre',
                'recommendation': f"Prioritize {top_genres[0][0]} beats",
                'confidence': 'high'
            })
        
        # Key recommendation
        top_keys = insights.get('keys', {}).get('top_performing', [])
        if top_keys:
            recommendations.append({
                'type': 'key',
                'recommendation': f"Use keys like {', '.join([k[0] for k in top_keys[:3]])}",
                'confidence': 'medium'
            })
        
        return recommendations
    
    def generate_improved_params(self, base_params: Dict[str, Any],
                                  insights: Dict[str, Any]) -> Dict[str, Any]:
        """Generate improved parameters based on insights."""
        improved = base_params.copy()
        
        # Adjust BPM if outside optimal range
        bpm_range = insights.get('bpm', {}).get('optimal_range')
        if bpm_range and improved.get('bpm'):
            if improved['bpm'] < bpm_range[0] or improved['bpm'] > bpm_range[1]:
                improved['bpm'] = int(np.random.uniform(bpm_range[0], bpm_range[1]))
        
        # Suggest genre
        top_genres = insights.get('genres', {}).get('top_performing', [])
        if top_genres and np.random.random() < 0.3:
            improved['genre'] = top_genres[0][0]
        
        return improved


# Initialize engine
learning_engine = AdaptiveLearningEngine()


@celery_app.task
def process_feedback(beat_id: str, feedback_type: str, 
                     metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """Process user feedback for a beat."""
    logger.info("feedback_received", beat_id=beat_id, type=feedback_type)
    
    weight = AdaptiveLearningEngine.FEEDBACK_WEIGHTS.get(feedback_type, 1.0)
    
    return {
        "beat_id": beat_id,
        "feedback_type": feedback_type,
        "weight": weight,
        "processed": True
    }


@celery_app.task
def analyze_performance_task(beats_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze performance of beats."""
    logger.info("performance_analysis_started", beats_count=len(beats_data))
    
    results = learning_engine.analyze_performance(beats_data)
    
    logger.info("performance_analysis_completed")
    
    return results


@celery_app.task
def generate_improved_params_task(base_params: Dict[str, Any],
                                   insights: Dict[str, Any]) -> Dict[str, Any]:
    """Generate improved generation parameters."""
    return learning_engine.generate_improved_params(base_params, insights)
