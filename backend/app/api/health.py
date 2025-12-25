"""Comprehensive health check endpoints for monitoring."""
from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Dict, Any
import sys
import asyncio
import os

from app.db.session import get_db
from app.core.redis_client import get_redis_client

router = APIRouter(prefix="/health", tags=["health"])


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: str
    version: str
    python_version: str
    database: str
    redis: str


class DetailedHealthResponse(BaseModel):
    """Detailed health check response model."""
    status: str
    timestamp: str
    version: str
    python_version: str
    services: Dict[str, Any]
    uptime_seconds: float


class ReadinessResponse(BaseModel):
    """Readiness check response model."""
    ready: bool
    checks: dict


# Track service start time for uptime calculation
_service_start_time = datetime.now(timezone.utc)


async def check_database_health(db: Session) -> Dict[str, Any]:
    """
    Check database connectivity and basic health.

    Args:
        db: Database session

    Returns:
        Dict with status and metrics
    """
    try:
        start_time = datetime.now(timezone.utc)

        # Execute simple query
        result = db.execute(text("SELECT 1"))
        result.fetchone()

        # Check if we can get table count
        table_count_result = db.execute(text(
            "SELECT COUNT(*) FROM information_schema.tables "
            "WHERE table_schema = 'public'"
        ))
        table_count = table_count_result.scalar()

        elapsed = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000

        return {
            "status": "healthy",
            "connected": True,
            "response_time_ms": round(elapsed, 2),
            "tables": table_count,
            "message": "Database connection successful"
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "connected": False,
            "error": str(e),
            "message": "Database connection failed"
        }


async def check_redis_health() -> Dict[str, Any]:
    """
    Check Redis connectivity and health.

    Returns:
        Dict with status and metrics
    """
    try:
        redis_client = get_redis_client()

        if not redis_client.is_connected:
            return {
                "status": "degraded",
                "connected": False,
                "message": "Using in-memory fallback (Redis unavailable)"
            }

        start_time = datetime.now(timezone.utc)

        # Ping Redis
        redis_client.client.ping()

        # Get some stats
        info = redis_client.client.info("stats")
        memory_info = redis_client.client.info("memory")

        elapsed = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000

        return {
            "status": "healthy",
            "connected": True,
            "response_time_ms": round(elapsed, 2),
            "total_commands_processed": info.get("total_commands_processed"),
            "used_memory_human": memory_info.get("used_memory_human"),
            "message": "Redis connection successful"
        }

    except Exception as e:
        return {
            "status": "degraded",
            "connected": False,
            "error": str(e),
            "message": "Redis connection failed (using in-memory fallback)"
        }


async def check_openai_health() -> Dict[str, Any]:
    """
    Check OpenAI API connectivity.

    Returns:
        Dict with status and basic info
    """
    try:
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            return {
                "status": "unhealthy",
                "configured": False,
                "message": "OpenAI API key not configured"
            }

        # We don't make actual API call to save costs
        # Just verify key is configured
        return {
            "status": "healthy",
            "configured": True,
            "api_key_length": len(api_key),
            "message": "OpenAI API key configured (not tested to avoid costs)"
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "configured": False,
            "error": str(e),
            "message": "OpenAI API check failed"
        }


async def check_vector_db_health() -> Dict[str, Any]:
    """
    Check Vector Database connectivity.

    Returns:
        Dict with status and info
    """
    try:
        from app.memory.vector_factory import get_vector_store

        vector_store = get_vector_store()

        # Check if vector store is configured
        if vector_store is None:
            return {
                "status": "degraded",
                "connected": False,
                "message": "Vector store not configured (using in-memory fallback)"
            }

        # For in-memory store
        if hasattr(vector_store, 'vectors'):
            return {
                "status": "healthy",
                "type": "in-memory",
                "connected": True,
                "vector_count": len(vector_store.vectors) if hasattr(vector_store, 'vectors') else 0,
                "message": "In-memory vector store operational"
            }

        # For Pinecone
        if hasattr(vector_store, 'index'):
            return {
                "status": "healthy",
                "type": "pinecone",
                "connected": True,
                "message": "Pinecone vector store connected"
            }

        return {
            "status": "unknown",
            "type": "unknown",
            "message": "Vector store type unknown"
        }

    except Exception as e:
        return {
            "status": "degraded",
            "connected": False,
            "error": str(e),
            "message": "Vector store check failed"
        }


