"""Centralized Celery configuration."""

import os
from celery import Celery

# Celery configuration
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Create shared Celery app
celery_app = Celery('aimusic')

celery_app.conf.update(
    broker_url=CELERY_BROKER_URL,
    result_backend=CELERY_RESULT_BACKEND,
    
    # Serialization
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    
    # Timezone
    timezone='UTC',
    enable_utc=True,
    
    # Task settings
    task_track_started=True,
    task_time_limit=600,  # 10 minutes max per task
    task_soft_time_limit=300,  # 5 minutes soft limit
    
    # Result settings
    result_expires=3600,  # Results expire after 1 hour
    result_extended=True,
    
    # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
    
    # Retry settings
    task_default_retry_delay=30,
    task_max_retries=3,
    
    # Queue definitions
    task_routes={
        'tasks.generate_midi': {'queue': 'midi'},
        'tasks.assign_sounds': {'queue': 'sound'},
        'tasks.render_audio': {'queue': 'sound'},
        'tasks.render_vst_audio': {'queue': 'sound'},
        'tasks.apply_mixing': {'queue': 'mix'},
        'tasks.apply_mastering': {'queue': 'master'},
        'tasks.run_quality_control': {'queue': 'qc'},
        'tasks.export_beat': {'queue': 'export'},
        'tasks.upload_beat_to_shopify': {'queue': 'shopify'},
        'tasks.research_trends_task': {'queue': 'trends'},
        'tasks.mark_beat_failed': {'queue': 'midi'},
    },
    
    # Dead letter queue
    task_reject_on_worker_lost=True,
    task_acks_late=True,
)

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    'research-trends': {
        'task': 'tasks.research_trends_task',
        'schedule': 3600.0,  # Every hour
    },
}


def get_celery_app() -> Celery:
    """Get the shared Celery application instance."""
    return celery_app
