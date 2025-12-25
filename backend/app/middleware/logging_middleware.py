"""Structured logging middleware with correlation IDs and request tracking."""
import logging
import time
import uuid
import json
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class StructuredLogger:
    """
    Structured logger that outputs JSON formatted logs.
    Perfect for log aggregation systems like ELK, Loki, Datadog.
    """

    @staticmethod
    def log(
        level: str,
        message: str,
        correlation_id: str = None,
        **extra_fields
    ):
        """
        Log structured message with additional fields.

        Args:
            level: Log level (info, warning, error, etc.)
            message: Log message
            correlation_id: Optional correlation ID
            **extra_fields: Additional fields to include
        """
        log_entry = {
            "timestamp": time.time(),
            "level": level.upper(),
            "message": message,
            "correlation_id": correlation_id,
            **extra_fields
        }

        # Remove None values
        log_entry = {k: v for k, v in log_entry.items() if v is not None}

        # Log as JSON
        log_json = json.dumps(log_entry)

        if level == "error":
            logger.error(log_json)
        elif level == "warning":
            logger.warning(log_json)
        elif level == "debug":
            logger.debug(log_json)
        else:
            logger.info(log_json)


class CorrelationIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds correlation IDs to all requests for distributed tracing.

    Features:
    - Generates unique ID for each request
    - Propagates ID through request lifecycle
    - Adds ID to response headers
    - Enables request tracing across services
    - Structured logging with correlation context
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.structured_logger = StructuredLogger()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with correlation ID tracking.

        Args:
            request: Incoming request
            call_next: Next middleware/handler

        Returns:
            Response with correlation ID header
        """
        # Generate or extract correlation ID
        correlation_id = request.headers.get(
            'X-Correlation-ID',
            str(uuid.uuid4())
        )

        # Add to request state for access in endpoints
        request.state.correlation_id = correlation_id

        # Start timing
        start_time = time.time()

        # Log request start
        self.structured_logger.log(
            level="info",
            message="Request started",
            correlation_id=correlation_id,
            method=request.method,
            path=request.url.path,
            query_params=str(request.query_params),
            client_ip=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent", "unknown")
        )

        # Process request
        try:
            response = await call_next(request)

            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log request completion
            self.structured_logger.log(
                level="info",
                message="Request completed",
                correlation_id=correlation_id,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2)
            )

            # Add correlation ID to response headers
            response.headers['X-Correlation-ID'] = correlation_id

            # Add performance headers
            response.headers['X-Response-Time'] = f"{duration_ms:.2f}ms"

            return response

        except Exception as e:
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log error
            self.structured_logger.log(
                level="error",
                message="Request failed",
                correlation_id=correlation_id,
                method=request.method,
                path=request.url.path,
                error=str(e),
                error_type=type(e).__name__,
                duration_ms=round(duration_ms, 2)
            )

            raise


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """
    Middleware for performance monitoring and metrics collection.

    Tracks:
    - Response times per endpoint
    - Request counts
    - Error rates
    - Slow queries (>1s)
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.structured_logger = StructuredLogger()
        self.slow_request_threshold = 1000  # ms

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Monitor request performance.

        Args:
            request: Incoming request
            call_next: Next middleware/handler

        Returns:
            Response with performance metrics
        """
        start_time = time.time()
        correlation_id = getattr(request.state, 'correlation_id', None)

        try:
            response = await call_next(request)
            duration_ms = (time.time() - start_time) * 1000

            # Log slow requests
            if duration_ms > self.slow_request_threshold:
                self.structured_logger.log(
                    level="warning",
                    message="Slow request detected",
                    correlation_id=correlation_id,
                    method=request.method,
                    path=request.url.path,
                    duration_ms=round(duration_ms, 2),
                    threshold_ms=self.slow_request_threshold,
                    status_code=response.status_code
                )

            # Add performance metrics to response
            response.headers['X-Performance-Category'] = self._categorize_performance(duration_ms)

            return response

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            # Log error with performance context
            self.structured_logger.log(
                level="error",
                message="Request error",
                correlation_id=correlation_id,
                method=request.method,
                path=request.url.path,
                duration_ms=round(duration_ms, 2),
                error=str(e),
                error_type=type(e).__name__
            )

            raise

    @staticmethod
    def _categorize_performance(duration_ms: float) -> str:
        """Categorize request performance."""
        if duration_ms < 100:
            return "excellent"
        elif duration_ms < 500:
            return "good"
        elif duration_ms < 1000:
            return "acceptable"
        elif duration_ms < 3000:
            return "slow"
        else:
            return "very-slow"


# Helper function to get correlation ID in endpoints
def get_correlation_id(request: Request) -> str:
    """
    Get correlation ID from request state.

    Usage in endpoints:
    ```python
    @router.get("/example")
    async def example(request: Request):
        correlation_id = get_correlation_id(request)
        logger.info(f"Processing request {correlation_id}")
    ```

    Args:
        request: FastAPI request object

    Returns:
        Correlation ID string
    """
    return getattr(request.state, 'correlation_id', 'no-correlation-id')


# Export structured logger for use in other modules
structured_logger = StructuredLogger()
