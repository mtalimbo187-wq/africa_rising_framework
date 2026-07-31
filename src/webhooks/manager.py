"""Webhook event delivery system"""

import hashlib
import hmac
import secrets
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
import requests
import logging
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class WebhookManager:
    """Manages webhook subscriptions and delivery"""

    EVENTS = {
        "production.started": "Production started execution",
        "production.completed": "Production completed successfully",
        "production.error": "Production encountered an error",
        "gate.passed": "Quality gate passed",
        "gate.failed": "Quality gate failed",
        "agent.completed": "Agent execution completed",
        "agent.failed": "Agent execution failed",
    }

    MAX_RETRIES = 5
    RETRY_BACKOFF = [1, 2, 4, 8, 15]  # seconds between retries

    @staticmethod
    def generate_secret() -> str:
        """Generate webhook secret"""
        return secrets.token_hex(32)

    @staticmethod
    def sign_payload(payload: str, secret: str) -> str:
        """Sign webhook payload with HMAC"""
        return hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

    @staticmethod
    async def deliver_webhook(
        webhook_id: str,
        production_id: str,
        event_type: str,
        data: Dict[str, Any],
        url: str,
        secret: str,
        db: Session,
        attempt: int = 1
    ):
        """Deliver webhook to subscriber with retry logic"""
        from ..database import WebhookDelivery

        payload = json.dumps({
            "event": event_type,
            "production_id": production_id,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        })

        signature = WebhookManager.sign_payload(payload, secret)

        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Signature": f"sha256={signature}",
            "X-Webhook-Event": event_type,
            "User-Agent": "DocumentaryStudio/1.0"
        }

        try:
            response = requests.post(
                url,
                data=payload,
                headers=headers,
                timeout=10
            )

            # Record delivery
            delivery = WebhookDelivery(
                webhook_id=webhook_id,
                production_id=production_id,
                event_type=event_type,
                status_code=response.status_code,
                response_body=response.text[:500],
                attempt=attempt
            )

            if response.status_code in [200, 201, 202, 204]:
                delivery.delivered_at = datetime.utcnow()
                logger.info(f"Webhook delivered: {event_type} to {url}")
            else:
                # Schedule retry
                if attempt < WebhookManager.MAX_RETRIES:
                    retry_delay = WebhookManager.RETRY_BACKOFF[attempt - 1]
                    delivery.next_retry_at = datetime.utcnow() + timedelta(seconds=retry_delay)
                    logger.warning(f"Webhook delivery failed ({response.status_code}), retrying in {retry_delay}s")

            db.add(delivery)
            db.commit()

        except requests.exceptions.RequestException as e:
            logger.error(f"Webhook delivery error: {e}")

            # Schedule retry
            if attempt < WebhookManager.MAX_RETRIES:
                retry_delay = WebhookManager.RETRY_BACKOFF[attempt - 1]
                delivery = WebhookDelivery(
                    webhook_id=webhook_id,
                    production_id=production_id,
                    event_type=event_type,
                    attempt=attempt,
                    next_retry_at=datetime.utcnow() + timedelta(seconds=retry_delay)
                )
                db.add(delivery)
                db.commit()

    @staticmethod
    async def trigger_event(
        event_type: str,
        production_id: str,
        data: Dict[str, Any],
        db: Session
    ):
        """Trigger webhook event for all subscribers"""
        from ..database import WebhookSubscription

        if event_type not in WebhookManager.EVENTS:
            logger.warning(f"Unknown event type: {event_type}")
            return

        # Get all active webhooks subscribed to this event
        webhooks = db.query(WebhookSubscription).filter(
            WebhookSubscription.active == True
        ).all()

        subscribed_webhooks = [
            w for w in webhooks
            if event_type in w.events or "*" in w.events
        ]

        logger.info(f"Triggering event {event_type} to {len(subscribed_webhooks)} webhooks")

        # Deliver to all subscribed webhooks
        for webhook in subscribed_webhooks:
            await WebhookManager.deliver_webhook(
                webhook_id=webhook.id,
                production_id=production_id,
                event_type=event_type,
                data=data,
                url=webhook.url,
                secret=webhook.secret,
                db=db
            )

    @staticmethod
    async def retry_failed_deliveries(db: Session):
        """Retry failed webhook deliveries (Celery task)"""
        from ..database import WebhookDelivery, WebhookSubscription

        now = datetime.utcnow()

        # Get deliveries ready for retry
        failed_deliveries = db.query(WebhookDelivery).filter(
            WebhookDelivery.delivered_at == None,
            WebhookDelivery.next_retry_at <= now
        ).all()

        logger.info(f"Retrying {len(failed_deliveries)} failed webhook deliveries")

        for delivery in failed_deliveries:
            webhook = db.query(WebhookSubscription).filter(
                WebhookSubscription.id == delivery.webhook_id
            ).first()

            if webhook:
                await WebhookManager.deliver_webhook(
                    webhook_id=delivery.webhook_id,
                    production_id=delivery.production_id,
                    event_type=delivery.event_type,
                    data={},
                    url=webhook.url,
                    secret=webhook.secret,
                    db=db,
                    attempt=delivery.attempt + 1
                )

    @staticmethod
    def get_event_description(event_type: str) -> str:
        """Get human-readable event description"""
        return WebhookManager.EVENTS.get(event_type, "Unknown event")
