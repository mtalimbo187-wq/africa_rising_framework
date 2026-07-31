"""SQLAlchemy ORM models for Documentary Studio"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Float, DateTime, Integer, Text, Boolean, JSON, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum
import uuid

Base = declarative_base()


class Production(Base):
    """Documentary production project"""
    __tablename__ = "productions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_name = Column(String(255), nullable=False, index=True)
    topic = Column(Text, nullable=False)
    status = Column(String(50), default="INIT", index=True)
    progress_percent = Column(Float, default=0.0)

    # Metadata
    estimated_length_seconds = Column(Integer, nullable=False)
    estimated_budget = Column(Float, nullable=False)
    actual_cost = Column(Float, default=0.0)

    # Results
    video_url = Column(String(512), nullable=True)
    dashboard_url = Column(String(512), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relations
    api_key_id = Column(String(36), ForeignKey("api_keys.id"))
    executions = relationship("Execution", back_populates="production", cascade="all, delete-orphan")
    quality_gates = relationship("QualityGate", back_populates="production", cascade="all, delete-orphan")
    costs = relationship("Cost", back_populates="production", cascade="all, delete-orphan")
    webhook_deliveries = relationship("WebhookDelivery", back_populates="production", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Production {self.project_name} ({self.status})>"


class Execution(Base):
    """Agent execution record"""
    __tablename__ = "executions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    production_id = Column(String(36), ForeignKey("productions.id"), index=True)
    agent_name = Column(String(255), nullable=False, index=True)
    status = Column(String(50), nullable=False)  # PASS, FAIL, TIMEOUT, RETRY
    duration_ms = Column(Integer, nullable=False)

    # Data
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)

    # Retry info
    attempt = Column(Integer, default=1)
    max_attempts = Column(Integer, default=3)

    # Timestamp
    executed_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relation
    production = relationship("Production", back_populates="executions")

    def __repr__(self):
        return f"<Execution {self.agent_name} ({self.status})>"


class QualityGate(Base):
    """Quality gate evaluation result"""
    __tablename__ = "quality_gates"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    production_id = Column(String(36), ForeignKey("productions.id"), index=True)
    gate_name = Column(String(255), nullable=False, index=True)
    metric = Column(String(255), nullable=False)
    threshold = Column(Float, nullable=False)
    value = Column(Float, nullable=False)
    passed = Column(Boolean, nullable=False)

    # Details
    details = Column(JSON, nullable=True)
    evaluated_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relation
    production = relationship("Production", back_populates="quality_gates")

    def __repr__(self):
        return f"<QualityGate {self.gate_name} ({self.value}/{self.threshold})>"


class WebhookSubscription(Base):
    """Webhook subscription for events"""
    __tablename__ = "webhook_subscriptions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    api_key_id = Column(String(36), ForeignKey("api_keys.id"), index=True)
    url = Column(String(512), nullable=False)
    events = Column(JSON, nullable=False)  # List of event types
    active = Column(Boolean, default=True)
    secret = Column(String(64), nullable=False)  # HMAC secret

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<WebhookSubscription {self.url}>"


class WebhookDelivery(Base):
    """Webhook delivery attempt record"""
    __tablename__ = "webhook_deliveries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    production_id = Column(String(36), ForeignKey("productions.id"), index=True)
    webhook_id = Column(String(36), ForeignKey("webhook_subscriptions.id"), index=True)
    event_type = Column(String(255), nullable=False)

    # Delivery info
    status_code = Column(Integer, nullable=True)
    response_body = Column(Text, nullable=True)
    attempt = Column(Integer, default=1)
    max_attempts = Column(Integer, default=5)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    delivered_at = Column(DateTime, nullable=True)
    next_retry_at = Column(DateTime, nullable=True)

    # Relations
    production = relationship("Production", back_populates="webhook_deliveries")

    def __repr__(self):
        return f"<WebhookDelivery {self.event_type} ({self.status_code})>"


class APIKey(Base):
    """API key for authentication"""
    __tablename__ = "api_keys"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    key_hash = Column(String(255), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    owner = Column(String(255), nullable=False)

    # Limits
    rate_limit_per_minute = Column(Integer, default=60)
    monthly_quota = Column(Integer, default=1000)
    monthly_used = Column(Integer, default=0)

    # Status
    active = Column(Boolean, default=True)
    last_used_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<APIKey {self.name} ({self.owner})>"


class Cost(Base):
    """Cost tracking for API calls"""
    __tablename__ = "costs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    production_id = Column(String(36), ForeignKey("productions.id"), index=True)
    service = Column(String(255), nullable=False, index=True)  # runway, pexels, elevenlabs, etc
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")

    # Details
    description = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relation
    production = relationship("Production", back_populates="costs")

    def __repr__(self):
        return f"<Cost {self.service} ${self.amount}>"
