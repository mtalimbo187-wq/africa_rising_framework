# Deployment Guide - AI Documentary Studio

Complete deployment instructions for production environments.

---

## Quick Start (Local)

```bash
# Clone repository
git clone https://github.com/mtalimbo187-wq/africa_rising_framework.git
cd africa_rising_framework

# Install dependencies
pip install -r requirements.txt

# Set API keys (optional, falls back to mock)
export RUNWAY_API_KEY="key_..."
export PEXELS_API_KEY="..."
export ELEVENLABS_API_KEY="..."
export TAVILY_API_KEY="..."

# Run production
python3 -m src.main

# View dashboard
open dashboard.html
```

---

## Docker Deployment

### Build & Run

```bash
# Build image
docker build -t documentary-studio:latest .

# Run container
docker run \
  -e RUNWAY_API_KEY="key_..." \
  -e ELEVENLABS_API_KEY="..." \
  -v $(pwd)/output:/app/output \
  documentary-studio:latest
```

---

## Cloud Deployment

### AWS Lambda

```bash
pip install -r requirements.txt -t package/
cp -r src/ package/

cd package && zip -r ../lambda_function.zip . && cd ..

aws lambda create-function \
  --function-name documentary-studio \
  --runtime python3.9 \
  --role arn:aws:iam::ACCOUNT:role/ROLE_NAME \
  --handler lambda_handler.lambda_handler \
  --zip-file fileb://lambda_function.zip \
  --timeout 300 \
  --memory-size 1024
```

### Google Cloud Run

```bash
gcloud run deploy documentary-studio \
  --source . \
  --platform managed \
  --region us-central1 \
  --set-env-vars RUNWAY_API_KEY=key_...,ELEVENLABS_API_KEY=... \
  --memory 1Gi \
  --timeout 300
```

### Heroku

```bash
heroku create documentary-studio
heroku config:set RUNWAY_API_KEY=key_...
heroku config:set ELEVENLABS_API_KEY=...
git push heroku main
```

---

## Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: documentary-studio
spec:
  replicas: 3
  selector:
    matchLabels:
      app: studio
  template:
    metadata:
      labels:
        app: studio
    spec:
      containers:
      - name: studio
        image: documentary-studio:latest
        env:
        - name: RUNWAY_API_KEY
          valueFrom:
            secretKeyRef:
              name: studio-secrets
              key: runway-key
```

---

## API Server (FastAPI)

```bash
pip install fastapi uvicorn
python3 app.py
# API available at http://localhost:8000/docs
```

---

## Environment Variables

```bash
RUNWAY_API_KEY=key_...
PEXELS_API_KEY=...
ELEVENLABS_API_KEY=...
TAVILY_API_KEY=...
DEBUG=False
LOG_LEVEL=INFO
```

---

## Support

- Documentation: IMPLEMENTATION_COMPLETE.md
- GitHub: https://github.com/mtalimbo187-wq/africa_rising_framework
- Status: 🚀 Ready for Production
