# Truth and Dare API - Deployment Guide

## Overview

This guide covers deploying the Truth and Dare API to production environments, including cloud platforms, containerization, and production best practices.

## Table of Contents

1. [Production Checklist](#production-checklist)
2. [Environment Configuration](#environment-configuration)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Platform Deployment](#cloud-platform-deployment)
5. [Load Balancing and Scaling](#load-balancing-and-scaling)
6. [Monitoring and Logging](#monitoring-and-logging)
7. [Security Considerations](#security-considerations)
8. [Performance Optimization](#performance-optimization)
9. [Backup and Recovery](#backup-and-recovery)
10. [Troubleshooting](#troubleshooting)

## Production Checklist

### Pre-deployment Requirements

#### System Requirements
- [ ] Python 3.11+ runtime environment
- [ ] Minimum 512MB RAM (1GB+ recommended)
- [ ] 50MB+ disk space for application
- [ ] Network access for HTTP/HTTPS traffic
- [ ] SSL certificates for HTTPS (recommended)

#### Security Requirements
- [ ] Environment variables configured securely
- [ ] CORS origins properly configured
- [ ] Rate limiting implemented (if needed)
- [ ] Security headers configured
- [ ] Input validation verified
- [ ] Error handling doesn't expose sensitive data

#### Performance Requirements
- [ ] Data files (truths.json, dares.json) optimized
- [ ] Memory usage monitored
- [ ] Response time targets defined
- [ ] Concurrent user limits established
- [ ] Load testing completed

#### Monitoring Requirements
- [ ] Health check endpoint tested
- [ ] Application logging configured
- [ ] Metrics collection setup
- [ ] Alerting rules defined
- [ ] Backup procedures established

## Environment Configuration

### Production Environment Variables

Create a production `.env` file with these settings:

```env
# Server Configuration - Production Settings
TRUTH_DARE_HOST=0.0.0.0
TRUTH_DARE_PORT=8000
TRUTH_DARE_DEBUG=false

# API Configuration
TRUTH_DARE_API_V1_PREFIX=/api/v1
TRUTH_DARE_CORS_ORIGINS=https://yourfrontend.com,https://yourmobileapp.com

# Data Configuration
TRUTH_DARE_TRUTHS_FILE_PATH=app/data/truths.json
TRUTH_DARE_DARES_FILE_PATH=app/data/dares.json

# Logging Configuration - Production Level
TRUTH_DARE_LOG_LEVEL=INFO
TRUTH_DARE_LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# Performance Configuration
TRUTH_DARE_CACHE_EXPIRY_SECONDS=3600
TRUTH_DARE_MAX_CONCURRENT_REQUESTS=1000

# Application Information
TRUTH_DARE_APP_NAME=Truth and Dare API
TRUTH_DARE_APP_VERSION=0.1.0
```

### Environment-specific Configurations

#### Development
```env
TRUTH_DARE_DEBUG=true
TRUTH_DARE_LOG_LEVEL=DEBUG
TRUTH_DARE_HOST=127.0.0.1
TRUTH_DARE_CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

#### Staging
```env
TRUTH_DARE_DEBUG=false
TRUTH_DARE_LOG_LEVEL=INFO
TRUTH_DARE_HOST=0.0.0.0
TRUTH_DARE_CORS_ORIGINS=https://staging.yourapp.com
```

#### Production
```env
TRUTH_DARE_DEBUG=false
TRUTH_DARE_LOG_LEVEL=WARNING
TRUTH_DARE_HOST=0.0.0.0
TRUTH_DARE_CORS_ORIGINS=https://yourapp.com
```

## Docker Deployment

### Dockerfile

Create an optimized production Dockerfile:

```dockerfile
# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app
USER app

# Copy application code
COPY --chown=app:app app/ ./app/

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Run application with Gunicorn for production
CMD ["gunicorn", "app.main:app", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--workers", "4", \
     "--bind", "0.0.0.0:8000", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info"]
```

### Docker Compose for Production

```yaml
version: '3.8'

services:
  truth-dare-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - TRUTH_DARE_HOST=0.0.0.0
      - TRUTH_DARE_PORT=8000
      - TRUTH_DARE_DEBUG=false
      - TRUTH_DARE_LOG_LEVEL=INFO
    volumes:
      - ./app/data:/app/app/data:ro
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - truth-dare-api
    restart: unless-stopped
```

### Building and Running

```bash
# Build the image
docker build -t truth-dare-api:latest .

# Run container
docker run -d \
  --name truth-dare-api \
  -p 8000:8000 \
  --env-file .env.production \
  truth-dare-api:latest

# Check logs
docker logs truth-dare-api

# Check health
curl http://localhost:8000/api/v1/health
```

## Cloud Platform Deployment

### AWS Deployment

#### Using AWS Fargate (ECS)

**Task Definition:**
```json
{
  "family": "truth-dare-api",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "truth-dare-api",
      "image": "your-account.dkr.ecr.region.amazonaws.com/truth-dare-api:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "TRUTH_DARE_HOST",
          "value": "0.0.0.0"
        },
        {
          "name": "TRUTH_DARE_DEBUG",
          "value": "false"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/truth-dare-api",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### Using AWS Lambda (Serverless)

**serverless.yml:**
```yaml
service: truth-dare-api

provider:
  name: aws
  runtime: python3.11
  stage: prod
  region: us-west-2
  
functions:
  api:
    handler: lambda_handler.handler
    events:
      - http:
          path: /{proxy+}
          method: ANY
          cors: true
    timeout: 30
    memorySize: 512
```

**lambda_handler.py:**
```python
from mangum import Mangum
from app.main import app

handler = Mangum(app)
```

### Google Cloud Platform (GCP)

#### Cloud Run Deployment

```bash
# Build and push to Container Registry
gcloud builds submit --tag gcr.io/PROJECT-ID/truth-dare-api

# Deploy to Cloud Run
gcloud run deploy truth-dare-api \
  --image gcr.io/PROJECT-ID/truth-dare-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000 \
  --memory 512Mi \
  --cpu 1 \
  --max-instances 10
```

### Microsoft Azure

#### Container Instances

```bash
# Create resource group
az group create --name truth-dare-rg --location eastus

# Deploy container
az container create \
  --resource-group truth-dare-rg \
  --name truth-dare-api \
  --image your-registry/truth-dare-api:latest \
  --dns-name-label truth-dare-api \
  --ports 8000 \
  --environment-variables \
    TRUTH_DARE_HOST=0.0.0.0 \
    TRUTH_DARE_DEBUG=false
```

### DigitalOcean App Platform

**app.yaml:**
```yaml
name: truth-dare-api
services:
- name: api
  source_dir: /
  github:
    repo: your-username/truth-dare-api
    branch: main
  run_command: gunicorn app.main:app --worker-class uvicorn.workers.UvicornWorker --workers 2 --bind 0.0.0.0:8080
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  routes:
  - path: /
  envs:
  - key: TRUTH_DARE_DEBUG
    value: "false"
  - key: TRUTH_DARE_HOST
    value: "0.0.0.0"
  - key: TRUTH_DARE_PORT
    value: "8080"
```

## Load Balancing and Scaling

### Nginx Configuration

```nginx
upstream truth_dare_api {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
    server 127.0.0.1:8004;
}

server {
    listen 80;
    server_name api.yourapp.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourapp.com;
    
    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS;
    
    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    
    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    
    location / {
        limit_req zone=api burst=20 nodelay;
        
        proxy_pass http://truth_dare_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 5s;
        proxy_send_timeout 10s;
        proxy_read_timeout 10s;
    }
    
    # Health check endpoint (no rate limiting)
    location /api/v1/health {
        proxy_pass http://truth_dare_api;
        access_log off;
    }
}
```

### Horizontal Scaling with Gunicorn

```bash
# Multi-worker deployment
gunicorn app.main:app \
  --worker-class uvicorn.workers.UvicornWorker \
  --workers $(nproc) \
  --bind 0.0.0.0:8000 \
  --max-requests 1000 \
  --max-requests-jitter 100 \
  --timeout 30 \
  --keepalive 5 \
  --access-logfile - \
  --error-logfile - \
  --log-level info
```

### Kubernetes Deployment

**deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: truth-dare-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: truth-dare-api
  template:
    metadata:
      labels:
        app: truth-dare-api
    spec:
      containers:
      - name: api
        image: truth-dare-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: TRUTH_DARE_HOST
          value: "0.0.0.0"
        - name: TRUTH_DARE_DEBUG
          value: "false"
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: truth-dare-api-service
spec:
  selector:
    app: truth-dare-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

## Monitoring and Logging

### Application Monitoring

#### Health Check Integration

```python
# Custom health check endpoint
@app.get("/api/v1/health")
async def enhanced_health_check():
    health_data = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0",
        "uptime": time.time() - start_time,
        "checks": {
            "data_availability": check_data_files(),
            "memory_usage": get_memory_usage(),
            "response_time": measure_response_time()
        }
    }
    return health_data
```

#### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, generate_latest

# Metrics
REQUEST_COUNT = Counter('requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('request_duration_seconds', 'Request duration')

@app.middleware("http")
async def add_prometheus_metrics(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_DURATION.observe(time.time() - start_time)
    
    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### Centralized Logging

#### Structured Logging Configuration

```python
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
```

#### ELK Stack Integration

**logstash.conf:**
```
input {
  beats {
    port => 5044
  }
}

filter {
  if [fields][service] == "truth-dare-api" {
    json {
      source => "message"
    }
    
    date {
      match => [ "timestamp", "ISO8601" ]
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "truth-dare-api-%{+YYYY.MM.dd}"
  }
}
```

**filebeat.yml:**
```yaml
filebeat.inputs:
- type: container
  paths:
    - '/var/lib/docker/containers/*/*.log'
  fields:
    service: truth-dare-api
  fields_under_root: true

output.logstash:
  hosts: ["logstash:5044"]
```

## Security Considerations

### Security Headers

```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

# Add security middleware
app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["api.yourapp.com", "*.yourapp.com"]
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    return response
```

### Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

@app.get("/api/v1/truth")
@limiter.limit("10/minute")
async def get_truth(request: Request):
    # Endpoint logic here
    pass
```

### SSL/TLS Configuration

```bash
# Generate SSL certificate (Let's Encrypt)
certbot certonly --webroot \
  -w /var/www/html \
  -d api.yourapp.com \
  --email admin@yourapp.com \
  --agree-tos \
  --non-interactive

# Auto-renewal
echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -
```

## Performance Optimization

### Caching Strategies

```python
from functools import lru_cache
import asyncio

# Response caching
@lru_cache(maxsize=1000)
def cache_response(endpoint: str, params: str) -> str:
    # Cache implementation
    pass

# Async caching with TTL
class AsyncCache:
    def __init__(self):
        self._cache = {}
        self._timestamps = {}
        self._ttl = 3600  # 1 hour
    
    async def get(self, key: str):
        if key in self._cache:
            if time.time() - self._timestamps[key] < self._ttl:
                return self._cache[key]
            else:
                del self._cache[key]
                del self._timestamps[key]
        return None
    
    async def set(self, key: str, value):
        self._cache[key] = value
        self._timestamps[key] = time.time()
```

### Database Optimization (Future)

```python
# When migrating to PostgreSQL
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

### CDN Integration

```python
# CloudFront configuration for static responses
@app.middleware("http")
async def add_cache_headers(request: Request, call_next):
    response = await call_next(request)
    
    if request.url.path.startswith("/api/v1/"):
        if request.url.path in ["/api/v1/truth/categories/list", "/api/v1/dare/difficulties/list"]:
            response.headers["Cache-Control"] = "public, max-age=3600"
        else:
            response.headers["Cache-Control"] = "public, max-age=300"
    
    return response
```

## Backup and Recovery

### Data Backup Strategy

```bash
#!/bin/bash
# backup_data.sh

BACKUP_DIR="/backups/truth-dare-api"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p "$BACKUP_DIR/$DATE"

# Backup data files
cp app/data/truths.json "$BACKUP_DIR/$DATE/"
cp app/data/dares.json "$BACKUP_DIR/$DATE/"

# Compress backup
tar -czf "$BACKUP_DIR/backup_$DATE.tar.gz" -C "$BACKUP_DIR" "$DATE"

# Remove uncompressed files
rm -rf "$BACKUP_DIR/$DATE"

# Keep only last 30 backups
find "$BACKUP_DIR" -name "backup_*.tar.gz" -mtime +30 -delete

echo "Backup completed: backup_$DATE.tar.gz"
```

### Disaster Recovery Plan

1. **Data Recovery**: Restore from latest backup
2. **Infrastructure Recovery**: Redeploy using Infrastructure as Code
3. **Configuration Recovery**: Restore environment variables
4. **Health Verification**: Run health checks and tests

```bash
#!/bin/bash
# restore_data.sh

BACKUP_FILE="$1"
RESTORE_DIR="/app/data"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file.tar.gz>"
    exit 1
fi

# Extract backup
tar -xzf "$BACKUP_FILE" -C /tmp/

# Find extracted directory
EXTRACTED_DIR=$(tar -tzf "$BACKUP_FILE" | head -1 | cut -f1 -d"/")

# Restore files
cp "/tmp/$EXTRACTED_DIR/truths.json" "$RESTORE_DIR/"
cp "/tmp/$EXTRACTED_DIR/dares.json" "$RESTORE_DIR/"

# Cleanup
rm -rf "/tmp/$EXTRACTED_DIR"

# Restart application
systemctl restart truth-dare-api

echo "Data restored from $BACKUP_FILE"
```

## Troubleshooting

### Common Issues

#### Application Won't Start

**Symptoms**: Container/process fails to start
**Possible Causes**:
- Missing data files
- Invalid configuration
- Port conflicts
- Permission issues

**Solutions**:
```bash
# Check file permissions
ls -la app/data/

# Verify configuration
python -c "from app.core.config import get_settings; print(get_settings())"

# Check port availability
netstat -tlnp | grep :8000

# Review logs
docker logs truth-dare-api
```

#### High Memory Usage

**Symptoms**: Out of memory errors, slow responses
**Possible Causes**:
- Memory leaks in application
- Too many worker processes
- Large data files loaded multiple times

**Solutions**:
```bash
# Monitor memory usage
docker stats truth-dare-api

# Reduce worker count
gunicorn --workers 2 app.main:app

# Profile memory usage
python -m memory_profiler app/main.py
```

#### Slow Response Times

**Symptoms**: High response latencies
**Possible Causes**:
- Data not cached properly
- Inefficient data structures
- Network latency
- Resource constraints

**Solutions**:
```bash
# Check data loading
curl -w "@curl-format.txt" http://localhost:8000/api/v1/health

# Monitor resource usage
top -p $(pgrep gunicorn)

# Enable profiling
python -m cProfile -o profile.stats app/main.py
```

### Monitoring Commands

```bash
# Health check
curl -f http://localhost:8000/api/v1/health

# Performance test
ab -n 1000 -c 10 http://localhost:8000/api/v1/truth

# Memory usage
ps aux | grep gunicorn

# Network connections
netstat -an | grep :8000

# Disk usage
df -h

# Application logs
tail -f /var/log/truth-dare-api/app.log
```

### Emergency Procedures

#### Quick Rollback

```bash
#!/bin/bash
# rollback.sh

PREVIOUS_VERSION="$1"

if [ -z "$PREVIOUS_VERSION" ]; then
    echo "Usage: $0 <previous_version>"
    exit 1
fi

# Stop current version
docker stop truth-dare-api

# Start previous version
docker run -d \
  --name truth-dare-api \
  -p 8000:8000 \
  --env-file .env.production \
  "truth-dare-api:$PREVIOUS_VERSION"

echo "Rolled back to version $PREVIOUS_VERSION"
```

#### Scale Up Quickly

```bash
# Kubernetes scale up
kubectl scale deployment truth-dare-api --replicas=10

# Docker Compose scale up
docker-compose up -d --scale truth-dare-api=5

# Manual instances
for port in 8001 8002 8003; do
    docker run -d -p $port:8000 truth-dare-api:latest
done
```

This deployment guide provides comprehensive instructions for deploying the Truth and Dare API in various production environments with proper monitoring, security, and scaling considerations.