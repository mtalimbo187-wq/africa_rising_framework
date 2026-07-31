# Deployment Guide

## Local Development Setup

### macOS

```bash
# 1. Install system dependencies
brew install python@3.9 ffmpeg redis postgresql

# 2. Clone repository
git clone https://github.com/africa-rising/framework.git
cd framework

# 3. Run setup script
bash deploy/setup.sh

# 4. Start services (optional)
redis-server &
postgres -D /usr/local/var/postgres &

# 5. Test installation
python3 -m pytest tests/
```

### Linux (Ubuntu/Debian)

```bash
# 1. Install system dependencies
sudo apt-get update
sudo apt-get install -y python3.9 python3-pip ffmpeg redis-server postgresql

# 2. Clone repository
git clone https://github.com/africa-rising/framework.git
cd framework

# 3. Run setup script
bash deploy/setup.sh

# 4. Start services
sudo systemctl start redis-server
sudo systemctl start postgresql

# 5. Test installation
python3 -m pytest tests/
```

### Windows

```powershell
# 1. Install Python 3.9 from python.org
# 2. Install FFmpeg from ffmpeg.org
# 3. Clone repository
git clone https://github.com/africa-rising/framework.git
cd framework

# 4. Run setup script
deploy\setup.bat

# 5. Test installation
python -m pytest tests\
```

## Docker Deployment

### Quick Start with Docker

```bash
# Build image
docker build -t africa-rising:latest .

# Run container
docker run -d \
  --name africa-rising \
  -p 5000:5000 \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/config.yaml:/app/config.yaml \
  -e ANTHROPIC_API_KEY="your_key" \
  africa-rising:latest

# View logs
docker logs -f africa-rising

# Stop container
docker stop africa-rising
```

### Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build
```

### Docker with GPU Support

```bash
# Enable NVIDIA GPU
docker run -d \
  --name africa-rising-gpu \
  --gpus all \
  -p 5000:5000 \
  -e ANTHROPIC_API_KEY="your_key" \
  africa-rising:latest

# Verify GPU access
docker exec africa-rising-gpu python3 << 'EOF'
import torch
print(f"GPU available: {torch.cuda.is_available()}")
print(f"GPU: {torch.cuda.get_device_name()}")
EOF
```

## Production Deployment

### AWS EC2

```bash
# 1. Launch EC2 instance
# Type: g4dn.xlarge (1x GPU)
# AMI: Ubuntu 20.04 LTS
# Storage: 100GB gp3

# 2. SSH into instance
ssh -i key.pem ubuntu@instance-ip

# 3. Install Docker
sudo apt-get update
sudo apt-get install -y docker.io

# 4. Pull and run container
docker pull africa-rising:latest
docker run -d \
  --name africa-rising \
  -p 5000:5000 \
  -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
  -v /mnt/output:/app/output \
  africa-rising:latest

# 5. Setup auto-restart
docker update --restart always africa-rising
```

### Google Cloud Run

```bash
# Build and push to Container Registry
docker build -t gcr.io/PROJECT_ID/africa-rising .
docker push gcr.io/PROJECT_ID/africa-rising

# Deploy to Cloud Run
gcloud run deploy africa-rising \
  --image gcr.io/PROJECT_ID/africa-rising \
  --platform managed \
  --region us-central1 \
  --memory 4Gi \
  --timeout 3600 \
  --set-env-vars ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY
```

### Kubernetes

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: africa-rising
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: pipeline
        image: africa-rising:latest
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
          limits:
            memory: "8Gi"
            cpu: "4"
        env:
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: anthropic

# Deploy
kubectl apply -f deployment.yaml
```

## Environment Configuration

### Production .env

```bash
# API Keys
export ANTHROPIC_API_KEY="sk-..."
export ELEVENLABS_API_KEY="..."
export PEXELS_API_KEY="..."
export TAVILY_API_KEY="..."
export GROK_API_KEY="..."
export GOOGLE_API_KEY="..."
export RUNWAY_API_KEY="..."

# Database
export DATABASE_URL="postgresql://user:pass@localhost/africa_rising"

# Monitoring
export SENTRY_DSN="https://..."
export LOG_LEVEL="INFO"

# Budget control
export BUDGET_LIMIT_USD="100.00"
export ALERT_THRESHOLD_PERCENT="80"
```

### Production config.yaml

```yaml
project:
  name: "Africa Rising - Production"
  environment: "production"
  
security:
  require_human_review: true
  verify_ssl: true
  require_https: true

api_calls:
  max_retries: 3
  timeout_seconds: 30
  rate_limit_per_minute: 60

monitoring:
  enable_telemetry: true
  alert_on_error: true
  log_level: "INFO"

cost_control:
  budget_limit_usd: 100.0
  alert_at_percent: 80
  stop_at_percent: 100

cache:
  enabled: true
  max_size_mb: 1000
  ttl_hours: 24
```

## Health Checks

### Application Health

