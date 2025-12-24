"""Structured Logging Configuration for LifeAI.

Provides JSON-formatted logging with request tracking, performance metrics,
and integration with monitoring systems.
"""

import logging
import sys
import json
import traceback
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import os

from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter that adds additional context to log records.

    Includes:
    - Timestamp in ISO format
    - Request ID for tracing
    - User ID for attribution
    - Environment information
    - Performance metrics
    """

    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]):
        """Add custom fields to log record."""
        super().add_fields(log_record, record, message_dict)

        # Add timestamp
        log_record['timestamp'] = datetime.utcnow().isoformat()

        # Add log level
        log_record['level'] = record.levelname

        # Add logger name
        log_record['logger'] = record.name

        # Add module and function
        log_record['module'] = record.module
        log_record['function'] = record.funcName
        log_record['line'] = record.lineno

        # Add environment
        log_record['environment'] = os.getenv('ENVIRONMENT', 'development')

        # Add request context if available
        if hasattr(record, 'request_id'):
            log_record['request_id'] = record.request_id

        if hasattr(record, 'user_id'):
            log_record['user_id'] = record.user_id

        if hasattr(record, 'session_id'):
            log_record['session_id'] = record.session_id

        # Add performance metrics if available
        if hasattr(record, 'duration_ms'):
            log_record['duration_ms'] = record.duration_ms

        if hasattr(record, 'status_code'):
            log_record['status_code'] = record.status_code

        # Add exception info if present
        if record.exc_info:
            log_record['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }

        # Add extra fields
        if hasattr(record, 'extra_data'):
            log_record['extra'] = record.extra_data


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    enable_console: bool = True,
    enable_json: bool = True
) -> None:
    """
    Configure structured logging for the application.

    Args:
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for log output
        enable_console: Whether to log to console
        enable_json: Whether to use JSON formatting
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    root_logger.handlers = []

    # Create formatter
    if enable_json:
        formatter = CustomJsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # File handler
    if log_file:
        # Create log directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Set library log levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    logging.info(
        "Logging configured",
        extra={
            'extra_data': {
                'log_level': log_level,
                'enable_console': enable_console,
                'enable_json': enable_json,
                'log_file': log_file
            }
        }
    )


class StructuredLogger:
    """
    Wrapper for structured logging with additional context.

    Provides convenience methods for logging with consistent structure
    and automatic context injection.
    """

    def __init__(self, name: str):
        """
        Initialize structured logger.

        Args:
            name: Logger name (usually module name)
        """
        self.logger = logging.getLogger(name)
        self.context: Dict[str, Any] = {}

    def set_context(self, **kwargs):
        """Set context that will be included in all log messages."""
        self.context.update(kwargs)

    def clear_context(self):
        """Clear all context."""
        self.context = {}

    def _log(
        self,
        level: int,
        message: str,
        exc_info: bool = False,
        **kwargs
    ):
        """Internal logging method with context."""
        extra_data = {**self.context, **kwargs}

        self.logger.log(
            level,
            message,
            exc_info=exc_info,
            extra={'extra_data': extra_data}
        )

    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self._log(logging.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs):
        """Log info message."""
        self._log(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self._log(logging.WARNING, message, **kwargs)

    def error(self, message: str, exc_info: bool = False, **kwargs):
        """Log error message."""
        self._log(logging.ERROR, message, exc_info=exc_info, **kwargs)

    def critical(self, message: str, exc_info: bool = False, **kwargs):
        """Log critical message."""
        self._log(logging.CRITICAL, message, exc_info=exc_info, **kwargs)

    def exception(self, message: str, **kwargs):
        """Log exception with traceback."""
        self._log(logging.ERROR, message, exc_info=True, **kwargs)

    def log_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        user_id: Optional[str] = None,
        **kwargs
    ):
        """
        Log HTTP request.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path
            status_code: Response status code
            duration_ms: Request duration in milliseconds
            user_id: Optional user ID
            **kwargs: Additional context
        """
        self.info(
            f"{method} {path} {status_code}",
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=duration_ms,
            user_id=user_id,
            **kwargs
        )

    def log_database_query(
        self,
        query_type: str,
        duration_ms: float,
        table: Optional[str] = None,
        rows_affected: Optional[int] = None,
        **kwargs
    ):
        """
        Log database query.

        Args:
            query_type: Type of query (SELECT, INSERT, UPDATE, DELETE)
            duration_ms: Query duration in milliseconds
            table: Optional table name
            rows_affected: Optional number of rows affected
            **kwargs: Additional context
        """
        self.debug(
            f"Database query: {query_type}",
            query_type=query_type,
            duration_ms=duration_ms,
            table=table,
            rows_affected=rows_affected,
            **kwargs
        )

    def log_llm_call(
        self,
        model: str,
        duration_ms: float,
        tokens_used: int,
        cost: Optional[float] = None,
        **kwargs
    ):
        """
        Log LLM API call.

        Args:
            model: Model name
            duration_ms: Call duration in milliseconds
            tokens_used: Number of tokens used
            cost: Optional cost in USD
            **kwargs: Additional context
        """
        self.info(
            f"LLM call: {model}",
            model=model,
            duration_ms=duration_ms,
            tokens_used=tokens_used,
            cost=cost,
            **kwargs
        )

    def log_cache_operation(
        self,
        operation: str,
        key: str,
        hit: bool,
        duration_ms: Optional[float] = None,
        **kwargs
    ):
        """
        Log cache operation.

        Args:
            operation: Operation type (GET, SET, DELETE)
            key: Cache key
            hit: Whether it was a cache hit
            duration_ms: Optional operation duration
            **kwargs: Additional context
        """
        self.debug(
            f"Cache {operation}: {key} ({'HIT' if hit else 'MISS'})",
            operation=operation,
            key=key,
            hit=hit,
            duration_ms=duration_ms,
            **kwargs
        )

    def log_user_action(
        self,
        user_id: str,
        action: str,
        resource: Optional[str] = None,
        success: bool = True,
        **kwargs
    ):
        """
        Log user action for audit trail.

        Args:
            user_id: User identifier
            action: Action performed
            resource: Optional resource affected
            success: Whether action succeeded
            **kwargs: Additional context
        """
        self.info(
            f"User action: {action}",
            user_id=user_id,
            action=action,
            resource=resource,
            success=success,
            **kwargs
        )


def get_logger(name: str) -> StructuredLogger:
    """
    Get a structured logger instance.

    Args:
        name: Logger name (usually __name__)

    Returns:
        StructuredLogger instance
    """
    return StructuredLogger(name)


# Example usage
if __name__ == "__main__":
    # Setup logging
    setup_logging(
        log_level="DEBUG",
        log_file="logs/app.log",
        enable_json=True
    )

    # Create logger
    logger = get_logger(__name__)

    # Log various events
    logger.info("Application started", version="1.0.0")

    logger.set_context(request_id="req-123", user_id="user-456")

    logger.log_request(
        method="POST",
        path="/api/chat/message",
        status_code=200,
        duration_ms=125.5
    )

    logger.log_llm_call(
        model="gpt-4",
        duration_ms=1500.0,
        tokens_used=350,
        cost=0.0105
    )

    logger.log_cache_operation(
        operation="GET",
        key="user:456:preferences",
        hit=True,
        duration_ms=2.5
    )

    try:
        raise ValueError("Test error")
    except Exception:
        logger.exception("An error occurred during processing")

    logger.clear_context()
