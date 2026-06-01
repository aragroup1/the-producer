"""Conversion tracking system.

Tracks the full funnel from video view → beat sale,
attributing revenue to specific content pieces.
"""

import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import structlog

logger = structlog.get_logger()


@dataclass
class ConversionEvent:
    """A single conversion event."""
    event_id: str
    video_id: str
    beat_id: str
    event_type: str  # view, click, add_to_cart, purchase
    revenue: float
    timestamp: datetime
    attribution_source: str  # direct, organic, referral
    user_fingerprint: str = ""  # Anonymous user ID


class ConversionTracker:
    """Track conversions from video views to beat sales."""
    
    def __init__(self, storage_path: str = "./output/conversions.json"):
        self.storage_path = storage_path
        self.events: List[ConversionEvent] = []
        self.load()
    
    def load(self):
        """Load conversion events."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    for item in data:
                        self.events.append(ConversionEvent(
                            event_id=item['event_id'],
                            video_id=item['video_id'],
                            beat_id=item['beat_id'],
                            event_type=item['event_type'],
                            revenue=item.get('revenue', 0),
                            timestamp=datetime.fromisoformat(item['timestamp']),
                            attribution_source=item.get('attribution_source', 'direct'),
                            user_fingerprint=item.get('user_fingerprint', '')
                        ))
            except Exception as e:
                logger.warning("conversion_data_load_failed", error=str(e))
    
    def save(self):
        """Save conversion events."""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        
        data = [
            {
                'event_id': e.event_id,
                'video_id': e.video_id,
                'beat_id': e.beat_id,
                'event_type': e.event_type,
                'revenue': e.revenue,
                'timestamp': e.timestamp.isoformat(),
                'attribution_source': e.attribution_source,
                'user_fingerprint': e.user_fingerprint
            }
            for e in self.events
        ]
        
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def record_event(self, video_id: str, beat_id: str,
                     event_type: str, revenue: float = 0,
                     attribution_source: str = "direct",
                     user_fingerprint: str = ""):
        """Record a conversion event."""
        event = ConversionEvent(
            event_id=f"{video_id}_{beat_id}_{datetime.now().timestamp()}",
            video_id=video_id,
            beat_id=beat_id,
            event_type=event_type,
            revenue=revenue,
            timestamp=datetime.now(),
            attribution_source=attribution_source,
            user_fingerprint=user_fingerprint
        )
        
        self.events.append(event)
        self.save()
        
        logger.info("conversion_event",
                   event_type=event_type,
                   video_id=video_id,
                   beat_id=beat_id,
                   revenue=revenue)
    
    def get_funnel(self, video_id: str = None, 
                   beat_id: str = None,
                   days: int = 30) -> Dict[str, Any]:
        """Get conversion funnel metrics.
        
        Args:
            video_id: Filter by video (optional)
            beat_id: Filter by beat (optional)
            days: Time period
        
        Returns:
            Funnel metrics
        """
        cutoff = datetime.now() - timedelta(days=days)
        
        events = [
            e for e in self.events
            if e.timestamp >= cutoff
            and (not video_id or e.video_id == video_id)
            and (not beat_id or e.beat_id == beat_id)
        ]
        
        # Count by event type
        views = len([e for e in events if e.event_type == 'view'])
        clicks = len([e for e in events if e.event_type == 'click'])
        carts = len([e for e in events if e.event_type == 'add_to_cart'])
        purchases = len([e for e in events if e.event_type == 'purchase'])
        
        # Revenue
        total_revenue = sum(e.revenue for e in events if e.event_type == 'purchase')
        
        # Conversion rates
        view_to_click = clicks / views if views > 0 else 0
        click_to_cart = carts / clicks if clicks > 0 else 0
        cart_to_purchase = purchases / carts if carts > 0 else 0
        view_to_purchase = purchases / views if views > 0 else 0
        
        return {
            'period_days': days,
            'video_id': video_id,
            'beat_id': beat_id,
            'funnel': {
                'views': views,
                'clicks': clicks,
                'add_to_carts': carts,
                'purchases': purchases
            },
            'conversion_rates': {
                'view_to_click': round(view_to_click * 100, 2),
                'click_to_cart': round(click_to_cart * 100, 2),
                'cart_to_purchase': round(cart_to_purchase * 100, 2),
                'view_to_purchase': round(view_to_purchase * 100, 2)
            },
            'revenue': {
                'total': round(total_revenue, 2),
                'per_purchase': round(total_revenue / purchases, 2) if purchases > 0 else 0,
                'per_view': round(total_revenue / views, 4) if views > 0 else 0
            }
        }
    
    def get_video_performance(self, video_id: str, 
                              days: int = 30) -> Dict[str, Any]:
        """Get performance metrics for a specific video."""
        funnel = self.get_funnel(video_id=video_id, days=days)
        
        # Get all beats promoted by this video
        video_events = [
            e for e in self.events
            if e.video_id == video_id
            and e.timestamp >= datetime.now() - timedelta(days=days)
        ]
        
        beat_revenue = {}
        for event in video_events:
            if event.event_type == 'purchase':
                beat_revenue[event.beat_id] = beat_revenue.get(event.beat_id, 0) + event.revenue
        
        return {
            'video_id': video_id,
            'funnel': funnel['funnel'],
            'conversion_rates': funnel['conversion_rates'],
            'revenue': funnel['revenue'],
            'beat_revenue': beat_revenue,
            'top_beats': sorted(
                [{'beat_id': k, 'revenue': v} for k, v in beat_revenue.items()],
                key=lambda x: x['revenue'],
                reverse=True
            )[:5]
        }
    
    def get_attribution_report(self, days: int = 30) -> Dict[str, Any]:
        """Get attribution breakdown by source."""
        cutoff = datetime.now() - timedelta(days=days)
        
        events = [e for e in self.events if e.timestamp >= cutoff]
        
        # Group by attribution source
        sources = {}
        for event in events:
            source = event.attribution_source
            
            if source not in sources:
                sources[source] = {'events': 0, 'revenue': 0}
            
            sources[source]['events'] += 1
            sources[source]['revenue'] += event.revenue
        
        return {
            'period_days': days,
            'attribution_sources': sources,
            'total_revenue': sum(s['revenue'] for s in sources.values()),
            'total_events': sum(s['events'] for s in sources.values())
        }
    
    def get_roi_by_content(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get ROI for each piece of content."""
        cutoff = datetime.now() - timedelta(days=days)
        
        # Group by video
        video_data = {}
        for event in self.events:
            if event.timestamp < cutoff:
                continue
            
            if event.video_id not in video_data:
                video_data[event.video_id] = {
                    'views': 0, 'clicks': 0, 'purchases': 0, 'revenue': 0
                }
            
            video_data[event.video_id][event.event_type + 's'] += 1
            video_data[event.video_id]['revenue'] += event.revenue
        
        # Calculate ROI
        results = []
        for video_id, data in video_data.items():
            roi = {
                'video_id': video_id,
                'views': data.get('views', 0),
                'clicks': data.get('clicks', 0),
                'purchases': data.get('purchases', 0),
                'revenue': round(data.get('revenue', 0), 2),
                'revenue_per_view': round(data.get('revenue', 0) / max(data.get('views', 1), 1), 4),
                'conversion_rate': round(data.get('purchases', 0) / max(data.get('views', 1), 1) * 100, 2)
            }
            results.append(roi)
        
        # Sort by revenue
        results.sort(key=lambda x: x['revenue'], reverse=True)
        
        return results
