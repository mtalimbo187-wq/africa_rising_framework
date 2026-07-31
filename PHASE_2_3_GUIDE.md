# Phase 2 & 3 Implementation Guide

## Overview

Complete implementation of Phase 2 (Production Infrastructure) and Phase 3 (Platform Integration) for Documentary Studio.

---

## Phase 2: Production Infrastructure

### 1. REST API (FastAPI)

**Endpoints:**
```bash
# Create production job
POST /api/v1/productions
Authorization: X-API-Key: sk_...
{
  "project_name": "My Documentary",
  "topic": "Topic description",
  "estimated_length_seconds": 600,
  "estimated_budget": 500.00
}

# Get production status
GET /api/v1/productions/{production_id}
Authorization: X-API-Key: sk_...

# Download video
GET /api/v1/productions/{production_id}/download

# List productions
GET /api/v1/productions?skip=0&limit=20

# Health check
GET /api/v1/health
```

### 2. Database Layer (PostgreSQL)

**Tables:**
- `productions` — Project records
- `executions` — Agent execution history
- `quality_gates` — Gate evaluation results
- `webhook_subscriptions` — Webhook endpoints
- `webhook_deliveries` — Delivery attempts and logs
- `api_keys` — API authentication
- `costs` — Cost tracking

**Initialize:**
```python
from src.database import init_db
init_db()  # Creates all tables
```

### 3. Webhook System

**Supported Events:**
- `production.started` — Production begins
- `production.completed` — Production finishes
- `production.error` — Production fails
- `gate.passed` — Quality gate passes
- `gate.failed` — Quality gate fails
- `agent.completed` — Agent execution completes
- `agent.failed` — Agent execution fails

**Subscribe:**
```bash
POST /api/v1/webhooks
{
  "url": "https://your-server.com/webhook",
  "events": ["production.completed", "gate.failed"]
}
```

**Webhook Payload:**
```json
{
  "event": "production.completed",
  "production_id": "uuid",
  "timestamp": "2026-07-31T12:00:00Z",
  "data": {
    "video_url": "...",
    "cost": 15.50,
    "duration": 120
  }
}
```

**Signature Verification:**
```python
import hmac
import hashlib

# Verify X-Webhook-Signature header
signature = hmac.new(
    secret.encode(),
    payload.encode(),
    hashlib.sha256
).hexdigest()

assert signature == header_signature
```

### 4. Job Queue (Celery + Redis)

**Async Tasks:**
```python
from src.queue import run_production_task, publish_to_youtube

# Queue production
run_production_task.delay(production_id)

# Queue YouTube publishing
publish_to_youtube.delay(production_id, video_url)
```

**Periodic Tasks:**
- Retry failed webhooks (every 5 minutes)
- Reset monthly usage (monthly)
- Cleanup old data (daily)
- Generate analytics (daily)

### 5. Advanced Retry Manager

**Circuit Breaker Pattern:**
```python
from src.core.advanced_retry import AdvancedRetryManager

retry_mgr = AdvancedRetryManager(agent_name="Asset Finder")
result = retry_mgr.execute_with_retry(api_call, arg1, arg2)
```

**Per-Agent Policies:**
- Research: 3 attempts, base=1, jitter=True
- Fact Checker: 3 attempts, base=2, jitter=True
- Visual: 2 attempts, base=1, jitter=True
- Production: 1 attempt (no retry)

### 6. Cost Optimizer

**Dynamic Cost Management:**
```python
from src.core.cost_optimizer import CostOptimizer

optimizer = CostOptimizer(budget=500.0)

# Check if we can afford an API call
if optimizer.can_afford("runway_ml", {"duration": 20}):
    result = runway.generate_video(...)
else:
    result = use_mock_video()
    
optimizer.log_cost("runway_ml", 15.50, "Video generation")

# Report
print(optimizer.get_budget_remaining())  # $484.50
print(optimizer.get_utilization())  # 3.1%
```

### 7. Docker Deployment

**Quick Start:**
```bash
# Copy environment
cp .env.example .env
# Edit .env with your API keys

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f api
```

**Services:**
- `api` — FastAPI server (port 8000)
- `worker` — Celery worker
- `beat` — Celery scheduler
- `postgres` — Database
- `redis` — Cache & message broker

---

## Phase 3: Platform Integration

### 1. Claude API Script Refinement

**Features:**
- Script quality enhancement
- Scene description generation
- Narration optimization
- Fact-checking enhancement

**Example:**
```python
from src.integrations import ClaudeScriptRefiner

refiner = ClaudeScriptRefiner()

# Refine script
result = refiner.refine_script(script, topic)
print(result["refined_script"])

# Generate visuals
visuals = refiner.generate_scene_descriptions(scene_text)

# Optimize narration
narration = refiner.optimize_narration(text, duration_seconds=60)
```

### 2. YouTube Auto-Publishing

**Features:**
- Auto-upload videos
- Set metadata and privacy
- Create playlists
- Schedule premieres
- Add subtitles
- Enable monetization

