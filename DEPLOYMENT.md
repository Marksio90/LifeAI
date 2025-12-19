# LifeAI Deployment Guide

This document provides instructions for deploying LifeAI to various environments.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Local Development](#local-development)
- [Testing](#testing)
- [Docker Deployment](#docker-deployment)
- [Production Deployment](#production-deployment)
- [CI/CD Pipeline](#cicd-pipeline)
- [Monitoring & Health Checks](#monitoring--health-checks)

## Prerequisites

### Required
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Docker & Docker Compose
- Git

### API Keys
- OpenAI API Key (for LLM, Whisper, TTS, Vision)

### Optional (Production)
- Kubernetes cluster
- Container registry (Docker Hub, GCR, ECR, etc.)
- Pinecone/Weaviate account (for production vector DB)

## Local Development

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local file
cp .env.example .env.local
# Edit .env.local: NEXT_PUBLIC_API_URL=http://localhost:8000

# Start development server
npm run dev
```

Visit http://localhost:3000

## Testing

### Backend Tests

```bash
cd backend

# Run all tests with coverage
pytest

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v

# Generate HTML coverage report
pytest --cov=app --cov-report=html
# View coverage: open htmlcov/index.html
```

### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Generate coverage report
npm run test:coverage
```

## Docker Deployment

### Using Docker Compose (Development)

```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Docker Build

```bash
# Build backend
docker build -f backend/Dockerfile.prod -t lifeai-backend:latest ./backend

# Build frontend
docker build -f frontend/Dockerfile.prod \
  --build-arg NEXT_PUBLIC_API_URL=https://api.youromain.com \
  -t lifeai-frontend:latest ./frontend

# Run backend
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@db:5432/lifeai \
  -e OPENAI_API_KEY=your-key \
  -e SECRET_KEY=your-secret \
  lifeai-backend:latest

# Run frontend
docker run -p 3000:3000 lifeai-frontend:latest
```

## Production Deployment

### Environment Variables

#### Backend (.env)
```env
# Database
DATABASE_URL=postgresql://user:pass@host:5432/lifeai

# Security
SECRET_KEY=your-very-secret-key-min-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# OpenAI
OPENAI_API_KEY=sk-...

# Vector Database (Production)
VECTOR_DB_TYPE=pinecone  # or weaviate, qdrant
PINECONE_API_KEY=...
PINECONE_ENVIRONMENT=...
PINECONE_INDEX_NAME=lifeai-embeddings

# CORS
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Environment
ENVIRONMENT=production
```

#### Frontend (.env.production)
```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

### Database Migrations

```bash
# In production, run migrations before deploying new code
cd backend
alembic upgrade head

# To create a new migration
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

### Kubernetes Deployment (Example)

```yaml
# backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: lifeai-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: lifeai-backend
  template:
    metadata:
      labels:
        app: lifeai-backend
    spec:
      containers:
      - name: backend
        image: your-registry/lifeai-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: lifeai-secrets
              key: database-url
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: lifeai-secrets
              key: openai-api-key
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: lifeai-backend
spec:
  selector:
    app: lifeai-backend
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

## CI/CD Pipeline

### GitHub Actions

The project includes two GitHub Actions workflows:

#### 1. CI/CD Pipeline (.github/workflows/ci-cd.yml)
Runs automatically on:
- Push to `main`, `develop`, or `claude/**` branches
- Pull requests to `main` or `develop`

**Jobs:**
- Backend tests with pytest
- Frontend tests with Jest
- Docker build validation
- Security scanning with Trivy

#### 2. Deployment (.github/workflows/deploy.yml)
Manual trigger with environment selection (staging/production)

**Required Secrets:**
- `OPENAI_API_KEY` - OpenAI API key
- `REGISTRY_URL` - Container registry URL
- `REGISTRY_USERNAME` - Registry username
- `REGISTRY_PASSWORD` - Registry password/token
- `API_URL` - Production API URL

### Setting up GitHub Secrets

1. Go to repository Settings > Secrets and variables > Actions
2. Add required secrets listed above

## Monitoring & Health Checks

### Health Endpoints

#### `/health/` - Basic Health Check
Returns service status, version, and timestamp.

```bash
curl http://localhost:8000/health/
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-19T10:30:00",
  "version": "2.1.0",
  "python_version": "3.11.0",
  "database": "connected"
}
```

#### `/health/ready` - Readiness Check
Checks if all dependencies are ready (database, APIs).

```bash
curl http://localhost:8000/health/ready
```

Response:
```json
{
  "ready": true,
  "checks": {
    "database": true,
    "openai_api": true
  }
}
```

#### `/health/live` - Liveness Check
Simple check to verify the process is alive.

```bash
curl http://localhost:8000/health/live
```

Response:
```json
{
  "status": "alive"
}
```

### Kubernetes Probes

```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 30
  timeoutSeconds: 3
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /health/ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10
  timeoutSeconds: 3
  failureThreshold: 3
```

### Logging

Backend uses Python's logging module with structured logs:

```python
import logging
logger = logging.getLogger(__name__)
logger.info("User registered", extra={"user_id": user.id, "email": user.email})
```

In production, configure log aggregation (ELK Stack, Cloud Logging, etc.).

### Monitoring Recommendations

1. **Application Metrics**
   - Prometheus + Grafana
   - Track: Request rate, error rate, response time, active users

2. **Error Tracking**
   - Sentry or similar
   - Automatic error reporting with context

3. **Database Monitoring**
   - Connection pool stats
   - Query performance
   - Slow query logs

4. **Infrastructure**
   - CPU, memory, disk usage
   - Network traffic
   - Pod/container status (if using Kubernetes)

## Scaling

### Horizontal Scaling

- Backend: Stateless design allows easy horizontal scaling
- Frontend: Static site generation with CDN
- Database: Use read replicas for read-heavy workloads

### Performance Optimization

1. **Caching**
   - Redis for session storage
   - CDN for static assets
   - Response caching for frequently accessed data

2. **Database**
   - Connection pooling
   - Query optimization
   - Indexes on frequently queried fields

3. **Vector Search**
   - Use production vector database (Pinecone/Weaviate)
   - Batch embedding generation
   - Cache frequently accessed embeddings

## Security Checklist

- [ ] Rotate SECRET_KEY regularly
- [ ] Use environment variables for secrets
- [ ] Enable HTTPS in production
- [ ] Set ALLOWED_ORIGINS correctly
- [ ] Regular security updates for dependencies
- [ ] Enable rate limiting
- [ ] Monitor for suspicious activity
- [ ] Regular backups of database
- [ ] Implement proper CORS policies

## Troubleshooting

### Common Issues

**Database connection errors:**
```bash
# Check database is running
docker-compose ps postgres

# Check connection string
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1"
```

**OpenAI API errors:**
```bash
# Verify API key is set
echo $OPENAI_API_KEY

# Test API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

**Port already in use:**
```bash
# Find process using port
lsof -i :8000  # or :3000

# Kill process
kill -9 <PID>
```

## Support

For issues and questions:
- GitHub Issues: https://github.com/Marksio90/LifeAI/issues
- Documentation: Check README.md and ARCHITECTURE.md
