"""Celery application configuration"""

import os
from celery import Celery
from celery.schedules import crontab

# Get Redis URL from environment
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "documentary_studio",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour hard limit
    task_soft_time_limit=3300,  # 55 minutes soft limit
    result_expires=86400,  # 24 hours
)

# Periodic tasks
celery_app.conf.beat_schedule = {
    "retry-failed-webhooks": {
        "task": "src.queue.tasks.retry_failed_webhooks",
        "schedule": crontab(minute="*/5"),  # Every 5 minutes
    },
    "reset-monthly-usage": {
        "task": "src.queue.tasks.reset_monthly_usage",
        "schedule": crontab(hour=0, minute=0, day_of_month=1),  # 1st of month
    },
    "cleanup-old-data": {
        "task": "src.queue.tasks.cleanup_old_data",
        "schedule": crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    "generate-analytics-report": {
        "task": "src.queue.tasks.generate_analytics_report",
        "schedule": crontab(hour=6, minute=0),  # Daily at 6 AM
    },
}