```bash
# Check if service is running
curl http://localhost:5000/health

# Response:
# {"status": "healthy", "timestamp": "2026-07-30T12:00:00"}
```

### Database Health

```bash
# Test database connection
python3 << 'EOF'
import psycopg2
import os

conn = psycopg2.connect(os.environ["DATABASE_URL"])
cursor = conn.cursor()
cursor.execute("SELECT 1")
print("✓ Database connection OK")
EOF
```

### API Keys Validation

```bash
python3 << 'EOF'
from core.security import CredentialManager

keys = [
    "ANTHROPIC_API_KEY",
    "ELEVENLABS_API_KEY",
    "PEXELS_API_KEY",
    "TAVILY_API_KEY"
]

for key in keys:
    try:
        CredentialManager.load_from_env(key)
        print(f"✓ {key} configured")
    except KeyError:
        print(f"❌ {key} missing")
EOF
```

## Monitoring & Alerts

### Application Monitoring

```python
# Install monitoring
pip install prometheus-client

# Export metrics
from prometheus_client import Counter, Histogram

request_count = Counter('pipeline_requests_total', 'Total requests')
request_duration = Histogram('pipeline_request_duration_seconds', 'Request duration')

# Use in agents
request_count.inc()
with request_duration.time():
    agent.run()
```

### Log Aggregation

```bash
# Send logs to ELK stack / CloudWatch
# Edit docker-compose.yml to include logging driver

# AWS CloudWatch example:
docker run -d \
  --log-driver awslogs \
  --log-opt awslogs-group=/aws/ecs/africa-rising \
  --log-opt awslogs-region=us-east-1 \
  africa-rising:latest
```

### Cost Monitoring

```bash
# Generate cost report
python3 << 'EOF'
import json
from pathlib import Path

logs = Path("output/logs/costs.jsonl")
total = 0

with open(logs) as f:
    for line in f:
        entry = json.loads(line)
        total += entry["cost_usd"]

print(f"Total spent: ${total:.2f}")
print(f"Daily average: ${total/30:.2f}")
EOF
```

## Scaling

### Horizontal Scaling

```yaml
# docker-compose.yml with load balancer
version: '3.8'
services:
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf

  pipeline1:
    image: africa-rising:latest
    environment:
      - WORKER_ID=1

  pipeline2:
    image: africa-rising:latest
    environment:
      - WORKER_ID=2

  pipeline3:
    image: africa-rising:latest
    environment:
      - WORKER_ID=3
```

### Job Queue

```python
# Use Redis for job queue
from celery import Celery
import os

app = Celery(
    'africa_rising',
    broker=os.environ.get('REDIS_URL', 'redis://localhost:6379')
)

@app.task
def process_video(script, project_name):
    from agents.producer_agent import ProducerAgent
    producer = ProducerAgent(project_name)
    return producer.execute({"script": script})

# Queue a job
process_video.delay(script, "my_doc")
```

## Backup & Recovery

### Database Backup

```bash
# Backup PostgreSQL
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Restore
psql $DATABASE_URL < backup_20260730.sql
```

### Asset Backup

```bash
# Backup all outputs
tar -czf output_backup_$(date +%Y%m%d).tar.gz output/

# Restore
tar -xzf output_backup_20260730.tar.gz
```

### Disaster Recovery

1. **Database:** Restore from most recent backup
2. **Assets:** Restore from backup storage (S3, GCS)
3. **Configuration:** Rebuild from git repository
4. **API Keys:** Restore from secure vault

## Troubleshooting Deployment

### Container won't start

```bash
# Check logs
docker logs africa-rising

# Test locally first
python3 pipeline.py --help

# Verify all dependencies installed
pip list | grep -E "pydantic|psutil|pexels"
```

### GPU not available in container

```bash
# Install NVIDIA Docker
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | apt-key add -

# Restart container with GPU
docker run --gpus all africa-rising:latest
```

### Out of memory

```bash
# Increase container memory limit
docker run -m 8g africa-rising:latest

# Or in compose:
services:
  pipeline:
    deploy:
      resources:
        limits:
          memory: 8G
```

### Slow video generation

```bash
# Enable GPU
export CUDA_VISIBLE_DEVICES=0

# Use faster models
config.yaml:
  visual_generation:
    runway:
      enabled: true  # Faster
    veo:
      enabled: false  # Slower

# Reduce resolution
config.yaml:
  video_settings:
    resolution: "1024x576"  # Instead of 1280x720
```

## Maintenance

### Regular Updates

```bash
# Check for updates
git pull origin main

# Rebuild container
docker build -t africa-rising:latest .

# Restart service
docker restart africa-rising
```

### Dependency Updates

```bash
# Check for outdated packages
pip list --outdated

# Update requirements
pip install --upgrade pip-audit

# Security audit
pip-audit
```

### Clean Up

```bash
# Remove old logs (>30 days)
find output/logs -name "*.log" -mtime +30 -delete

# Clean Docker
docker system prune -a

# Clear cache
rm -rf cache/*
```
