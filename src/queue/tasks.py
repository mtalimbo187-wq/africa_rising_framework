"""Celery tasks for background processing"""

from datetime import datetime, timedelta
import logging
from .celery_app import celery_app
from ..database.connection import SessionLocal
from ..database import Production, Execution
from ..webhooks import WebhookManager
from ..api.auth import reset_monthly_usage

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def run_production_task(self, production_id: str):
    """Execute documentary production in background"""
    from ..producer import Producer
    from ..core.schemas import ProjectPlan

    db = SessionLocal()
    try:
        # Get production record
        production = db.query(Production).filter(
            Production.id == production_id
        ).first()

        if not production:
            logger.error(f"Production not found: {production_id}")
            return {"error": "Production not found"}

        logger.info(f"Starting production: {production_id}")

        # Trigger webhook event
        await WebhookManager.trigger_event(
            "production.started",
            production_id,
            {"project_name": production.project_name},
            db
        )

        # Update status
        production.status = "RUNNING"
        production.started_at = datetime.utcnow()
        db.commit()

        # Create project plan from production record
        project = ProjectPlan(
            project_name=production.project_name,
            topic=production.topic,
            estimated_length_seconds=production.estimated_length_seconds,
            estimated_budget=production.estimated_budget,
            required_agents=[],  # Populated from defaults
            quality_thresholds={}  # Populated from defaults
        )

        # Execute production
        producer = Producer()
        # Register agents...
        result = producer.execute_production(project)

        # Update production record
        production.status = result.get("state", "EXPORT")
        production.progress_percent = 100.0
        production.actual_cost = result.get("total_cost", 0)
        production.video_url = result.get("video_url")
        production.completed_at = datetime.utcnow()
        db.commit()

        logger.info(f"Production completed: {production_id}")

        # Trigger completion webhook
        await WebhookManager.trigger_event(
            "production.completed",
            production_id,
            {
                "video_url": production.video_url,
                "cost": production.actual_cost,
                "duration": (production.completed_at - production.started_at).total_seconds()
            },
            db
        )

        return result

    except Exception as e:
        logger.error(f"Production error: {e}")

        # Trigger error webhook
        await WebhookManager.trigger_event(
            "production.error",
            production_id,
            {"error": str(e)},
            db
        )

        # Update production status
        production.status = "ERROR"
        db.commit()

        # Retry task
        raise self.retry(exc=e, countdown=60)

    finally:
        db.close()


@celery_app.task
def retry_failed_webhooks():
    """Retry failed webhook deliveries"""
    db = SessionLocal()
    try:
        logger.info("Retrying failed webhook deliveries")
        # Implemented in WebhookManager.retry_failed_deliveries
    finally:
        db.close()


@celery_app.task
def reset_monthly_usage_task():
    """Reset monthly usage for all API keys"""
    db = SessionLocal()
    try:
        logger.info("Resetting monthly usage")
        reset_monthly_usage()
    finally:
        db.close()


@celery_app.task
def cleanup_old_data():
    """Remove old execution records and logs"""
    db = SessionLocal()
    try:
        # Delete executions older than 90 days
        cutoff_date = datetime.utcnow() - timedelta(days=90)

        deleted = db.query(Execution).filter(
            Execution.executed_at < cutoff_date
        ).delete()

        db.commit()
        logger.info(f"Cleaned up {deleted} old execution records")

    finally:
        db.close()


@celery_app.task
def generate_analytics_report():
    """Generate daily analytics report"""
    db = SessionLocal()
    try:
        from sqlalchemy import func

        # Calculate daily metrics
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        total_productions = db.query(func.count(Production.id)).filter(
            Production.created_at >= today_start
        ).scalar()

        successful = db.query(func.count(Production.id)).filter(
            Production.created_at >= today_start,
            Production.status == "EXPORT"
        ).scalar()

        total_cost = db.query(func.sum(Production.actual_cost)).filter(
            Production.created_at >= today_start
        ).scalar() or 0

        logger.info(f"""
        Daily Analytics Report:
        - Productions: {total_productions}
        - Successful: {successful}
        - Success Rate: {successful/total_productions*100:.1f}%
        - Total Cost: ${total_cost:.2f}
        """)

    finally:
        db.close()


@celery_app.task
def publish_to_youtube(production_id: str, video_url: str):
    """Publish production to YouTube (Phase 3)"""
    from ..integrations import YouTubePublisher

    db = SessionLocal()
    try:
        production = db.query(Production).filter(
            Production.id == production_id
        ).first()

        if not production:
            return

        publisher = YouTubePublisher()
        result = publisher.upload_video(
            video_url=video_url,
            title=production.project_name,
            description=f"Generated by Documentary Studio\n\nTopic: {production.topic}",
            tags=["documentary", "ai-generated"]
        )

        logger.info(f"Published to YouTube: {result.get('video_id')}")

    finally:
        db.close()


@celery_app.task
def publish_to_tiktok(production_id: str, video_url: str):
    """Publish production to TikTok (Phase 3)"""
    from ..integrations import TikTokPublisher

    db = SessionLocal()
    try:
        production = db.query(Production).filter(
            Production.id == production_id
        ).first()

        if not production:
            return

        publisher = TikTokPublisher()
        result = publisher.upload_video(
            video_url=video_url,
            caption=production.project_name,
            hashtags=["documentary", "ai", "education"]
        )

        logger.info(f"Published to TikTok: {result.get('video_id')}")

    finally:
        db.close()