**Example:**
```python
from src.integrations import YouTubePublisher
from src.queue.tasks import publish_to_youtube

publisher = YouTubePublisher()

# Upload video
result = publisher.upload_video(
    video_url="s3://bucket/video.mp4",
    title="Amazing Documentary",
    description="...",
    tags=["documentary", "education"],
    privacy="public"
)

# In production, use Celery task
publish_to_youtube.delay(production_id, video_url)
```

### 3. TikTok Video Generation

**Features:**
- Extract short clips
- Auto-caption generation
- Add trending sounds
- Optimize hashtags
- Cross-post to Instagram Reels

**Example:**
```python
from src.integrations import TikTokGenerator

generator = TikTokGenerator()

# Extract clips
clips = generator.extract_clips(video_url, duration_seconds=15)

# Generate captions
captions = generator.generate_captions(text)

# Upload to TikTok
result = generator.upload_video(
    video_url=clip_url,
    caption="Check this out!",
    hashtags=["documentary", "ai", "trending"],
    schedule_time="2026-08-01T18:00:00Z"
)
```

### 4. A/B Testing Engine

**Optimize Gate Thresholds:**
```python
from src.analytics import ABTestEngine

ab_test = ABTestEngine()

# Create test
ab_test.create_test(
    gate_name="Fact Verification",
    baseline_threshold=0.95,
    variant_threshold=0.93
)

# Run productions with both thresholds
for production in productions:
    if random.random() > 0.5:
        threshold = 0.95  # baseline
    else:
        threshold = 0.93  # variant
    
    # Record result
    ab_test.record_trial(
        gate_name="Fact Verification",
        variant_name="baseline" if threshold == 0.95 else "variant",
        passed=production.gates_passed >= 5
    )

# Get results
results = ab_test.get_winner("Fact Verification")
print(f"Winner: {results['winner']}")
print(f"Improvement: {results['improvement']:.1f}%")
```

### 5. Analytics & Predictions

**Engagement Prediction:**
```python
from src.analytics import EngagementPredictor

predictor = EngagementPredictor()

result = predictor.predict_engagement(
    topic="African Industrial Development",
    script_quality=0.85,
    visual_complexity=0.75,
    narration_quality=0.90
)

print(f"Predicted engagement: {result['predicted_engagement_score']:.1f}%")
print(f"Predicted views: {result['predicted_views']:,}")
print(f"Completion rate: {result['predicted_completion_rate']:.1%}")
```

**Success Probability:**
```python
from src.analytics import SuccessProbabilityPredictor

predictor = SuccessProbabilityPredictor()

result = predictor.predict_gate_success(
    topic="Documentary",
    production_budget=500.0
)

print(f"Overall success: {result['overall_success_probability']:.1%}")
print(f"Fact verification: {result['gate_predictions']['fact_verification']['pass_probability']:.1%}")
```

---

## Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/db

# Redis
REDIS_URL=redis://localhost:6379/0

# API Keys
ANTHROPIC_API_KEY=sk-...
RUNWAY_API_KEY=...
PEXELS_API_KEY=...
TAVILY_API_KEY=...
ELEVENLABS_API_KEY=...
YOUTUBE_API_KEY=...

# API Settings
API_PORT=8000
RATE_LIMIT_PER_MINUTE=60
MONTHLY_QUOTA=1000
```

---

## Testing

**Run Tests:**
```bash
pytest src/tests/ -v

# With coverage
pytest src/tests/ --cov=src --cov-report=html

# Specific test
pytest src/tests/test_agents.py::test_research_agent -v
```

**Test Database:**
```bash
# Use SQLite for testing
export DATABASE_URL=sqlite:///test.db
```

---

## Monitoring

**Health Checks:**
```bash
# API health
curl http://localhost:8000/api/v1/health

# Readiness
curl http://localhost:8000/api/v1/ready
```

**Logs:**
```bash
# Docker logs
docker-compose logs -f api

# JSON logs
export LOG_FORMAT=json
```

---

## Deployment Checklist

- [ ] Database initialized and migrated
- [ ] API keys configured
- [ ] Webhooks tested with real endpoints
- [ ] Celery workers running
- [ ] Redis connectivity verified
- [ ] Tests passing (100% coverage)
- [ ] CI/CD pipeline active
- [ ] Monitoring alerts configured
- [ ] Backup strategy in place
- [ ] SSL certificates valid

---

## Support & Troubleshooting

**API Not Responding:**
```bash
# Check API health
curl http://localhost:8000/api/v1/health

# Check database
psql -U user -d documentary_studio -c "SELECT 1"

# Check Redis
redis-cli ping
```

**Queue Not Processing:**
```bash
# Check Celery worker
docker-compose logs worker

# Check Redis queue
redis-cli LLEN celery

# Restart worker
docker-compose restart worker
```

**Webhook Delivery Issues:**
```bash
# Check delivery attempts
SELECT * FROM webhook_deliveries WHERE status_code != 200

# Retry failed
src.webhooks.WebhookManager.retry_failed_deliveries()
```

---

**v1.0 Release:** All 20 Phase 2 & 3 components implemented and tested ✅
