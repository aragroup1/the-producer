"""A/B testing framework for thumbnails.

Manages thumbnail variants, tracks performance, and automatically
selects winners based on CTR data.
"""

import os
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import structlog

logger = structlog.get_logger()


@dataclass
class ThumbnailVariant:
    """A single thumbnail variant in an A/B test."""
    variant_id: str
    label: str  # A, B, C
    thumbnail_path: str
    impressions: int = 0
    clicks: int = 0
    ctr: float = 0.0
    views: int = 0
    watch_time_seconds: float = 0.0


@dataclass
class ABTest:
    """An A/B test for thumbnails."""
    test_id: str
    beat_id: str
    video_content_id: str
    variants: List[ThumbnailVariant]
    status: str = "running"  # running, completed, cancelled
    winner: Optional[str] = None  # variant label
    confidence: float = 0.0
    started_at: datetime = None
    ended_at: Optional[datetime] = None
    min_samples: int = 1000  # Min impressions per variant
    min_confidence: float = 0.95  # 95% confidence


class ABTestManager:
    """Manage A/B tests for thumbnails."""
    
    def __init__(self, storage_path: str = "./output/ab_tests.json"):
        self.storage_path = storage_path
        self.tests: Dict[str, ABTest] = {}
        self.load()
    
    def load(self):
        """Load tests from storage."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    for test_data in data:
                        variants = [
                            ThumbnailVariant(**v)
                            for v in test_data.get('variants', [])
                        ]
                        test = ABTest(
                            test_id=test_data['test_id'],
                            beat_id=test_data['beat_id'],
                            video_content_id=test_data['video_content_id'],
                            variants=variants,
                            status=test_data.get('status', 'running'),
                            winner=test_data.get('winner'),
                            confidence=test_data.get('confidence', 0.0),
                            started_at=datetime.fromisoformat(test_data['started_at']) if test_data.get('started_at') else datetime.now(),
                            ended_at=datetime.fromisoformat(test_data['ended_at']) if test_data.get('ended_at') else None,
                            min_samples=test_data.get('min_samples', 1000),
                            min_confidence=test_data.get('min_confidence', 0.95)
                        )
                        self.tests[test.test_id] = test
            except Exception as e:
                logger.error("ab_test_load_failed", error=str(e))
    
    def save(self):
        """Save tests to storage."""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        data = []
        for test in self.tests.values():
            test_dict = asdict(test)
            test_dict['started_at'] = test.started_at.isoformat() if test.started_at else None
            test_dict['ended_at'] = test.ended_at.isoformat() if test.ended_at else None
            data.append(test_dict)
        
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def create_test(self, beat_id: str, video_content_id: str,
                    thumbnail_paths: List[str]) -> ABTest:
        """Create a new A/B test.
        
        Args:
            beat_id: Beat ID
            video_content_id: Video content ID
            thumbnail_paths: List of thumbnail file paths
        
        Returns:
            Created ABTest
        """
        labels = ['A', 'B', 'C'][:len(thumbnail_paths)]
        
        variants = [
            ThumbnailVariant(
                variant_id=str(uuid.uuid4()),
                label=label,
                thumbnail_path=path
            )
            for label, path in zip(labels, thumbnail_paths)
        ]
        
        test = ABTest(
            test_id=str(uuid.uuid4()),
            beat_id=beat_id,
            video_content_id=video_content_id,
            variants=variants,
            started_at=datetime.now()
        )
        
        self.tests[test.test_id] = test
        self.save()
        
        logger.info("ab_test_created",
                   test_id=test.test_id,
                   beat_id=beat_id,
                   variants=len(variants))
        
        return test
    
    def record_impression(self, test_id: str, variant_label: str):
        """Record an impression for a variant."""
        test = self.tests.get(test_id)
        if not test or test.status != "running":
            return
        
        for variant in test.variants:
            if variant.label == variant_label:
                variant.impressions += 1
                break
        
        self.save()
    
    def record_click(self, test_id: str, variant_label: str,
                     watch_time: float = 0.0):
        """Record a click/view for a variant."""
        test = self.tests.get(test_id)
        if not test or test.status != "running":
            return
        
        for variant in test.variants:
            if variant.label == variant_label:
                variant.clicks += 1
                variant.views += 1
                variant.watch_time_seconds += watch_time
                # Update CTR
                if variant.impressions > 0:
                    variant.ctr = variant.clicks / variant.impressions
                break
        
        self.save()
        
        # Check if test should be evaluated
        self._evaluate_test(test_id)
    
    def _evaluate_test(self, test_id: str):
        """Evaluate if a test has a winner."""
        test = self.tests.get(test_id)
        if not test or test.status != "running":
            return
        
        # Check minimum samples
        for variant in test.variants:
            if variant.impressions < test.min_samples:
                return  # Not enough data
        
        # Calculate statistical significance
        winner, confidence = self._calculate_winner(test)
        
        if winner and confidence >= test.min_confidence:
            test.winner = winner
            test.confidence = confidence
            test.status = "completed"
            test.ended_at = datetime.now()
            
            logger.info("ab_test_completed",
                       test_id=test_id,
                       winner=winner,
                       confidence=confidence)
            
            self.save()
    
    def _calculate_winner(self, test: ABTest) -> tuple:
        """Calculate winning variant using z-test for proportions.
        
        Returns:
            (winner_label, confidence)
        """
        if len(test.variants) < 2:
            return None, 0.0
        
        # Find best performing variant
        best = max(test.variants, key=lambda v: v.ctr)
        
        if best.impressions == 0:
            return None, 0.0
        
        # Compare against second best
        others = [v for v in test.variants if v.label != best.label]
        if not others:
            return best.label, 1.0
        
        second_best = max(others, key=lambda v: v.ctr)
        
        # Z-test for proportions
        p1 = best.ctr
        p2 = second_best.ctr
        n1 = best.impressions
        n2 = second_best.impressions
        
        if n1 == 0 or n2 == 0:
            return None, 0.0
        
        # Pooled proportion
        p_pool = (best.clicks + second_best.clicks) / (n1 + n2)
        
        # Standard error
        se = (p_pool * (1 - p_pool) * (1/n1 + 1/n2)) ** 0.5
        
        if se == 0:
            return best.label, 1.0
        
        # Z-score
        z = (p1 - p2) / se
        
        # Convert to confidence (two-tailed)
        import math
        confidence = self._z_to_confidence(abs(z))
        
        return best.label, confidence
    
    def _z_to_confidence(self, z: float) -> float:
        """Convert z-score to confidence level."""
        import math
        # Error function approximation
        a1 = 0.254829592
        a2 = -0.284496736
        a3 = 1.421413741
        a4 = -1.453152027
        a5 = 1.061405429
        p = 0.3275911
        
        sign = 1 if z >= 0 else -1
        z = abs(z) / (2 ** 0.5)
        
        t = 1.0 / (1.0 + p * z)
        y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-z * z)
        
        return sign * y
    
    def get_test_results(self, test_id: str) -> Optional[Dict[str, Any]]:
        """Get results for a specific test."""
        test = self.tests.get(test_id)
        if not test:
            return None
        
        return {
            'test_id': test.test_id,
            'beat_id': test.beat_id,
            'status': test.status,
            'winner': test.winner,
            'confidence': test.confidence,
            'started_at': test.started_at.isoformat() if test.started_at else None,
            'ended_at': test.ended_at.isoformat() if test.ended_at else None,
            'variants': [
                {
                    'label': v.label,
                    'impressions': v.impressions,
                    'clicks': v.clicks,
                    'ctr': round(v.ctr * 100, 2),
                    'views': v.views,
                    'avg_watch_time': round(v.watch_time_seconds / max(v.views, 1), 2)
                }
                for v in test.variants
            ]
        }
    
    def get_active_tests(self) -> List[ABTest]:
        """Get all running tests."""
        return [t for t in self.tests.values() if t.status == "running"]
    
    def get_winning_thumbnail(self, test_id: str) -> Optional[str]:
        """Get the winning thumbnail path for a test."""
        test = self.tests.get(test_id)
        if not test or not test.winner:
            return None
        
        for variant in test.variants:
            if variant.label == test.winner:
                return variant.thumbnail_path
        
        return None
    
    def cancel_test(self, test_id: str):
        """Cancel a running test."""
        test = self.tests.get(test_id)
        if test:
            test.status = "cancelled"
            test.ended_at = datetime.now()
            self.save()
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get summary of all A/B test performance."""
        completed = [t for t in self.tests.values() if t.status == "completed"]
        
        if not completed:
            return {
                'total_tests': len(self.tests),
                'completed_tests': 0,
                'average_improvement': 0,
                'top_performing_variant': None
            }
        
        # Calculate average CTR improvement
        improvements = []
        for test in completed:
            winner = next((v for v in test.variants if v.label == test.winner), None)
            if winner:
                others = [v for v in test.variants if v.label != test.winner]
                if others:
                    avg_other_ctr = sum(v.ctr for v in others) / len(others)
                    if avg_other_ctr > 0:
                        improvement = (winner.ctr - avg_other_ctr) / avg_other_ctr
                        improvements.append(improvement)
        
        avg_improvement = sum(improvements) / len(improvements) if improvements else 0
        
        # Find top variant across all tests
        all_variants = []
        for test in self.tests.values():
            for v in test.variants:
                all_variants.append({
                    'label': v.label,
                    'ctr': v.ctr,
                    'impressions': v.impressions
                })
        
        # Filter variants with enough data
        significant = [v for v in all_variants if v['impressions'] >= 500]
        top_variant = max(significant, key=lambda v: v['ctr']) if significant else None
        
        return {
            'total_tests': len(self.tests),
            'completed_tests': len(completed),
            'running_tests': len([t for t in self.tests.values() if t.status == "running"]),
            'average_ctr_improvement': round(avg_improvement * 100, 2),
            'top_performing_variant': top_variant['label'] if top_variant else None,
            'top_variant_ctr': round(top_variant['ctr'] * 100, 2) if top_variant else 0
        }
