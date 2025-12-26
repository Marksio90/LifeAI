"""Debug endpoints for testing error tracking and monitoring."""
from fastapi import APIRouter, HTTPException, Depends
from app.core.config import get_settings
from app.monitoring.sentry import capture_exception, capture_message, set_user_context
import logging

router = APIRouter(prefix="/debug", tags=["debug"])
logger = logging.getLogger(__name__)


@router.get("/sentry-test")
async def test_sentry(settings = Depends(get_settings)):
    """
    Test Sentry integration by triggering an error.

    WARNING: Only use in development/staging environments!
    This endpoint intentionally raises an exception to verify Sentry is working.

    Returns:
        Never returns - always raises an exception
    """
    # Only allow in non-production environments
    if settings.environment == "production":
        raise HTTPException(
            status_code=403,
            detail="Debug endpoints are disabled in production"
        )

    # Capture a test message first
    event_id = capture_message(
        "Sentry test message triggered",
        level="info",
        context={"test": True}
    )
    logger.info(f"Test message sent to Sentry: {event_id}")

    # Now trigger an actual error
    try:
        # This will trigger a ZeroDivisionError
        result = 1 / 0
    except Exception as e:
        event_id = capture_exception(e, context={"endpoint": "sentry-test"})
        logger.error(f"Test exception captured in Sentry: {event_id}")
        raise HTTPException(
            status_code=500,
            detail=f"Sentry test successful! Event ID: {event_id}"
        )


@router.get("/sentry-message")
async def test_sentry_message(
    message: str = "Test message",
    level: str = "info",
    settings = Depends(get_settings)
):
    """
    Test Sentry message capture.

    Args:
        message: Message to send
        level: Message level (debug, info, warning, error, fatal)

    Returns:
        Event ID from Sentry
    """
    if settings.environment == "production":
        raise HTTPException(
            status_code=403,
            detail="Debug endpoints are disabled in production"
        )

    event_id = capture_message(message, level=level, context={"test": True})
    return {
        "status": "success",
        "event_id": event_id,
        "message": message,
        "level": level,
        "sentry_configured": bool(settings.sentry_dsn)
    }


@router.get("/sentry-user-context")
async def test_user_context(
    user_id: str = "test-user-123",
    email: str = "test@example.com",
    settings = Depends(get_settings)
):
    """
    Test Sentry user context tracking.

    Args:
        user_id: Test user ID
        email: Test email

    Returns:
        Confirmation with event ID
    """
    if settings.environment == "production":
        raise HTTPException(
            status_code=403,
            detail="Debug endpoints are disabled in production"
        )

    # Set user context
    set_user_context(user_id=user_id, email=email)

    # Capture a message with user context
    event_id = capture_message(
        f"User context test for {user_id}",
        level="info",
        context={"user_test": True}
    )

    return {
        "status": "success",
        "event_id": event_id,
        "user_id": user_id,
        "email": email,
        "message": "User context set and message captured"
    }
