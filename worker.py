"""Celery worker entry point — imports all task modules from all services."""

import os
import sys

# Set up Python path to include all services
sys.path.insert(0, '/app')
sys.path.insert(0, '/app/services/api-gateway')
sys.path.insert(0, '/app/services/marketing-agent')
sys.path.insert(0, '/app/services/sound-engine')
sys.path.insert(0, '/app/services/composition-engine')
sys.path.insert(0, '/app/services/mixing-engine')
sys.path.insert(0, '/app/services/mastering-engine')
sys.path.insert(0, '/app/services/export-pipeline')
sys.path.insert(0, '/app/services/quality-scoring')
sys.path.insert(0, '/app/services/shopify-integration')
sys.path.insert(0, '/app/services/trend-research')
sys.path.insert(0, '/app/services/adaptive-learning')

# Import the Celery app first
from shared.celery_config import celery_app

# Import all task modules so Celery discovers them
# These imports register the tasks with the Celery app

# Import all task modules to register them with Celery
# Each service's tasks.py registers its tasks using @celery_app.task decorator

import importlib
import pkgutil

# List of service modules that may contain tasks
SERVICE_MODULES = [
    'services.composition_engine.app.tasks',
    'services.sound_engine.app.tasks',
    'services.mixing_engine.app.tasks',
    'services.mastering_engine.app.tasks',
    'services.quality_scoring.app.tasks',
    'services.export_pipeline.app.tasks',
    'services.shopify_integration.app.tasks',
    'services.trend_research.app.tasks',
    'services.adaptive_learning.app.tasks',
    'services.marketing_agent.app.tasks',
]

for module_name in SERVICE_MODULES:
    try:
        importlib.import_module(module_name)
        print(f"Loaded tasks from {module_name}")
    except Exception as e:
        print(f"Warning: Could not load {module_name}: {e}")

# This is what Celery uses
__all__ = ['celery_app']
