"""FastAPI server for Documentary Studio"""

import logging
import json
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from ..core.schemas import ProjectPlan
from ..database import get_db, Production, Execution, QualityGate, Cost, init_db, check_db_connection
from ..producer import Producer
from ..dashboard import ProducerDashboard
from .auth import verify_api_key, get_rate_limit
from .schemas import ProductionRequest, ProductionResponse, StatusResponse, HealthResponse

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Documentary Studio API",
    description="AI-powered documentary generation platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """Initialize database on startup"""
    logger.info("Starting Documentary Studio API v1.0")
    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    logger.info("Shutting down Documentary Studio API")


@app.get("/api/v1/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    db_ok = check_db_connection()
    return HealthResponse(
        status="healthy" if db_ok else "degraded",
        timestamp=datetime.utcnow(),
        database="connected" if db_ok else "disconnected"
    )


@app.get("/api/v1/ready")
async def ready_check():
    """Readiness probe for Kubernetes"""
    db_ok = check_db_connection()
    if not db_ok:
        raise HTTPException(status_code=503, detail="Database not ready")
    return {"status": "ready"}


@app.post("/api/v1/productions", response_model=ProductionResponse)
async def create_production(
    request: ProductionRequest,
    db: Session = Depends(get_db),
    x_api_key: str = Header(...),
):
    """Submit documentary production job"""
    # Verify API key and apply rate limiting
    api_key = verify_api_key(x_api_key, db)
    await get_rate_limit(api_key, db)

    # Create production record
    production = Production(
        project_name=request.project_name,
        topic=request.topic,
        estimated_length_seconds=request.estimated_length_seconds,
        estimated_budget=request.estimated_budget,
        api_key_id=api_key.id,
        status="QUEUED"
    )

    db.add(production)
    db.commit()
    db.refresh(production)

    logger.info(f"Production created: {production.id} ({production.project_name})")

    # Queue execution (Phase 2 job queue integration)
    # from src.queue.tasks import run_production_task
    # run_production_task.delay(production.id)

    return ProductionResponse(
        id=production.id,
        project_name=production.project_name,
        status=production.status,
        created_at=production.created_at,
        progress=0.0
    )


@app.get("/api/v1/productions/{production_id}", response_model=StatusResponse)
async def get_production_status(
    production_id: str,
    db: Session = Depends(get_db),
    x_api_key: str = Header(...),
):
    """Get production status"""
    verify_api_key(x_api_key, db)

    production = db.query(Production).filter(Production.id == production_id).first()
    if not production:
        raise HTTPException(status_code=404, detail="Production not found")

    # Get execution history
    executions = db.query(Execution).filter(
        Execution.production_id == production_id
    ).all()

    # Get quality gates
    gates = db.query(QualityGate).filter(
        QualityGate.production_id == production_id
    ).all()

    gates_passed = sum(1 for g in gates if g.passed)

    return StatusResponse(
        id=production.id,
        status=production.status,
        progress=production.progress_percent,
        gates_passed=gates_passed,
        gates_total=len(gates),
        agents_executed=len(executions),
        cost=production.actual_cost,
        video_url=production.video_url,
        created_at=production.created_at,
        started_at=production.started_at,
        completed_at=production.completed_at
    )


@app.get("/api/v1/productions/{production_id}/dashboard")
async def get_production_dashboard(
    production_id: str,
    db: Session = Depends(get_db),
    x_api_key: str = Header(...),
):
    """Get live dashboard HTML"""
    verify_api_key(x_api_key, db)

    production = db.query(Production).filter(Production.id == production_id).first()
    if not production:
        raise HTTPException(status_code=404, detail="Production not found")

    # Generate dashboard (would integrate with ProducerDashboard)
    return {
        "status": "success",
        "dashboard_html": "<html><!-- Dashboard content --></html>"
    }


@app.get("/api/v1/productions/{production_id}/download")
async def download_production(
    production_id: str,
    db: Session = Depends(get_db),
    x_api_key: str = Header(...),
):
    """Download production video"""
    verify_api_key(x_api_key, db)

    production = db.query(Production).filter(Production.id == production_id).first()
    if not production:
        raise HTTPException(status_code=404, detail="Production not found")

    if not production.video_url:
        raise HTTPException(status_code=400, detail="Video not ready yet")

    return {
        "video_url": production.video_url,
        "duration_seconds": production.estimated_length_seconds,
        "created_at": production.completed_at
    }


@app.get("/api/v1/productions", response_model=dict)
async def list_productions(
    db: Session = Depends(get_db),
    x_api_key: str = Header(...),
    skip: int = 0,
    limit: int = 20,
):
    """List all productions for API key"""
    api_key = verify_api_key(x_api_key, db)

    productions = db.query(Production).filter(
        Production.api_key_id == api_key.id
    ).offset(skip).limit(limit).all()

    total = db.query(Production).filter(
        Production.api_key_id == api_key.id
    ).count()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "productions": [
            {
                "id": p.id,
                "project_name": p.project_name,
                "status": p.status,
                "progress": p.progress_percent,
                "created_at": p.created_at
            }
            for p in productions
        ]
    }


@app.get("/api/v1/metrics")
async def get_metrics(
    db: Session = Depends(get_db),
    x_api_key: str = Header(...),
):
    """Get usage metrics for API key"""
    api_key = verify_api_key(x_api_key, db)

    productions = db.query(Production).filter(
        Production.api_key_id == api_key.id
    ).all()

    costs = db.query(Cost).join(Production).filter(
        Production.api_key_id == api_key.id
    ).all()

    total_cost = sum(c.amount for c in costs)
    success_count = sum(1 for p in productions if p.status == "EXPORT")

    return {
        "api_key": api_key.name,
        "total_productions": len(productions),
        "successful_productions": success_count,
        "total_cost": total_cost,
        "monthly_used": api_key.monthly_used,
        "monthly_quota": api_key.monthly_quota,
        "rate_limit": api_key.rate_limit_per_minute
    }


@app.post("/api/v1/webhooks")
async def create_webhook(
    webhook_data: dict,
    db: Session = Depends(get_db),
    x_api_key: str = Header(...),
):
    """Subscribe to webhooks"""
    from ..webhooks import WebhookManager
    from ..database import WebhookSubscription

    api_key = verify_api_key(x_api_key, db)

    webhook = WebhookSubscription(
        api_key_id=api_key.id,
        url=webhook_data["url"],
        events=webhook_data["events"],
        secret=WebhookManager.generate_secret()
    )

    db.add(webhook)
    db.commit()
    db.refresh(webhook)

    return {
        "id": webhook.id,
        "url": webhook.url,
        "events": webhook.events,
        "created_at": webhook.created_at
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
