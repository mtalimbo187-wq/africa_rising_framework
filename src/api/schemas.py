"""Pydantic schemas for API requests/responses"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class ProductionRequest(BaseModel):
    """Request to create production"""
    project_name: str = Field(..., min_length=1, max_length=255)
    topic: str = Field(..., min_length=10)
    estimated_length_seconds: int = Field(..., gt=0, le=3600)
    estimated_budget: float = Field(..., gt=0)

    class Config:
        schema_extra = {
            "example": {
                "project_name": "Africa Rising",
                "topic": "Documentary about industrial development",
                "estimated_length_seconds": 600,
                "estimated_budget": 500.00
            }
        }


class ProductionResponse(BaseModel):
    """Response from production creation"""
    id: str
    project_name: str
    status: str
    progress: float
    created_at: datetime

    class Config:
        from_attributes = True


class StatusResponse(BaseModel):
    """Production status response"""
    id: str
    status: str
    progress: float
    gates_passed: int
    gates_total: int
    agents_executed: int
    cost: float
    video_url: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class HealthResponse(BaseModel):
    """Health check response"""
    status: str  # healthy, degraded, unhealthy
    timestamp: datetime
    database: str  # connected, disconnected


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    code: str
    timestamp: datetime


class WebhookRequest(BaseModel):
    """Webhook subscription request"""
    url: str
    events: List[str]  # production.started, gate.passed, etc


class WebhookResponse(BaseModel):
    """Webhook subscription response"""
    id: str
    url: str
    events: List[str]
    created_at: datetime


class APIKeyRequest(BaseModel):
    """Create API key request"""
    name: str
    owner: str


class APIKeyResponse(BaseModel):
    """API key response"""
    id: str
    name: str
    owner: str
    key: str  # Only returned on creation
    rate_limit_per_minute: int
    monthly_quota: int
    created_at: datetime
