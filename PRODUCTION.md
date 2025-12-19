# LifeAI Production Deployment Guide

Complete guide for deploying LifeAI to production with PostgreSQL, Redis, and Pinecone.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Infrastructure Setup](#infrastructure-setup)
- [Secrets Management](#secrets-management)
- [Database Setup](#database-setup)
- [Vector Database (Pinecone)](#vector-database-pinecone)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Post-Deployment](#post-deployment)

## Prerequisites

### Required Services
- [x] PostgreSQL 15+ (production database)
- [x] Redis 7+ (caching and sessions)
- [x] Pinecone account (production vector database)
- [x] OpenAI API key
- [x] Domain name with SSL certificate

### Optional Services
- [ ] AWS Account (for Secrets Manager)
- [ ] Container Registry (Docker Hub, GCR, ECR)
- [ ] Kubernetes Cluster (EKS, GKE, AKS, or self-hosted)

## Infrastructure Setup

### 1. Pinecone Vector Database

Create a Pinecone account and index:

```bash
# 1. Sign up at https://www.pinecone.io
# 2. Create a new project
# 3. Create an index with these settings:
#    - Name: lifeai-embeddings
#    - Dimensions: 1536 (OpenAI text-embedding-3-small)
#    - Metric: cosine
#    - Cloud: AWS
#    - Region: us-east-1 (or your preferred region)
```

### 2. PostgreSQL Setup

#### Option A: Managed Database (Recommended)
Use a managed PostgreSQL service:
- AWS RDS
- Google Cloud SQL
- Azure Database for PostgreSQL
- DigitalOcean Managed Databases

#### Option B: Self-Hosted
```bash
# Using docker-compose.prod.yml
docker-compose -f docker-compose.prod.yml up -d postgres

# Or manual installation
sudo apt-get install postgresql-15
```

### 3. Redis Setup

#### Option A: Managed Redis (Recommended)
Use a managed Redis service:
- AWS ElastiCache
- Google Cloud Memorystore
- Azure Cache for Redis
- Redis Cloud

#### Option B: Self-Hosted
```bash
# Using docker-compose.prod.yml
docker-compose -f docker-compose.prod.yml up -d redis

# Or manual installation
sudo apt-get install redis-server
```

## Secrets Management

### Option 1: Environment Variables (Simple)

Create `.env.production` file:
```bash
cp .env.production.example .env.production
# Edit and fill in all values
nano .env.production
```

### Option 2: Docker Secrets (Docker Swarm)

```bash
# Create secrets
echo "your-secret-key" | docker secret create secret_key -
echo "your-db-password" | docker secret create postgres_password -
echo "sk-your-openai-key" | docker secret create openai_api_key -

# Secrets are automatically loaded from /run/secrets/
```

### Option 3: AWS Secrets Manager

```bash
# Install AWS CLI
pip install awscli boto3

# Configure credentials
aws configure

# Create secrets
aws secretsmanager create-secret \
  --name lifeai/production/database_url \
  --secret-string "postgresql://user:pass@host:5432/lifeai"

aws secretsmanager create-secret \
  --name lifeai/production/openai_api_key \
  --secret-string "sk-your-openai-api-key"

# Application will automatically fetch from AWS Secrets Manager
# when ENVIRONMENT=production
```

### Option 4: Kubernetes Secrets

```bash
# Create namespace
kubectl create namespace lifeai

# Create secrets
kubectl create secret generic lifeai-secrets \
  --from-literal=DATABASE_URL='postgresql://...' \
  --from-literal=SECRET_KEY='...' \
  --from-literal=OPENAI_API_KEY='sk-...' \
  --from-literal=PINECONE_API_KEY='...' \
  --namespace=lifeai

# Or from file
kubectl create secret generic lifeai-secrets \
  --from-env-file=.env.production \
  --namespace=lifeai
```

## Database Setup

### 1. Initialize Database

```bash
# Run initialization script
docker exec -i lifeai-postgres psql -U lifeai -d lifeai < backend/scripts/init-db.sql

# Or if using external database
psql $DATABASE_URL < backend/scripts/init-db.sql
```

### 2. Run Migrations

```bash
# Using Docker
docker exec lifeai-backend alembic upgrade head

# Or locally
cd backend
alembic upgrade head
```

### 3. Setup Backups

#### Automated Backups (Docker)
```bash
# Backup service runs automatically in docker-compose.prod.yml
# Backups are saved to ./backups/ directory
# Keeps last 7 days by default (configurable with BACKUP_KEEP_DAYS)

# Manual backup
docker exec lifeai-postgres pg_dump \
  -U lifeai -d lifeai --format=custom > backup.sql
```

#### Restore from Backup
```bash
# Make backup script executable
chmod +x backend/scripts/restore.sh

# Restore
docker exec -i lifeai-postgres /backups/restore.sh /backups/lifeai_backup_20231219_120000.sql.gz
```

## Vector Database (Pinecone)

### Setup

1. **Create Pinecone Index** (if not already created)
```python
import pinecone

pinecone.init(api_key="your-api-key", environment="us-east-1")

pinecone.create_index(
    name="lifeai-embeddings",
    dimension=1536,
    metric="cosine"
)
```

2. **Set Environment Variables**
```bash
VECTOR_DB_TYPE=pinecone
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=lifeai-embeddings
```

3. **Verify Connection**
```bash
# Check health endpoint
curl http://your-domain/health/ready

# Should show:
# {
#   "ready": true,
#   "checks": {
#     "database": true,
#     "openai_api": true
#   }
# }
```

### Migration from In-Memory to Pinecone

If you have existing data in in-memory vector store:

```python
# backend/scripts/migrate_vectors.py
import asyncio
from app.memory.in_memory_store import InMemoryVectorStore
from app.memory.pinecone_store import PineconeVectorStore

async def migrate():
    old_store = InMemoryVectorStore()
    new_store = PineconeVectorStore()

    # Get all documents from in-memory store
    documents = old_store.get_all_documents()

    # Upsert to Pinecone
    await new_store.upsert(documents)

    print(f"Migrated {len(documents)} documents to Pinecone")

if __name__ == "__main__":
    asyncio.run(migrate())
```

## Docker Deployment

### Production Deployment with Docker Compose

```bash
# 1. Clone repository
git clone https://github.com/Marksio90/LifeAI.git
cd LifeAI

# 2. Create .env.production file
cp .env.production.example .env.production
# Edit with your production values

# 3. Build and start services
docker-compose -f docker-compose.prod.yml up -d

# 4. Check logs
docker-compose -f docker-compose.prod.yml logs -f

# 5. Verify health
curl http://localhost:8000/health/
curl http://localhost:3000/
```

### Individual Service Management

```bash
# Start only database services
docker-compose -f docker-compose.prod.yml up -d postgres redis

# Run migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Start application services
docker-compose -f docker-compose.prod.yml up -d backend frontend

# Scale backend
docker-compose -f docker-compose.prod.yml up -d --scale backend=3
```

## Kubernetes Deployment

### 1. Prepare Cluster

```bash
# Create namespace
kubectl apply -f kubernetes/deployment.yaml

# This creates:
# - Namespace: lifeai
# - ConfigMap: lifeai-config
# - Secret: lifeai-secrets (UPDATE THIS!)
# - Deployments: postgres, redis, backend, frontend
# - Services: All services with LoadBalancers
# - HPA: Auto-scaling for backend
# - PVCs: Persistent storage
```

### 2. Update Secrets

```bash
# Edit the secrets in kubernetes/deployment.yaml
# Or create from file:
kubectl create secret generic lifeai-secrets \
  --from-env-file=.env.production \
  --namespace=lifeai \
  --dry-run=client -o yaml | kubectl apply -f -
```

### 3. Build and Push Images

```bash
# Login to your container registry
docker login your-registry.com

# Build images
docker build -f backend/Dockerfile.prod -t your-registry/lifeai-backend:v2.1.0 ./backend
docker build -f frontend/Dockerfile.prod -t your-registry/lifeai-frontend:v2.1.0 ./frontend

# Push images
docker push your-registry/lifeai-backend:v2.1.0
docker push your-registry/lifeai-frontend:v2.1.0

# Update deployment.yaml with your registry
# Then apply
kubectl apply -f kubernetes/deployment.yaml
```

### 4. Monitor Deployment

```bash
# Watch pods starting
kubectl get pods -n lifeai -w

# Check logs
kubectl logs -f deployment/backend -n lifeai
kubectl logs -f deployment/frontend -n lifeai

# Check services
kubectl get svc -n lifeai

# Get external IPs
kubectl get svc backend-service -n lifeai
kubectl get svc frontend-service -n lifeai
```

### 5. Setup Ingress (Optional)

```yaml
# kubernetes/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: lifeai-ingress
  namespace: lifeai
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - api.yourdomain.com
    - yourdomain.com
    secretName: lifeai-tls
  rules:
  - host: api.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 80
  - host: yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
```

## Post-Deployment

### 1. Verify Deployment

```bash
# Health checks
curl https://api.yourdomain.com/health/
curl https://api.yourdomain.com/health/ready

# API docs
open https://api.yourdomain.com/docs

# Frontend
open https://yourdomain.com
```

### 2. Setup Monitoring

```bash
# Using Prometheus + Grafana (example)
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring
```

### 3. Setup Logging

```bash
# Using ELK Stack or Cloud Logging
# Configure log aggregation based on your cloud provider
```

### 4. Setup Alerts

```yaml
# Example: Prometheus AlertManager rules
groups:
- name: lifeai
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
    for: 5m
    annotations:
      summary: "High error rate detected"

  - alert: DatabaseDown
    expr: up{job="postgres"} == 0
    for: 1m
    annotations:
      summary: "Database is down"
```

### 5. Security Hardening

- [ ] Enable firewall rules
- [ ] Configure SSL/TLS certificates
- [ ] Setup WAF (Web Application Firewall)
- [ ] Enable DDoS protection
- [ ] Configure rate limiting
- [ ] Regular security audits
- [ ] Dependency updates

### 6. Performance Optimization

```bash
# PostgreSQL optimization
# Edit postgresql.conf
max_connections = 100
shared_buffers = 2GB
effective_cache_size = 6GB
work_mem = 16MB

# Redis optimization
maxmemory 2gb
maxmemory-policy allkeys-lru

# Backend optimization
# Increase workers in Dockerfile.prod
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "8"]
```

## Troubleshooting

### Database Connection Issues
```bash
# Test connection
psql $DATABASE_URL -c "SELECT version();"

# Check logs
docker logs lifeai-postgres
kubectl logs deployment/postgres -n lifeai
```

### Vector DB Connection Issues
```bash
# Test Pinecone connection
python -c "
from pinecone import Pinecone
pc = Pinecone(api_key='your-key')
print(pc.list_indexes())
"
```

### Application Not Starting
```bash
# Check environment variables
docker exec lifeai-backend env | grep -E "DATABASE|OPENAI|PINECONE"

# Check logs
docker logs lifeai-backend
kubectl logs deployment/backend -n lifeai
```

## Maintenance

### Regular Tasks

**Daily:**
- Monitor error logs
- Check application health
- Verify backups completed

**Weekly:**
- Review security alerts
- Check disk usage
- Review performance metrics

**Monthly:**
- Update dependencies
- Security patches
- Database optimization
- Review and rotate secrets

### Scaling

```bash
# Docker Compose
docker-compose -f docker-compose.prod.yml up -d --scale backend=5

# Kubernetes (automatic with HPA)
kubectl get hpa -n lifeai

# Manual scaling
kubectl scale deployment backend --replicas=10 -n lifeai
```

## Support

For production issues:
- Check logs first
- Review DEPLOYMENT.md for common issues
- GitHub Issues: https://github.com/Marksio90/LifeAI/issues
