"""Sentry error tracking integration."""
import logging
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from app.core.config import Settings

logger = logging.getLogger(__name__)


def init_sentry(settings: Settings) -> None:
    """
    Initialize Sentry error tracking.

    Args:
        settings: Application settings containing Sentry configuration

    Features:
        - Automatic error capture for FastAPI
        - SQLAlchemy query tracking
        - Redis command tracking
        - Log integration (WARNING and above)
        - Performance monitoring (traces)
        - User context tracking
        - Request/response data
    """
    if not settings.sentry_dsn:
        logger.info("Sentry DSN not configured, skipping initialization")
        return

    try:
        # Configure logging integration
        # Capture WARNING and above as breadcrumbs, ERROR+ as events
        sentry_logging = LoggingIntegration(
            level=logging.INFO,  # Breadcrumb level
            event_level=logging.ERROR  # Event level
        )

        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.sentry_environment,
            # Performance monitoring
            traces_sample_rate=settings.sentry_traces_sample_rate,
            profiles_sample_rate=settings.sentry_profiles_sample_rate,
            # Integrations
            integrations=[
                FastApiIntegration(transaction_style="endpoint"),
                SqlalchemyIntegration(),
                RedisIntegration(),
                sentry_logging,
            ],
            # Release tracking
            release=f"lifeai@{settings.app_version}",
            # Send default PII (Personally Identifiable Information)
            send_default_pii=False,  # Set to True if you want user IPs, etc.
            # Additional options
            before_send=before_send_filter,
            # Tag all events with service name
            tags={"service": "lifeai-backend"},
        )

        logger.info(
            f"Sentry initialized successfully - Environment: {settings.sentry_environment}, "
            f"Traces Sample Rate: {settings.sentry_traces_sample_rate}"
        )

    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}", exc_info=True)


def before_send_filter(event, hint):
    """
    Filter events before sending to Sentry.

    This allows you to:
    - Filter out sensitive data
    - Modify event data
    - Skip certain events
    - Add custom tags

    Args:
        event: The event dictionary
        hint: Contains the original exception

    Returns:
        Modified event or None to skip
    """
    # Example: Filter out specific exceptions
    if 'exc_info' in hint:
        exc_type, exc_value, tb = hint['exc_info']

        # Don't send HTTP 404 errors
        if hasattr(exc_value, 'status_code') and exc_value.status_code == 404:
            return None

        # Don't send specific known errors
        if isinstance(exc_value, (KeyboardInterrupt, SystemExit)):
            return None

    # Example: Remove sensitive data from request body
    if 'request' in event and 'data' in event['request']:
        # Remove password fields
        if isinstance(event['request']['data'], dict):
            for key in ['password', 'token', 'api_key']:
                if key in event['request']['data']:
                    event['request']['data'][key] = '[FILTERED]'

    # Example: Add custom tags
    if 'user' in event:
        event['tags'] = event.get('tags', {})
        event['tags']['user_authenticated'] = bool(event.get('user', {}).get('id'))

    return event


def capture_exception(error: Exception, context: dict = None) -> str:
    """
    Capture an exception and send to Sentry with context.

    Args:
        error: The exception to capture
        context: Additional context dictionary

    Returns:
        Event ID from Sentry

    Example:
        >>> try:
        ...     risky_operation()
        ... except Exception as e:
        ...     event_id = capture_exception(e, {
        ...         'user_id': user.id,
        ...         'operation': 'risky_operation'
        ...     })
        ...     logger.error(f"Error captured in Sentry: {event_id}")
    """
    with sentry_sdk.push_scope() as scope:
        if context:
            for key, value in context.items():
                scope.set_context(key, value)
        event_id = sentry_sdk.capture_exception(error)
        return event_id


def capture_message(message: str, level: str = "info", context: dict = None) -> str:
    """
    Capture a message and send to Sentry.

    Args:
        message: The message to capture
        level: Message level (debug, info, warning, error, fatal)
        context: Additional context dictionary

    Returns:
        Event ID from Sentry

    Example:
        >>> capture_message(
        ...     "User performed unusual action",
        ...     level="warning",
        ...     context={'user_id': user.id}
        ... )
    """
    with sentry_sdk.push_scope() as scope:
        if context:
            for key, value in context.items():
                scope.set_context(key, value)
        event_id = sentry_sdk.capture_message(message, level=level)
        return event_id


def set_user_context(user_id: str, email: str = None, username: str = None):
    """
    Set user context for Sentry events.

    This will attach user information to all subsequent events.

    Args:
        user_id: Unique user identifier
        email: User email (optional)
        username: Username (optional)

    Example:
        >>> from app.monitoring.sentry import set_user_context
        >>> set_user_context(
        ...     user_id=current_user.id,
        ...     email=current_user.email,
        ...     username=current_user.username
        ... )
    """
    sentry_sdk.set_user({
        "id": user_id,
        "email": email,
        "username": username
    })


def clear_user_context():
    """Clear user context (e.g., on logout)."""
    sentry_sdk.set_user(None)


def add_breadcrumb(message: str, category: str = "default", level: str = "info", data: dict = None):
    """
    Add a breadcrumb for debugging context.

    Breadcrumbs are a trail of events that happened before an error.

    Args:
        message: Breadcrumb message
        category: Category (e.g., "auth", "query", "ui")
        level: Level (debug, info, warning, error)
        data: Additional data dictionary

    Example:
        >>> add_breadcrumb(
        ...     "User logged in",
        ...     category="auth",
        ...     data={'method': 'email'}
        ... )
    """
    sentry_sdk.add_breadcrumb(
        message=message,
        category=category,
        level=level,
        data=data or {}
    )
