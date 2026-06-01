"""Click-Through Rate (CTR) tracking system.

Monitors and analyzes CTR performance across all content,
tracking thumbnail effectiveness and title performance.
"""

import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import structlog

logger = structlog.get_logger()


@dataclass
class CTRRecord:
    """A single CTR measurement."""
    video_id: str
    impressions: int
    clicks: int
    ctr: float
    thumbnail_variant: str
    title_variant: str
    recorded_at: datetime


class CTRTracker:
    """Track and analyze CTR performance."""
    
    # Industry benchmarks
    BENCHMARKS = {
        'excellent': 0.08,  # 8%+
        'good': 0.05,       # 5-8%
        'average': 0.03,    # 3-5%
        'poor': 0.02,       # 2-3%
        'critical': 0.01    # <2%
    }
    
    def __init__(self, storage_path: str = "./output/ctr_data.json"):
        self.storage_path = storage_path
        self.records: List[CTRRecord] = []
        self.load()
    
    def load(self):
        """Load CTR data."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    for item in data:
                        self.records.append(CTRRecord(
                            video_id=item['video_id'],
                            impressions=item['impressions'],
                            clicks=item['clicks'],
                            ctr=item['ctr'],
                            thumbnail_variant=item.get('thumbnail_variant', 'A'),
                            title_variant=item.get('title_variant', 'A'),
                            recorded_at=datetime.fromisoformat(item['recorded_at'])
                        ))
            except Exception as e:
                logger.warning("ctr_data_load_failed", error=str(e))
    
    def save(self):
        """Save CTR data."""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        
        data = [
            {
                'video_id': r.video_id,
                'impressions': r.impressions,
                'clicks': r.clicks,
                'ctr': r.ctr,
                'thumbnail_variant': r.thumbnail_variant,
                'title_variant': r.title_variant,
                'recorded_at': r.recorded_at.isoformat()
            }
            for r in self.records
        ]
        
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def record_ctr(self, video_id: str, impressions: int, clicks: int,
                   thumbnail_variant: str = "A", 
                   title_variant: str = "A"):
        """Record a CTR measurement."""
        ctr = clicks / impressions if impressions > 0 else 0
        
        record = CTRRecord(
            video_id=video_id,
            impressions=impressions,
            clicks=clicks,
            ctr=ctr,
            thumbnail_variant=thumbnail_variant,
            title_variant=title_variant,
            recorded_at=datetime.now()
        )
        
        self.records.append(record)
        self.save()
        
        # Log performance
        self._log_performance(record)
    
    def _log_performance(self, record: CTRRecord):
        """Log CTR performance level."""
        ctr = record.ctr
        
        if ctr >= self.BENCHMARKS['excellent']:
            level = 'excellent'
        elif ctr >= self.BENCHMARKS['good']:
            level = 'good'
        elif ctr >= self.BENCHMARKS['average']:
            level = 'average'
        elif ctr >= self.BENCHMARKS['poor']:
            level = 'poor'
        else:
            level = 'critical'
        
        logger.info("ctr_recorded",
                   video_id=record.video_id,
                   ctr=round(ctr * 100, 2),
                   level=level,
                   thumbnail=record.thumbnail_variant)
    
    def get_video_ctr(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get latest CTR for a video."""
        video_records = [r for r in self.records if r.video_id == video_id]
        
        if not video_records:
            return None
        
        latest = max(video_records, key=lambda r: r.recorded_at)
        
        # Calculate trend
        if len(video_records) > 1:
            sorted_records = sorted(video_records, key=lambda r: r.recorded_at)
            first_ctr = sorted_records[0].ctr
            last_ctr = sorted_records[-1].ctr
            
            if first_ctr > 0:
                change = (last_ctr - first_ctr) / first_ctr
            else:
                change = 0
        else:
            change = 0
        
        return {
            'video_id': video_id,
            'current_ctr': round(latest.ctr * 100, 2),
            'impressions': latest.impressions,
            'clicks': latest.clicks,
            'thumbnail_variant': latest.thumbnail_variant,
            'title_variant': latest.title_variant,
            'ctr_change': round(change * 100, 2),
            'recorded_at': latest.recorded_at.isoformat()
        }
    
    def get_variant_performance(self, variant_type: str = "thumbnail") -> Dict[str, Any]:
        """Get performance by variant (A/B test analysis).
        
        Args:
            variant_type: 'thumbnail' or 'title'
        
        Returns:
            Performance comparison by variant
        """
        variant_field = 'thumbnail_variant' if variant_type == 'thumbnail' else 'title_variant'
        
        # Group by variant
        variants = {}
        for record in self.records:
            label = getattr(record, variant_field)
            
            if label not in variants:
                variants[label] = {'total_impressions': 0, 'total_clicks': 0, 'count': 0}
            
            variants[label]['total_impressions'] += record.impressions
            variants[label]['total_clicks'] += record.clicks
            variants[label]['count'] += 1
        
        # Calculate CTR per variant
        results = {}
        for label, data in variants.items():
            ctr = data['total_clicks'] / data['total_impressions'] if data['total_impressions'] > 0 else 0
            results[label] = {
                'variant': label,
                'total_impressions': data['total_impressions'],
                'total_clicks': data['total_clicks'],
                'ctr': round(ctr * 100, 2),
                'record_count': data['count']
            }
        
        return results
    
    def get_performance_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get overall CTR performance summary."""
        cutoff = datetime.now() - timedelta(days=days)
        recent = [r for r in self.records if r.recorded_at >= cutoff]
        
        if not recent:
            return {'period_days': days, 'records': 0}
        
        total_impressions = sum(r.impressions for r in recent)
        total_clicks = sum(r.clicks for r in recent)
        avg_ctr = total_clicks / total_impressions if total_impressions > 0 else 0
        
        # Distribution
        ctrs = [r.ctr for r in recent]
        
        excellent = sum(1 for c in ctrs if c >= self.BENCHMARKS['excellent'])
        good = sum(1 for c in ctrs if self.BENCHMARKS['good'] <= c < self.BENCHMARKS['excellent'])
        average = sum(1 for c in ctrs if self.BENCHMARKS['average'] <= c < self.BENCHMARKS['good'])
        poor = sum(1 for c in ctrs if self.BENCHMARKS['poor'] <= c < self.BENCHMARKS['average'])
        critical = sum(1 for c in ctrs if c < self.BENCHMARKS['poor'])
        
        return {
            'period_days': days,
            'total_records': len(recent),
            'total_impressions': total_impressions,
            'total_clicks': total_clicks,
            'average_ctr': round(avg_ctr * 100, 2),
            'best_ctr': round(max(ctrs) * 100, 2),
            'worst_ctr': round(min(ctrs) * 100, 2),
            'distribution': {
                'excellent': excellent,
                'good': good,
                'average': average,
                'poor': poor,
                'critical': critical
            },
            'thumbnail_variants': self.get_variant_performance('thumbnail'),
            'title_variants': self.get_variant_performance('title')
        }
    
    def get_recommendations(self) -> List[str]:
        """Get CTR improvement recommendations."""
        summary = self.get_performance_summary()
        recommendations = []
        
        avg_ctr = summary.get('average_ctr', 0)
        
        if avg_ctr < 3.0:
            recommendations.append("CTR is below average. Focus on thumbnail improvements.")
            recommendations.append("Try more contrasting colors in thumbnails.")
        
        if avg_ctr < 2.0:
            recommendations.append("CTR is critically low. Complete thumbnail overhaul recommended.")
            recommendations.append("Test completely different thumbnail styles.")
        
        # Check variant performance
        thumb_variants = summary.get('thumbnail_variants', {})
        if len(thumb_variants) > 1:
            best = max(thumb_variants.values(), key=lambda v: v['ctr'])
            worst = min(thumb_variants.values(), key=lambda v: v['ctr'])
            
            if best['ctr'] > worst['ctr'] * 1.2:
                recommendations.append(
                    f"Thumbnail variant {best['variant']} outperforms by "
                    f"{round((best['ctr'] - worst['ctr']) / worst['ctr'] * 100)}%. "
                    f"Make it the default."
                )
        
        if not recommendations:
            recommendations.append("CTR performance is good. Continue current strategy.")
        
        return recommendations
