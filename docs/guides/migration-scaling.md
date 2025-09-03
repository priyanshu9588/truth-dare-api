# Truth and Dare API - Migration and Scaling Guide

## Overview

This guide covers strategies for migrating the Truth and Dare API to more robust architectures and scaling it to handle increased load and features. It includes migration paths, scaling strategies, and future-proofing recommendations.

## Table of Contents

1. [Migration Strategies](#migration-strategies)
2. [Database Migration](#database-migration)
3. [Horizontal Scaling](#horizontal-scaling)
4. [Vertical Scaling](#vertical-scaling)
5. [Performance Optimization](#performance-optimization)
6. [Feature Scaling](#feature-scaling)
7. [Infrastructure Scaling](#infrastructure-scaling)
8. [Monitoring and Observability](#monitoring-and-observability)
9. [Breaking Changes](#breaking-changes)
10. [Version Management](#version-management)

## Migration Strategies

### Current Architecture Assessment

**Current State:**
- JSON file-based data storage
- In-memory caching
- Single-instance deployment
- 110 items (55 truths + 55 dares)
- ~20MB memory footprint
- <50ms response times

**Scaling Triggers:**
- Data volume > 10,000 items
- Concurrent users > 1,000
- Response time > 100ms
- Memory usage > 500MB
- Feature complexity increases

### Migration Paths

#### Path 1: Gradual Enhancement (Recommended)
1. **Phase 1**: Add caching layer (Redis)
2. **Phase 2**: Implement database storage
3. **Phase 3**: Add horizontal scaling
4. **Phase 4**: Microservices architecture

#### Path 2: Database-First Migration
1. **Phase 1**: Migrate to PostgreSQL
2. **Phase 2**: Add connection pooling
3. **Phase 3**: Implement caching
4. **Phase 4**: Scale horizontally

#### Path 3: Cloud-Native Migration
1. **Phase 1**: Containerize application
2. **Phase 2**: Deploy to Kubernetes
3. **Phase 3**: Add managed services
4. **Phase 4**: Implement auto-scaling

## Database Migration

### From JSON to PostgreSQL

#### Step 1: Schema Design

```sql
-- Create database schema
CREATE DATABASE truth_dare_api;

-- Truth questions table
CREATE TABLE truths (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Dare challenges table
CREATE TABLE dares (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    difficulty VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Indexes for performance
CREATE INDEX idx_truths_category ON truths(category) WHERE is_active = TRUE;
CREATE INDEX idx_dares_difficulty ON dares(difficulty) WHERE is_active = TRUE;
CREATE INDEX idx_truths_active ON truths(is_active);
CREATE INDEX idx_dares_active ON dares(is_active);

-- Categories lookup table (optional normalization)
CREATE TABLE truth_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE
);

-- Difficulties lookup table (optional normalization)
CREATE TABLE dare_difficulties (
    id SERIAL PRIMARY KEY,
    name VARCHAR(20) UNIQUE NOT NULL,
    description TEXT,
    sort_order INTEGER,
    is_active BOOLEAN DEFAULT TRUE
);
```

#### Step 2: Data Migration Script

```python
# scripts/migrate_to_postgresql.py
import json
import asyncpg
import asyncio
from pathlib import Path
from typing import List, Dict, Any

async def migrate_data():
    """Migrate JSON data to PostgreSQL."""
    
    # Database connection
    conn = await asyncpg.connect(
        host="localhost",
        port=5432,
        user="truth_dare_user",
        password="secure_password",
        database="truth_dare_api"
    )
    
    try:
        # Load JSON data
        truths_file = Path("app/data/truths.json")
        dares_file = Path("app/data/dares.json")
        
        with open(truths_file, "r") as f:
            truths = json.load(f)
        
        with open(dares_file, "r") as f:
            dares = json.load(f)
        
        # Begin transaction
        async with conn.transaction():
            # Clear existing data
            await conn.execute("DELETE FROM truths")
            await conn.execute("DELETE FROM dares")
            
            # Insert truths
            truth_records = [
                (truth["content"], truth["category"])
                for truth in truths
            ]
            await conn.executemany(
                "INSERT INTO truths (content, category) VALUES ($1, $2)",
                truth_records
            )
            
            # Insert dares
            dare_records = [
                (dare["content"], dare["difficulty"])
                for dare in dares
            ]
            await conn.executemany(
                "INSERT INTO dares (content, difficulty) VALUES ($1, $2)",
                dare_records
            )
            
            print(f"Migrated {len(truths)} truths and {len(dares)} dares")
            
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(migrate_data())
```

#### Step 3: Database Service Implementation

```python
# app/services/database_service.py
import asyncpg
from typing import List, Dict, Any, Optional
from app.core.config import get_settings

class DatabaseService:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Initialize database connection pool."""
        settings = get_settings()
        self.pool = await asyncpg.create_pool(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database=settings.db_name,
            min_size=5,
            max_size=20,
            command_timeout=60
        )
    
    async def disconnect(self):
        """Close database connection pool."""
        if self.pool:
            await self.pool.close()
    
    async def get_random_truth(self) -> Dict[str, Any]:
        """Get a random truth from database."""
        async with self.pool.acquire() as conn:
            result = await conn.fetchrow("""
                SELECT id, content, category 
                FROM truths 
                WHERE is_active = TRUE 
                ORDER BY RANDOM() 
                LIMIT 1
            """)
            return dict(result) if result else None
    
    async def get_truth_by_category(self, category: str) -> Dict[str, Any]:
        """Get a random truth by category."""
        async with self.pool.acquire() as conn:
            result = await conn.fetchrow("""
                SELECT id, content, category 
                FROM truths 
                WHERE category = $1 AND is_active = TRUE 
                ORDER BY RANDOM() 
                LIMIT 1
            """, category)
            return dict(result) if result else None
    
    async def get_truth_categories(self) -> List[str]:
        """Get available truth categories."""
        async with self.pool.acquire() as conn:
            results = await conn.fetch("""
                SELECT DISTINCT category 
                FROM truths 
                WHERE is_active = TRUE 
                ORDER BY category
            """)
            return [row["category"] for row in results]

# Singleton pattern
_database_service = None

async def get_database_service() -> DatabaseService:
    global _database_service
    if _database_service is None:
        _database_service = DatabaseService()
        await _database_service.connect()
    return _database_service
```

#### Step 4: Updated Configuration

```python
# app/core/config.py
class Settings(BaseSettings):
    # Existing settings...
    
    # Database Configuration
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "truth_dare_user"
    db_password: str = ""
    db_name: str = "truth_dare_api"
    db_pool_min_size: int = 5
    db_pool_max_size: int = 20
    
    # Migration settings
    use_database: bool = False  # Feature flag for gradual migration
    json_fallback: bool = True  # Fallback to JSON if DB fails
```

### Migration to NoSQL (MongoDB)

#### Schema Design

```python
# MongoDB document structure
truth_document = {
    "_id": ObjectId(),
    "content": "What is your biggest fear?",
    "category": "deep",
    "tags": ["personal", "emotion"],
    "difficulty_level": 1,  # 1-5 scale
    "age_rating": "13+",
    "language": "en",
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow(),
    "is_active": True,
    "usage_count": 0,
    "rating": {
        "average": 4.2,
        "count": 156
    }
}

dare_document = {
    "_id": ObjectId(),
    "content": "Do 10 jumping jacks",
    "difficulty": "easy",
    "category": "physical",
    "duration_minutes": 1,
    "props_required": [],
    "indoor_suitable": True,
    "outdoor_suitable": True,
    "group_size": {"min": 1, "max": 10},
    "age_rating": "all",
    "safety_level": "safe",
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow(),
    "is_active": True
}
```

#### MongoDB Service

```python
# app/services/mongodb_service.py
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Dict, Any, List, Optional
import random

class MongoDBService:
    def __init__(self, connection_string: str):
        self.client = AsyncIOMotorClient(connection_string)
        self.db = self.client.truth_dare_api
        self.truths = self.db.truths
        self.dares = self.db.dares
    
    async def get_random_truth(self, category: Optional[str] = None) -> Dict[str, Any]:
        """Get random truth with optional category filter."""
        pipeline = [{"$match": {"is_active": True}}]
        
        if category:
            pipeline[0]["$match"]["category"] = category
        
        pipeline.append({"$sample": {"size": 1}})
        
        cursor = self.truths.aggregate(pipeline)
        result = await cursor.to_list(length=1)
        return result[0] if result else None
    
    async def get_enhanced_dare(self, 
                               difficulty: Optional[str] = None,
                               indoor_only: bool = False,
                               max_duration: Optional[int] = None) -> Dict[str, Any]:
        """Get dare with enhanced filtering."""
        match_criteria = {"is_active": True}
        
        if difficulty:
            match_criteria["difficulty"] = difficulty
        if indoor_only:
            match_criteria["indoor_suitable"] = True
        if max_duration:
            match_criteria["duration_minutes"] = {"$lte": max_duration}
        
        pipeline = [
            {"$match": match_criteria},
            {"$sample": {"size": 1}}
        ]
        
        cursor = self.dares.aggregate(pipeline)
        result = await cursor.to_list(length=1)
        return result[0] if result else None
```

## Horizontal Scaling

### Load Balancer Configuration

#### Nginx Load Balancer

```nginx
# /etc/nginx/sites-available/truth-dare-api
upstream truth_dare_backend {
    least_conn;  # Load balancing method
    
    server 10.0.1.10:8000 weight=3 max_fails=3 fail_timeout=30s;
    server 10.0.1.11:8000 weight=3 max_fails=3 fail_timeout=30s;
    server 10.0.1.12:8000 weight=2 max_fails=3 fail_timeout=30s;
    server 10.0.1.13:8000 weight=1 max_fails=3 fail_timeout=30s backup;
}

server {
    listen 80;
    server_name api.truthdare.app;
    
    location / {
        proxy_pass http://truth_dare_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Health check
        proxy_next_upstream error timeout invalid_header http_500 http_502 http_503;
        proxy_connect_timeout 2s;
        proxy_send_timeout 10s;
        proxy_read_timeout 10s;
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        proxy_pass http://truth_dare_backend;
    }
}
```

#### HAProxy Configuration

```bash
# /etc/haproxy/haproxy.cfg
global
    daemon
    maxconn 4096

defaults
    mode http
    timeout connect 5000ms
    timeout client 50000ms
    timeout server 50000ms

frontend truth_dare_frontend
    bind *:80
    default_backend truth_dare_backend

backend truth_dare_backend
    balance roundrobin
    option httpchk GET /api/v1/health
    http-check expect status 200
    
    server api1 10.0.1.10:8000 check inter 30s
    server api2 10.0.1.11:8000 check inter 30s
    server api3 10.0.1.12:8000 check inter 30s
    server api4 10.0.1.13:8000 check inter 30s backup
```

### Container Orchestration

#### Docker Swarm

```yaml
# docker-compose.swarm.yml
version: '3.8'

services:
  truth-dare-api:
    image: truth-dare-api:latest
    deploy:
      replicas: 4
      placement:
        constraints:
          - node.role == worker
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
        window: 120s
      update_config:
        parallelism: 1
        delay: 10s
        failure_action: rollback
    environment:
      - TRUTH_DARE_HOST=0.0.0.0
      - TRUTH_DARE_PORT=8000
    networks:
      - truth-dare-network
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    configs:
      - source: nginx_config
        target: /etc/nginx/nginx.conf
    deploy:
      replicas: 2
      placement:
        constraints:
          - node.role == manager
    networks:
      - truth-dare-network

networks:
  truth-dare-network:
    driver: overlay

configs:
  nginx_config:
    file: ./nginx.conf
```

#### Kubernetes Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: truth-dare-api
  labels:
    app: truth-dare-api
spec:
  replicas: 5
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 1
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
        image: truth-dare-api:v1.2.0
        ports:
        - containerPort: 8000
        env:
        - name: TRUTH_DARE_HOST
          value: "0.0.0.0"
        - name: TRUTH_DARE_DB_HOST
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: host
        resources:
          requests:
            memory: "128Mi"
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

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: truth-dare-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: truth-dare-api
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Session Affinity and State Management

```python
# app/middleware/session.py
from fastapi import Request, Response
import hashlib

class SessionAffinityMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, request: Request, call_next):
        # Generate session ID from client IP or user agent
        client_id = f"{request.client.host}{request.headers.get('user-agent', '')}"
        session_id = hashlib.md5(client_id.encode()).hexdigest()[:8]
        
        response = await call_next(request)
        response.headers["X-Session-ID"] = session_id
        return response
```

## Vertical Scaling

### Resource Optimization

#### Memory Optimization

```python
# app/utils/memory_optimizer.py
import gc
import sys
from typing import Dict, Any
import psutil

class MemoryOptimizer:
    def __init__(self):
        self.process = psutil.Process()
    
    def get_memory_info(self) -> Dict[str, Any]:
        """Get current memory usage information."""
        memory_info = self.process.memory_info()
        return {
            "rss": memory_info.rss / 1024 / 1024,  # MB
            "vms": memory_info.vms / 1024 / 1024,  # MB
            "percent": self.process.memory_percent(),
            "available": psutil.virtual_memory().available / 1024 / 1024  # MB
        }
    
    def optimize_memory(self):
        """Force garbage collection and memory optimization."""
        # Force garbage collection
        collected = gc.collect()
        
        # Clear module caches
        if hasattr(sys, '_clear_type_cache'):
            sys._clear_type_cache()
        
        return {
            "objects_collected": collected,
            "memory_after": self.get_memory_info()
        }

# Periodic memory optimization
@asynccontextmanager
async def memory_management_lifespan(app: FastAPI):
    optimizer = MemoryOptimizer()
    
    async def periodic_cleanup():
        while True:
            await asyncio.sleep(300)  # Every 5 minutes
            optimizer.optimize_memory()
    
    cleanup_task = asyncio.create_task(periodic_cleanup())
    yield
    cleanup_task.cancel()
```

#### CPU Optimization

```python
# app/core/performance.py
import asyncio
import time
from functools import wraps
from typing import Dict, Any

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}
    
    def monitor_endpoint(self, endpoint_name: str):
        """Decorator to monitor endpoint performance."""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                start_cpu = time.process_time()
                
                try:
                    result = await func(*args, **kwargs)
                    return result
                finally:
                    end_time = time.time()
                    end_cpu = time.process_time()
                    
                    # Record metrics
                    self.metrics[endpoint_name] = {
                        "wall_time": end_time - start_time,
                        "cpu_time": end_cpu - start_cpu,
                        "timestamp": end_time
                    }
            return wrapper
        return decorator

# Usage
performance_monitor = PerformanceMonitor()

@router.get("/truth")
@performance_monitor.monitor_endpoint("get_random_truth")
async def get_random_truth():
    # Endpoint implementation
    pass
```

### Database Connection Optimization

```python
# app/core/database.py
import asyncpg
from typing import Optional

class OptimizedDatabasePool:
    def __init__(self, settings):
        self.settings = settings
        self.pool: Optional[asyncpg.Pool] = None
    
    async def initialize(self):
        """Initialize optimized connection pool."""
        self.pool = await asyncpg.create_pool(
            host=self.settings.db_host,
            port=self.settings.db_port,
            user=self.settings.db_user,
            password=self.settings.db_password,
            database=self.settings.db_name,
            
            # Optimized pool settings
            min_size=10,  # Minimum connections
            max_size=50,  # Maximum connections
            max_queries=50000,  # Max queries per connection
            max_inactive_connection_lifetime=300,  # 5 minutes
            
            # Connection optimization
            command_timeout=60,
            server_settings={
                'application_name': 'truth_dare_api',
                'tcp_keepalives_idle': '600',
                'tcp_keepalives_interval': '30',
                'tcp_keepalives_count': '3',
            }
        )
```

## Performance Optimization

### Caching Strategies

#### Redis Implementation

```python
# app/services/cache_service.py
import aioredis
import json
from typing import Optional, Any, Union
from datetime import timedelta

class CacheService:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis: Optional[aioredis.Redis] = None
    
    async def connect(self):
        """Connect to Redis."""
        self.redis = await aioredis.from_url(
            self.redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=20
        )
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        value = await self.redis.get(key)
        return json.loads(value) if value else None
    
    async def set(self, 
                  key: str, 
                  value: Any, 
                  expire: Union[int, timedelta] = 3600) -> bool:
        """Set value in cache with expiration."""
        serialized_value = json.dumps(value)
        return await self.redis.set(key, serialized_value, ex=expire)
    
    async def get_or_set(self, 
                         key: str, 
                         factory_func, 
                         expire: int = 3600) -> Any:
        """Get from cache or set using factory function."""
        value = await self.get(key)
        if value is None:
            value = await factory_func()
            await self.set(key, value, expire)
        return value

# Cache implementation in services
class CachedTruthService:
    def __init__(self, db_service, cache_service):
        self.db_service = db_service
        self.cache_service = cache_service
    
    async def get_random_truth(self) -> Dict[str, Any]:
        """Get random truth with caching."""
        cache_key = "random_truth"
        
        return await self.cache_service.get_or_set(
            cache_key,
            lambda: self.db_service.get_random_truth(),
            expire=300  # 5 minutes
        )
```

#### Multi-layer Caching

```python
# app/services/multilayer_cache.py
from typing import Dict, Any, Optional
import asyncio

class MultiLayerCache:
    def __init__(self, l1_cache, l2_cache, l3_cache=None):
        self.l1 = l1_cache  # In-memory (fastest)
        self.l2 = l2_cache  # Redis (fast)
        self.l3 = l3_cache  # Database (slowest)
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache layers."""
        # Try L1 cache (in-memory)
        value = self.l1.get(key)
        if value is not None:
            return value
        
        # Try L2 cache (Redis)
        value = await self.l2.get(key)
        if value is not None:
            # Populate L1
            self.l1.set(key, value, expire=300)
            return value
        
        # Try L3 cache (Database) if available
        if self.l3:
            value = await self.l3.get(key)
            if value is not None:
                # Populate L2 and L1
                await self.l2.set(key, value, expire=3600)
                self.l1.set(key, value, expire=300)
                return value
        
        return None
    
    async def set(self, key: str, value: Any):
        """Set value in all cache layers."""
        tasks = [
            self.l1.set(key, value, expire=300),
            self.l2.set(key, value, expire=3600)
        ]
        if self.l3:
            tasks.append(self.l3.set(key, value))
        
        await asyncio.gather(*tasks, return_exceptions=True)
```

### API Response Optimization

```python
# app/middleware/compression.py
from fastapi import Request, Response
import gzip
import json

class CompressionMiddleware:
    def __init__(self, app, min_size: int = 1024):
        self.app = app
        self.min_size = min_size
    
    async def __call__(self, request: Request, call_next):
        response = await call_next(request)
        
        # Check if client accepts gzip
        accept_encoding = request.headers.get("accept-encoding", "")
        if "gzip" not in accept_encoding:
            return response
        
        # Get response content
        content = b""
        async for chunk in response.body_iterator:
            content += chunk
        
        # Compress if content is large enough
        if len(content) >= self.min_size:
            compressed_content = gzip.compress(content)
            if len(compressed_content) < len(content):
                response.headers["content-encoding"] = "gzip"
                response.headers["content-length"] = str(len(compressed_content))
                return Response(
                    content=compressed_content,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type
                )
        
        return Response(
            content=content,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type
        )
```

## Feature Scaling

### Advanced API Features

#### Content Personalization

```python
# app/services/personalization_service.py
from typing import Dict, Any, List
import numpy as np

class PersonalizationService:
    def __init__(self, db_service, ml_model=None):
        self.db_service = db_service
        self.ml_model = ml_model
        self.user_preferences = {}
    
    async def get_personalized_truth(self, 
                                    user_id: str, 
                                    user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Get personalized truth based on user profile."""
        
        # Extract user preferences
        age = user_profile.get("age", 18)
        interests = user_profile.get("interests", [])
        difficulty_preference = user_profile.get("difficulty", "medium")
        
        # Calculate category weights based on profile
        category_weights = self._calculate_category_weights(age, interests)
        
        # Get weighted random truth
        return await self._get_weighted_truth(category_weights)
    
    def _calculate_category_weights(self, age: int, interests: List[str]) -> Dict[str, float]:
        """Calculate category weights based on user profile."""
        weights = {
            "general": 1.0,
            "funny": 1.2 if "humor" in interests else 0.8,
            "deep": 1.3 if age > 21 else 0.7,
            "relationships": 1.1 if age > 16 else 0.5,
            "embarrassing": 1.0 if age > 18 else 0.3
        }
        return weights
```

#### Content Rating System

```python
# app/models/rating.py
from pydantic import BaseModel, Field
from typing import Optional

class ContentRating(BaseModel):
    content_id: int
    content_type: str  # "truth" or "dare"
    user_id: Optional[str] = None
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None
    is_appropriate: bool = True
    difficulty_feedback: Optional[str] = None

# app/services/rating_service.py
class RatingService:
    def __init__(self, db_service):
        self.db_service = db_service
    
    async def rate_content(self, rating: ContentRating) -> bool:
        """Rate truth/dare content."""
        # Store rating in database
        await self.db_service.store_rating(rating)
        
        # Update content average rating
        await self._update_content_rating(rating.content_id, rating.content_type)
        
        # Flag inappropriate content
        if not rating.is_appropriate:
            await self._flag_content(rating.content_id, rating.content_type)
        
        return True
    
    async def get_top_rated_content(self, 
                                   content_type: str, 
                                   limit: int = 10) -> List[Dict[str, Any]]:
        """Get highest-rated content."""
        return await self.db_service.get_top_rated(content_type, limit)
```

#### Multi-language Support

```python
# app/services/translation_service.py
from typing import Dict, Any, Optional

class TranslationService:
    def __init__(self):
        self.translations = {}
        self.load_translations()
    
    def load_translations(self):
        """Load translation files."""
        # Load from JSON files or database
        self.translations = {
            "en": {},  # English (default)
            "es": {},  # Spanish
            "fr": {},  # French
            "de": {},  # German
            "pt": {},  # Portuguese
        }
    
    async def get_localized_content(self, 
                                   content_id: int,
                                   content_type: str,
                                   language: str = "en") -> Dict[str, Any]:
        """Get content in specified language."""
        
        # Get original content
        content = await self._get_original_content(content_id, content_type)
        
        # Translate if not in default language
        if language != "en" and language in self.translations:
            translated_content = await self._translate_content(content, language)
            return translated_content
        
        return content
    
    async def _translate_content(self, content: Dict[str, Any], language: str) -> Dict[str, Any]:
        """Translate content to target language."""
        # Use translation service (Google Translate, DeepL, etc.)
        # or lookup pre-translated content
        translated = content.copy()
        
        # Translate the main content
        if "content" in content:
            translated["content"] = await self._translate_text(content["content"], language)
        
        translated["language"] = language
        return translated
```

### Content Management System

```python
# app/services/cms_service.py
from typing import List, Dict, Any, Optional
from datetime import datetime

class ContentManagementService:
    def __init__(self, db_service, cache_service):
        self.db_service = db_service
        self.cache_service = cache_service
    
    async def create_truth(self, truth_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new truth question."""
        # Validate content
        if not self._validate_content(truth_data["content"]):
            raise ValueError("Content validation failed")
        
        # Check for duplicates
        if await self._is_duplicate_content(truth_data["content"], "truth"):
            raise ValueError("Duplicate content detected")
        
        # Create truth
        truth = await self.db_service.create_truth(truth_data)
        
        # Invalidate cache
        await self.cache_service.invalidate_pattern("truth_*")
        
        return truth
    
    async def moderate_content(self, 
                              content_id: int, 
                              content_type: str,
                              action: str,
                              reason: Optional[str] = None) -> bool:
        """Moderate content (approve, reject, flag)."""
        
        moderation_record = {
            "content_id": content_id,
            "content_type": content_type,
            "action": action,
            "reason": reason,
            "moderated_at": datetime.utcnow(),
            "moderated_by": "system"  # or user_id
        }
        
        # Store moderation action
        await self.db_service.store_moderation(moderation_record)
        
        # Update content status
        if action == "reject":
            await self.db_service.deactivate_content(content_id, content_type)
        elif action == "approve":
            await self.db_service.activate_content(content_id, content_type)
        
        # Invalidate cache
        await self.cache_service.invalidate_pattern(f"{content_type}_*")
        
        return True
    
    def _validate_content(self, content: str) -> bool:
        """Validate content for appropriateness."""
        # Basic validation rules
        if len(content) < 10 or len(content) > 500:
            return False
        
        # Check for inappropriate words
        inappropriate_words = ["bad_word1", "bad_word2"]  # Load from config
        content_lower = content.lower()
        
        for word in inappropriate_words:
            if word in content_lower:
                return False
        
        return True
```

## Infrastructure Scaling

### Auto-scaling Configuration

#### AWS Auto Scaling

```yaml
# cloudformation/autoscaling.yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Truth and Dare API Auto Scaling Configuration'

Parameters:
  MinSize:
    Type: Number
    Default: 2
    Description: Minimum number of instances
  
  MaxSize:
    Type: Number
    Default: 20
    Description: Maximum number of instances
  
  DesiredCapacity:
    Type: Number
    Default: 3
    Description: Desired number of instances

Resources:
  LaunchTemplate:
    Type: AWS::EC2::LaunchTemplate
    Properties:
      LaunchTemplateName: truth-dare-api-template
      LaunchTemplateData:
        ImageId: ami-12345678  # Your AMI ID
        InstanceType: t3.medium
        IamInstanceProfile:
          Arn: !GetAtt InstanceProfile.Arn
        SecurityGroupIds:
          - !Ref SecurityGroup
        UserData:
          Fn::Base64: !Sub |
            #!/bin/bash
            docker run -d \
              --name truth-dare-api \
              -p 8000:8000 \
              -e TRUTH_DARE_HOST=0.0.0.0 \
              -e TRUTH_DARE_DB_HOST=${DatabaseEndpoint} \
              truth-dare-api:latest

  AutoScalingGroup:
    Type: AWS::AutoScaling::AutoScalingGroup
    Properties:
      AutoScalingGroupName: truth-dare-api-asg
      LaunchTemplate:
        LaunchTemplateId: !Ref LaunchTemplate
        Version: !GetAtt LaunchTemplate.LatestVersionNumber
      MinSize: !Ref MinSize
      MaxSize: !Ref MaxSize
      DesiredCapacity: !Ref DesiredCapacity
      VPCZoneIdentifier:
        - subnet-12345678
        - subnet-87654321
      TargetGroupARNs:
        - !Ref TargetGroup
      HealthCheckType: ELB
      HealthCheckGracePeriod: 300
      Tags:
        - Key: Name
          Value: truth-dare-api-instance
          PropagateAtLaunch: true

  ScaleUpPolicy:
    Type: AWS::AutoScaling::ScalingPolicy
    Properties:
      AutoScalingGroupName: !Ref AutoScalingGroup
      PolicyType: StepScaling
      AdjustmentType: ChangeInCapacity
      StepAdjustments:
        - MetricIntervalLowerBound: 0
          MetricIntervalUpperBound: 50
          ScalingAdjustment: 1
        - MetricIntervalLowerBound: 50
          ScalingAdjustment: 2

  CPUAlarmHigh:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmDescription: 'High CPU utilization alarm'
      MetricName: CPUUtilization
      Namespace: AWS/EC2
      Statistic: Average
      Period: 300
      EvaluationPeriods: 2
      Threshold: 70
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref ScaleUpPolicy
      Dimensions:
        - Name: AutoScalingGroupName
          Value: !Ref AutoScalingGroup
```

#### Kubernetes Horizontal Pod Autoscaler

```yaml
# k8s/hpa-advanced.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: truth-dare-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: truth-dare-api
  minReplicas: 3
  maxReplicas: 50
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "100"
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
      - type: Pods
        value: 2
        periodSeconds: 60
```

### Content Delivery Network (CDN)

```python
# app/middleware/cdn.py
from fastapi import Request, Response
import hashlib
import time

class CDNMiddleware:
    def __init__(self, app, cdn_enabled: bool = True):
        self.app = app
        self.cdn_enabled = cdn_enabled
        self.cache_headers = {
            "/api/v1/truth/categories/list": 3600,  # 1 hour
            "/api/v1/dare/difficulties/list": 3600,  # 1 hour
            "/api/v1/stats": 300,  # 5 minutes
            "/api/v1/health": 60,   # 1 minute
        }
    
    async def __call__(self, request: Request, call_next):
        response = await call_next(request)
        
        if not self.cdn_enabled:
            return response
        
        path = request.url.path
        
        # Add cache headers for static-ish endpoints
        if path in self.cache_headers:
            max_age = self.cache_headers[path]
            response.headers["Cache-Control"] = f"public, max-age={max_age}"
            response.headers["Expires"] = str(int(time.time()) + max_age)
            
            # Add ETag for better caching
            content = response.body
            etag = hashlib.md5(content).hexdigest()
            response.headers["ETag"] = f'"{etag}"'
            
            # Check if client has cached version
            if request.headers.get("If-None-Match") == f'"{etag}"':
                return Response(status_code=304)
        
        return response
```

## Monitoring and Observability

### Advanced Metrics Collection

```python
# app/middleware/metrics.py
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry
import time
import psutil

# Custom registry for better control
registry = CollectorRegistry()

# Metrics
REQUEST_COUNT = Counter(
    'http_requests_total', 
    'Total HTTP requests',
    ['method', 'endpoint', 'status'],
    registry=registry
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint'],
    registry=registry,
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

ACTIVE_CONNECTIONS = Gauge(
    'active_connections',
    'Active connections',
    registry=registry
)

MEMORY_USAGE = Gauge(
    'memory_usage_bytes',
    'Memory usage in bytes',
    registry=registry
)

CPU_USAGE = Gauge(
    'cpu_usage_percent',
    'CPU usage percentage',
    registry=registry
)

class MetricsMiddleware:
    def __init__(self, app):
        self.app = app
        self.active_requests = 0
    
    async def __call__(self, request: Request, call_next):
        start_time = time.time()
        self.active_requests += 1
        ACTIVE_CONNECTIONS.set(self.active_requests)
        
        try:
            response = await call_next(request)
            
            # Record metrics
            duration = time.time() - start_time
            REQUEST_DURATION.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(duration)
            
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status=response.status_code
            ).inc()
            
            return response
        
        finally:
            self.active_requests -= 1
            ACTIVE_CONNECTIONS.set(self.active_requests)

# Background task to update system metrics
async def update_system_metrics():
    """Update system-level metrics."""
    while True:
        process = psutil.Process()
        MEMORY_USAGE.set(process.memory_info().rss)
        CPU_USAGE.set(process.cpu_percent())
        await asyncio.sleep(10)
```

### Distributed Tracing

```python
# app/middleware/tracing.py
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor

def setup_tracing(app, service_name: str = "truth-dare-api"):
    """Set up distributed tracing."""
    
    # Configure tracer provider
    trace.set_tracer_provider(TracerProvider())
    tracer = trace.get_tracer(__name__)
    
    # Configure Jaeger exporter
    jaeger_exporter = JaegerExporter(
        agent_host_name="jaeger-agent",
        agent_port=6831,
    )
    
    span_processor = BatchSpanProcessor(jaeger_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)
    
    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)
    
    # Instrument database and cache
    AsyncPGInstrumentor().instrument()
    RedisInstrumentor().instrument()
    
    return tracer

# Custom span decorator
def trace_function(name: str = None):
    """Decorator to trace function execution."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            tracer = trace.get_tracer(__name__)
            span_name = name or f"{func.__module__}.{func.__name__}"
            
            with tracer.start_as_current_span(span_name) as span:
                # Add function metadata
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)
                
                try:
                    result = await func(*args, **kwargs)
                    span.set_attribute("function.result.type", type(result).__name__)
                    return result
                except Exception as e:
                    span.record_exception(e)
                    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                    raise
        return wrapper
    return decorator
```

## Breaking Changes

### API Versioning Strategy

```python
# app/routes/versioning.py
from fastapi import APIRouter, Header, HTTPException
from typing import Optional

class APIVersionMiddleware:
    def __init__(self, app, default_version: str = "v1"):
        self.app = app
        self.default_version = default_version
        self.supported_versions = ["v1", "v2"]
    
    async def __call__(self, request: Request, call_next):
        # Get version from header or path
        version = self._get_api_version(request)
        
        if version not in self.supported_versions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported API version: {version}. Supported: {self.supported_versions}"
            )
        
        # Add version to request state
        request.state.api_version = version
        
        response = await call_next(request)
        response.headers["API-Version"] = version
        return response
    
    def _get_api_version(self, request: Request) -> str:
        # Check path prefix
        if request.url.path.startswith("/api/v2/"):
            return "v2"
        elif request.url.path.startswith("/api/v1/"):
            return "v1"
        
        # Check header
        version_header = request.headers.get("API-Version", self.default_version)
        return version_header

# Versioned response models
class TruthResponseV1(BaseResponse):
    id: int
    content: str
    category: str

class TruthResponseV2(BaseResponse):
    id: int
    content: str
    category: str
    tags: List[str]
    difficulty_level: int
    age_rating: str
    language: str = "en"

# Versioned endpoints
@router.get("/truth", response_model=Union[TruthResponseV1, TruthResponseV2])
async def get_truth(request: Request):
    version = request.state.api_version
    
    if version == "v1":
        # Return v1 format
        truth = await truth_service.get_random_truth()
        return TruthResponseV1(**truth)
    elif version == "v2":
        # Return v2 format with additional fields
        truth = await truth_service.get_enhanced_truth()
        return TruthResponseV2(**truth)
```

### Migration Scripts

```python
# scripts/migrate_v1_to_v2.py
import asyncio
import json
from pathlib import Path
from typing import Dict, Any, List

async def migrate_v1_to_v2():
    """Migrate from v1 data format to v2."""
    
    print("Starting migration from v1 to v2...")
    
    # Backup existing data
    await backup_existing_data()
    
    # Load v1 data
    v1_truths = load_json_data("app/data/truths.json")
    v1_dares = load_json_data("app/data/dares.json")
    
    # Convert to v2 format
    v2_truths = convert_truths_to_v2(v1_truths)
    v2_dares = convert_dares_to_v2(v1_dares)
    
    # Save v2 data
    save_json_data("app/data/truths_v2.json", v2_truths)
    save_json_data("app/data/dares_v2.json", v2_dares)
    
    # Validate migration
    if await validate_migration(v1_truths, v2_truths, v1_dares, v2_dares):
        print("Migration completed successfully!")
        
        # Move v2 files to production locations
        Path("app/data/truths_v2.json").rename("app/data/truths.json")
        Path("app/data/dares_v2.json").rename("app/data/dares.json")
    else:
        print("Migration validation failed!")
        return False
    
    return True

def convert_truths_to_v2(v1_truths: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert v1 truth format to v2."""
    v2_truths = []
    
    for truth in v1_truths:
        v2_truth = {
            "id": truth["id"],
            "content": truth["content"],
            "category": truth["category"],
            
            # New v2 fields
            "tags": generate_tags(truth["content"], truth["category"]),
            "difficulty_level": assign_difficulty_level(truth["content"]),
            "age_rating": determine_age_rating(truth["content"], truth["category"]),
            "language": "en",
            "created_at": "2025-01-01T00:00:00Z",  # Default timestamp
            "updated_at": "2025-01-01T00:00:00Z",
            "is_active": True,
            "usage_count": 0,
            "rating": {"average": 0.0, "count": 0}
        }
        v2_truths.append(v2_truth)
    
    return v2_truths

def generate_tags(content: str, category: str) -> List[str]:
    """Generate tags based on content and category."""
    tags = [category]
    
    # Add content-based tags
    content_lower = content.lower()
    
    tag_keywords = {
        "personal": ["you", "your", "yourself"],
        "emotion": ["feel", "emotion", "happy", "sad", "angry", "fear"],
        "relationship": ["love", "friend", "family", "partner"],
        "experience": ["ever", "time", "moment", "experience"],
        "opinion": ["think", "believe", "opinion", "prefer"]
    }
    
    for tag, keywords in tag_keywords.items():
        if any(keyword in content_lower for keyword in keywords):
            tags.append(tag)
    
    return list(set(tags))  # Remove duplicates

async def validate_migration(v1_truths, v2_truths, v1_dares, v2_dares) -> bool:
    """Validate that migration preserved all data correctly."""
    
    # Check counts
    if len(v1_truths) != len(v2_truths):
        print(f"Truth count mismatch: {len(v1_truths)} -> {len(v2_truths)}")
        return False
    
    if len(v1_dares) != len(v2_dares):
        print(f"Dare count mismatch: {len(v1_dares)} -> {len(v2_dares)}")
        return False
    
    # Validate truth data preservation
    for v1_truth in v1_truths:
        v2_truth = next((t for t in v2_truths if t["id"] == v1_truth["id"]), None)
        if not v2_truth:
            print(f"Missing truth ID: {v1_truth['id']}")
            return False
        
        if (v2_truth["content"] != v1_truth["content"] or 
            v2_truth["category"] != v1_truth["category"]):
            print(f"Truth data mismatch for ID: {v1_truth['id']}")
            return False
    
    print("Migration validation passed!")
    return True

if __name__ == "__main__":
    asyncio.run(migrate_v1_to_v2())
```

## Version Management

### Backward Compatibility

```python
# app/core/compatibility.py
from typing import Dict, Any, Union
from packaging import version

class CompatibilityLayer:
    def __init__(self):
        self.compatibility_matrix = {
            "v1": {
                "supported_until": "2026-01-01",
                "deprecation_warnings": True,
                "breaking_changes": []
            },
            "v2": {
                "supported_until": "2027-01-01",
                "deprecation_warnings": False,
                "breaking_changes": [
                    "truth response format extended",
                    "dare response format extended",
                    "new required headers"
                ]
            }
        }
    
    def is_version_supported(self, api_version: str) -> bool:
        """Check if API version is still supported."""
        return api_version in self.compatibility_matrix
    
    def get_deprecation_warning(self, api_version: str) -> Union[str, None]:
        """Get deprecation warning for version."""
        version_info = self.compatibility_matrix.get(api_version)
        if not version_info:
            return None
        
        if version_info.get("deprecation_warnings"):
            return (f"API version {api_version} is deprecated. "
                   f"Support ends on {version_info['supported_until']}. "
                   f"Please migrate to v2.")
        
        return None
    
    def transform_response(self, 
                          data: Dict[str, Any], 
                          from_version: str, 
                          to_version: str) -> Dict[str, Any]:
        """Transform response between API versions."""
        
        if from_version == to_version:
            return data
        
        # v2 to v1 transformation (backward compatibility)
        if from_version == "v2" and to_version == "v1":
            return self._downgrade_v2_to_v1(data)
        
        # v1 to v2 transformation (forward compatibility)
        if from_version == "v1" and to_version == "v2":
            return self._upgrade_v1_to_v2(data)
        
        return data
    
    def _downgrade_v2_to_v1(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove v2-specific fields for v1 compatibility."""
        v1_data = {
            "id": data["id"],
            "content": data["content"],
            "category": data.get("category") or data.get("difficulty")
        }
        
        if "type" in data:
            v1_data["type"] = data["type"]
        
        return v1_data
    
    def _upgrade_v1_to_v2(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add v2 fields with default values."""
        v2_data = data.copy()
        
        # Add default v2 fields
        if "tags" not in v2_data:
            v2_data["tags"] = [data.get("category", "general")]
        
        if "difficulty_level" not in v2_data:
            v2_data["difficulty_level"] = 1
        
        if "age_rating" not in v2_data:
            v2_data["age_rating"] = "13+"
        
        if "language" not in v2_data:
            v2_data["language"] = "en"
        
        return v2_data
```

This comprehensive migration and scaling guide provides detailed strategies for evolving the Truth and Dare API from its current simple architecture to a robust, scalable system capable of handling enterprise-level loads and feature complexity.