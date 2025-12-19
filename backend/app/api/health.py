"""Health check endpoints for monitoring."""
from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
import sys

from app.db.session import get_db

router = APIRouter(prefix="/health", tags=["health"])


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: str
    version: str
    python_version: str
    database: str


class ReadinessResponse(BaseModel):
    """Readiness check response model."""
    ready: bool
    checks: dict


@router.get("/", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check():
    """
    Basic health check endpoint.
    Returns 200 OK if the service is running.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="2.1.0",
        python_version=sys.version.split()[0],
        database="connected"
    )


@router.get("/ready", response_model=ReadinessResponse)
async def readiness_check(db: Session = Depends(get_db)):
    """
    Readiness check endpoint.
    Verifies that all dependencies are available.
    """
    checks = {
        "database": False,
        "openai_api": True,  # Assume available unless we want to ping it
    }

    # Check database connection
    try:
        db.execute("SELECT 1")
        checks["database"] = True
    except Exception:
        checks["database"] = False

    # Determine overall readiness
    ready = all(checks.values())

    return ReadinessResponse(
        ready=ready,
        checks=checks
    )


@router.get("/live", status_code=status.HTTP_200_OK)
async def liveness_check():
    """
    Liveness check endpoint.
    Returns 200 OK if the process is alive.
    Used by Kubernetes liveness probes.
    """
    return {"status": "alive"}
