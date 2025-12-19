from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request


# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


# Rate limit configurations
FREE_USER_RATE_LIMIT = "20/hour"  # Free users: 20 requests per hour
PREMIUM_USER_RATE_LIMIT = "200/hour"  # Premium users: 200 requests per hour
MULTIMODAL_RATE_LIMIT = "10/hour"  # Multimodal endpoints (expensive)


def get_rate_limit_for_user(request: Request) -> str:
    """
    Get rate limit based on user subscription.

    Args:
        request: FastAPI request

    Returns:
        Rate limit string
    """
    # TODO: Check user subscription status from request
    # For now, return default free user limit
    return FREE_USER_RATE_LIMIT