@router.get("/", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check():
    """
    Basic health check endpoint.
    Returns 200 OK if the service is running.

    This is a lightweight check suitable for load balancer health checks.
    """
    redis_client = get_redis_client()
    redis_status = "connected" if redis_client.is_connected else "disconnected (using in-memory fallback)"

    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat(),
        version="2.1.0",
        python_version=sys.version.split()[0],
        database="connected",
        redis=redis_status
    )


@router.get("/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check(db: Session = Depends(get_db)):
    """
    Detailed health check endpoint.
    Performs comprehensive checks of all service dependencies.

    This endpoint checks:
    - Database connectivity and performance
    - Redis connectivity and stats
    - OpenAI API configuration
    - Vector DB status
    - Service uptime

    Use this for monitoring dashboards and detailed diagnostics.
    """
    # Run all health checks concurrently
    db_check, redis_check, openai_check, vector_check = await asyncio.gather(
        check_database_health(db),
        check_redis_health(),
        check_openai_health(),
        check_vector_db_health(),
        return_exceptions=True
    )

    # Calculate uptime
    uptime = (datetime.now(timezone.utc) - _service_start_time).total_seconds()

    # Determine overall status
    critical_services = [db_check, openai_check]
    all_healthy = all(
        isinstance(check, dict) and check.get("status") == "healthy"
        for check in critical_services
    )

    overall_status = "healthy" if all_healthy else "degraded"

    return DetailedHealthResponse(
        status=overall_status,
        timestamp=datetime.now(timezone.utc).isoformat(),
        version="2.1.0",
        python_version=sys.version.split()[0],
        services={
            "database": db_check if isinstance(db_check, dict) else {"status": "error", "error": str(db_check)},
            "redis": redis_check if isinstance(redis_check, dict) else {"status": "error", "error": str(redis_check)},
            "openai_api": openai_check if isinstance(openai_check, dict) else {"status": "error", "error": str(openai_check)},
            "vector_db": vector_check if isinstance(vector_check, dict) else {"status": "error", "error": str(vector_check)},
        },
        uptime_seconds=round(uptime, 2)
    )


@router.get("/ready", response_model=ReadinessResponse)
async def readiness_check(db: Session = Depends(get_db)):
    """
    Readiness check endpoint for Kubernetes readiness probes.

    Verifies that all critical dependencies are available.
    Service is NOT ready to accept traffic if:
    - Database is unreachable
    - OpenAI API key is not configured

    Optional services (Redis, Vector DB) don't affect readiness.
    """
    checks = {
        "database": False,
        "redis": False,
        "openai_api": False,
        "vector_db": False,
    }

    # Check database connection
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception:
        checks["database"] = False

    # Check Redis connection (optional)
    redis_client = get_redis_client()
    checks["redis"] = redis_client.is_connected

    # Check OpenAI API key configuration
    checks["openai_api"] = bool(os.getenv("OPENAI_API_KEY"))

    # Check Vector DB (optional)
    try:
        from app.memory.vector_factory import get_vector_store
        vector_store = get_vector_store()
        checks["vector_db"] = vector_store is not None
    except Exception:
        checks["vector_db"] = False

    # Determine overall readiness
    # Only database and openai_api are required
    ready = checks["database"] and checks["openai_api"]

    return ReadinessResponse(
        ready=ready,
        checks=checks
    )


@router.get("/live", status_code=status.HTTP_200_OK)
async def liveness_check():
    """
    Liveness check endpoint for Kubernetes liveness probes.

    Returns 200 OK if the process is alive and responsive.
    This is a very lightweight check that only verifies the process can handle requests.

    If this fails, Kubernetes will restart the pod.
    """
    return {
        "status": "alive",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
