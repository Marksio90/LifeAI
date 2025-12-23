"""
Prometheus middleware for FastAPI to automatically collect HTTP metrics.
"""
import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from app.monitoring.metrics import http_requests_total, http_request_duration_seconds

logger = logging.getLogger(__name__)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """
    Middleware to collect Prometheus metrics for all HTTP requests.

    Automatically tracks:
    - Request count by method, endpoint, and status
    - Request duration by method and endpoint
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        logger.info("✅ Prometheus middleware initialized")

    async def dispatch(self, request: Request, call_next):
        """Process request and collect metrics."""
        # Start timer
        start_time = time.time()

        # Get endpoint path (without query params)
        path = request.url.path
        method = request.method

        # Process request
        try:
            response: Response = await call_next(request)
            status_code = response.status_code

        except Exception as e:
            # Track errors
            status_code = 500
            logger.error(f"Request failed: {e}")
            raise

        finally:
            # Calculate duration
            duration = time.time() - start_time

            # Record metrics
            http_requests_total.labels(
                method=method,
                endpoint=path,
                status=status_code
            ).inc()

            http_request_duration_seconds.labels(
                method=method,
                endpoint=path
            ).observe(duration)

        return response
