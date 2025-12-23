"""
Prometheus metrics endpoint.
"""
from fastapi import APIRouter, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from app.monitoring.metrics import active_sessions, redis_connection_status, vector_db_documents_total
from app.core.session_store import get_session_store
from app.core.redis_client import get_redis_client
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("")
async def metrics():
    """
    Prometheus metrics endpoint.

    This endpoint exposes all collected metrics in Prometheus format
    for scraping by Prometheus server.

    Returns:
        Response with metrics in Prometheus text format
    """
    # Update gauge metrics before exposing
    try:
        # Update session count
        session_store = get_session_store()
        stats = session_store.get_stats()
        active_sessions.set(stats.get('memory_sessions', 0))

        # Update Redis connection status
        redis_client = get_redis_client()
        redis_connection_status.set(1 if redis_client.is_connected else 0)

        # TODO: Update vector DB document count
        # This would require adding a count method to vector store
        # vector_db_documents_total.set(vector_store.count())

    except Exception as e:
        logger.error(f"Error updating gauge metrics: {e}")

    # Generate metrics in Prometheus format
    metrics_output = generate_latest()

    return Response(
        content=metrics_output,
        media_type=CONTENT_TYPE_LATEST
    )
