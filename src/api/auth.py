"""API authentication and rate limiting"""

import hashlib
import secrets
from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from ..database import APIKey
import logging

logger = logging.getLogger(__name__)


def hash_api_key(key: str) -> str:
    """Hash API key for storage"""
    return hashlib.sha256(key.encode()).hexdigest()


def generate_api_key() -> str:
    """Generate a new API key"""
    return f"sk_{secrets.token_urlsafe(32)}"


def verify_api_key(key: str, db: Session) -> APIKey:
    """Verify API key and return key object"""
    key_hash = hash_api_key(key)

    api_key = db.query(APIKey).filter(
        APIKey.key_hash == key_hash,
        APIKey.active == True
    ).first()

    if not api_key:
        logger.warning(f"Invalid API key attempt")
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Check if expired
    if api_key.expires_at and api_key.expires_at < datetime.utcnow():
        logger.warning(f"Expired API key: {api_key.id}")
        raise HTTPException(status_code=401, detail="API key expired")

    # Update last used
    api_key.last_used_at = datetime.utcnow()
    db.commit()

    return api_key


async def get_rate_limit(api_key: APIKey, db: Session):
    """Check rate limit for API key"""
    from sqlalchemy import func
    from ..database import Production

    # Count requests in last minute
    one_minute_ago = datetime.utcnow() - timedelta(minutes=1)

    recent_requests = db.query(Production).filter(
        Production.api_key_id == api_key.id,
        Production.created_at >= one_minute_ago
    ).count()

    if recent_requests >= api_key.rate_limit_per_minute:
        logger.warning(f"Rate limit exceeded for {api_key.id}")
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: {api_key.rate_limit_per_minute} requests per minute"
        )

    return True


def check_monthly_quota(api_key: APIKey, db: Session) -> bool:
    """Check if API key has reached monthly quota"""
    if api_key.monthly_used >= api_key.monthly_quota:
        logger.warning(f"Monthly quota exceeded for {api_key.id}")
        return False
    return True


def increment_usage(api_key: APIKey, db: Session):
    """Increment monthly usage for API key"""
    api_key.monthly_used += 1
    db.commit()


def reset_monthly_usage():
    """Reset monthly usage (called via Celery periodic task)"""
    from ..database.connection import SessionLocal
    db = SessionLocal()
    try:
        db.query(APIKey).update({"monthly_used": 0})
        db.commit()
        logger.info("Monthly usage reset for all API keys")
    finally:
        db.close()
