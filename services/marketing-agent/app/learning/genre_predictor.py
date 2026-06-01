"""Genre trend predictor.

Predicts which genres will trend based on:
- Historical performance data
- Market signals
- Seasonal patterns
- Cross-platform trends
"""

import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict
import structlog

logger = structlog.get_logger()


class GenrePredictor:
    """Predict trending genres."""
    
    # Seasonal genre preferences
    SEASONAL_PATTERNS = {
        1: ['drill', 'trap', 'phonk'],        # January - dark winter
        2: ['drill', 'trap', 'rnb'],          # February
        3: ['trap', 'afrobeats', 'rnb'],      # March - spring
        4: ['afrobeats', 'dancehall', 'trap'], # April
        5: ['afrobeats', 'dancehall', 'reggaeton'], # May
        6: ['afrobeats', 'reggaeton', 'hyperpop'],   # June - summer
        7: ['afrobeats', 'dancehall', 'trap'],       # July
        8: ['trap', 'drill', 'phonk'],              # August
        9: ['trap', 'drill', 'rnb'],                # September
        10: ['drill', 'trap', 'phonk'],             # October - autumn
        11: ['drill', 'phonk', 'lofi'],             # November
        12: ['lofi', 'rnb', 'ambient'],             # December - winter/chill
    }
    
    def __init__(self, storage_path: str = "./output/genre_predictions.json"):
        self.storage_path = storage_path
        self.history: List[Dict[str, Any]] = []
        self.load()
    
    def load(self):
        """Load prediction history."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    self.history = json.load(f)
            except Exception as e:
                logger.warning("genre_prediction_load_failed", error=str(e))
    
    def save(self):
        """Save prediction history."""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def predict_trending_genres(self, days_ahead: int = 14) -> List[Dict[str, Any]]:
        """Predict which genres will trend in the coming weeks.
        
        Returns:
            List of genres with trend probability scores
        """
        predictions = []
        
        # Factor 1: Seasonal patterns
        future_date = datetime.now() + timedelta(days=days_ahead)
        seasonal_genres = self.SEASONAL_PATTERNS.get(future_date.month, [])
        
        # Factor 2: Historical momentum
        momentum = self._calculate_momentum()
        
        # Factor 3: Market signals (from trend research)
        market_signals = self._get_market_signals()
        
        # Combine factors
        all_genres = set(seasonal_genres) | set(momentum.keys()) | set(market_signals.keys())
        
        for genre in all_genres:
            seasonal_score = 0.3 if genre in seasonal_genres else 0
            momentum_score = momentum.get(genre, 0) * 0.4
            market_score = market_signals.get(genre, 0) * 0.3
            
            total_score = seasonal_score + momentum_score + market_score
            
            predictions.append({
                'genre': genre,
                'trend_probability': round(min(1.0, total_score), 3),
                'factors': {
                    'seasonal': round(seasonal_score, 3),
                    'momentum': round(momentum_score, 3),
                    'market': round(market_score, 3)
                },
                'predicted_for': future_date.isoformat()
            })
        
        # Sort by probability
        predictions.sort(key=lambda x: x['trend_probability'], reverse=True)
        
        # Record prediction
        self.history.append({
            'predicted_at': datetime.now().isoformat(),
            'days_ahead': days_ahead,
            'predictions': predictions[:10]
        })
        self.save()
        
        return predictions[:10]
    
    def _calculate_momentum(self) -> Dict[str, float]:
        """Calculate momentum score for each genre from historical data."""
        # This would use actual performance data
        # For now, return estimated momentum
        return {
            'drill': 0.85,
            'trap': 0.80,
            'afrobeats': 0.75,
            'phonk': 0.70,
            'rnb': 0.65,
            'lofi': 0.60,
            'rage': 0.55,
            'jersey_club': 0.50,
        }
    
    def _get_market_signals(self) -> Dict[str, float]:
        """Get market signals from trend research."""
        # This would integrate with trend detectors
        # For now, return estimated signals
        return {
            'afrobeats': 0.90,
            'drill': 0.85,
            'trap': 0.80,
            'phonk': 0.75,
            'rnb': 0.70,
            'lofi': 0.65,
        }
    
    def get_genre_recommendations(self, 
                                   current_inventory: Dict[str, int] = None) -> List[Dict[str, Any]]:
        """Get genre production recommendations.
        
        Args:
            current_inventory: Current beat count per genre
        
        Returns:
            Recommendations for what to produce
        """
        predictions = self.predict_trending_genres(days_ahead=7)
        
        recommendations = []
        
        for pred in predictions:
            genre = pred['genre']
            current_count = current_inventory.get(genre, 0) if current_inventory else 0
            
            # Recommend production based on gap
            if pred['trend_probability'] > 0.7 and current_count < 20:
                recommended_production = 20 - current_count
                priority = 'high'
            elif pred['trend_probability'] > 0.5 and current_count < 15:
                recommended_production = 15 - current_count
                priority = 'medium'
            else:
                recommended_production = 5
                priority = 'low'
            
            recommendations.append({
                'genre': genre,
                'trend_probability': pred['trend_probability'],
                'current_inventory': current_count,
                'recommended_production': recommended_production,
                'priority': priority,
                'reasoning': f"Trend probability {pred['trend_probability']:.0%}"
            })
        
        # Sort by priority and probability
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        recommendations.sort(key=lambda x: (priority_order[x['priority']], -x['trend_probability']))
        
        return recommendations
    
    def validate_predictions(self) -> Dict[str, Any]:
        """Check how past predictions performed."""
        if len(self.history) < 2:
            return {'message': 'Not enough history to validate'}
        
        # Compare predictions with actual outcomes
        # This would need actual performance data linked to predictions
        
        return {
            'total_predictions': len(self.history),
            'validation_status': 'pending_actual_data',
            'note': 'Link actual genre performance data to validate predictions'
        }
    
    def get_seasonal_calendar(self) -> Dict[str, List[str]]:
        """Get full seasonal genre calendar."""
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        calendar = {}
        for i, month in enumerate(months, 1):
            calendar[month] = self.SEASONAL_PATTERNS.get(i, [])
        
        return calendar
