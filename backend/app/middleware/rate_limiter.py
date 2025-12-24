"""Advanced Rate Limiting with Redis Sliding Window Algorithm.

Implements sophisticated rate limiting with:
- Sliding window algorithm (more accurate than fixed window)
- Per-user and per-IP limiting
- Multiple time windows (second, minute, hour, day)
- Burst allowance
- Dynamic rate limits based on user tier
- Rate limit headers in responses
"""

import time
import logging
from typing import Optional, Tuple
from datetime import datetime, timedelta
import hashlib

import redis.asyncio as redis
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RateLimitConfig:
    """Rate limit configuration for different tiers."""

    # Free tier limits
    FREE_TIER = {
        "requests_per_second": 5,
        "requests_per_minute": 60,
        "requests_per_hour": 500,
        "requests_per_day": 2000,
        "burst_allowance": 10
    }

    # Premium tier limits
    PREMIUM_TIER = {
        "requests_per_second": 20,
        "requests_per_minute": 300,
        "requests_per_hour": 5000,
        "requests_per_day": 50000,
        "burst_allowance": 50
    }

    # Admin tier (unlimited)
    ADMIN_TIER = {
        "requests_per_second": 1000,
        "requests_per_minute": 10000,
        "requests_per_hour": 100000,
        "requests_per_day": 1000000,
        "burst_allowance": 200
    }


class SlidingWindowRateLimiter:
    """
    Advanced rate limiter using Redis sliding window algorithm.

    More accurate than fixed window counters, prevents burst attacks
    at window boundaries.
    """

    def __init__(self, redis_client: redis.Redis):
        """
        Initialize rate limiter.

        Args:
            redis_client: Redis client instance
        """
        self.redis = redis_client
        logger.info("SlidingWindowRateLimiter initialized")

    async def check_rate_limit(
        self,
        identifier: str,
        limit: int,
        window_seconds: int,
        burst_allowance: int = 0
    ) -> Tuple[bool, dict]:
        """
        Check if request is within rate limit using sliding window.

        Args:
            identifier: Unique identifier (user ID or IP)
            limit: Maximum requests allowed in window
            window_seconds: Time window in seconds
            burst_allowance: Additional requests allowed for bursts

        Returns:
            Tuple of (allowed: bool, info: dict)
        """
        now = time.time()
        window_start = now - window_seconds

        # Redis key
        key = f"ratelimit:{identifier}:{window_seconds}"

        try:
            # Use Redis sorted set for sliding window
            pipe = self.redis.pipeline()

            # Remove old entries outside window
            pipe.zremrangebyscore(key, 0, window_start)

            # Count requests in current window
            pipe.zcard(key)

            # Add current request
            pipe.zadd(key, {str(now): now})

            # Set expiration
            pipe.expire(key, window_seconds * 2)

            results = await pipe.execute()

            # Get current count (before adding new request)
            current_count = results[1]

            # Check if limit exceeded
            effective_limit = limit + burst_allowance
            allowed = current_count < effective_limit

            # Calculate remaining and reset time
            remaining = max(0, effective_limit - current_count - 1)
            reset_time = int(now + window_seconds)

            info = {
                "limit": limit,
                "remaining": remaining,
                "reset": reset_time,
                "current": current_count + 1,
                "window_seconds": window_seconds,
                "burst_allowance": burst_allowance
            }

            if not allowed:
                logger.warning(
                    f"Rate limit exceeded for {identifier}: "
                    f"{current_count}/{effective_limit} in {window_seconds}s"
                )

            return allowed, info

        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            # On error, allow request (fail open)
            return True, {
                "limit": limit,
                "remaining": limit,
                "reset": int(now + window_seconds),
                "error": str(e)
            }

    async def check_multi_window(
        self,
        identifier: str,
        tier_config: dict
    ) -> Tuple[bool, dict]:
        """
        Check rate limits across multiple time windows.

        Args:
            identifier: Unique identifier
            tier_config: Configuration dict with limits

        Returns:
            Tuple of (allowed: bool, most_restrictive_info: dict)
        """
        windows = [
            ("second", 1, tier_config["requests_per_second"]),
            ("minute", 60, tier_config["requests_per_minute"]),
            ("hour", 3600, tier_config["requests_per_hour"]),
            ("day", 86400, tier_config["requests_per_day"]),
        ]

        burst = tier_config.get("burst_allowance", 0)

        # Check all windows
        for window_name, window_seconds, limit in windows:
            allowed, info = await self.check_rate_limit(
                identifier,
                limit,
                window_seconds,
                burst
            )

            if not allowed:
                info["window"] = window_name
                return False, info

        # All windows passed
        # Return info from minute window (most relevant)
        _, info = await self.check_rate_limit(
            identifier,
            tier_config["requests_per_minute"],
            60,
            burst
        )
        info["window"] = "minute"

        return True, info

    async def get_rate_limit_info(
        self,
        identifier: str,
        window_seconds: int
    ) -> dict:
        """
        Get current rate limit status without incrementing.

        Args:
            identifier: Unique identifier
            window_seconds: Time window

        Returns:
            Rate limit info dict
        """
        now = time.time()
        window_start = now - window_seconds
        key = f"ratelimit:{identifier}:{window_seconds}"

        try:
            # Count without modifying
            count = await self.redis.zcount(key, window_start, now)

            return {
                "current": count,
                "window_seconds": window_seconds,
                "timestamp": now
            }

        except Exception as e:
            logger.error(f"Error getting rate limit info: {e}")
            return {"error": str(e)}


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware for automatic rate limiting of HTTP requests.

    Features:
    - Per-user rate limiting (authenticated)
    - Per-IP rate limiting (anonymous)
    - Multiple time windows
    - Rate limit headers
    - Custom responses
    """

    def __init__(
        self,
        app,
        redis_url: str = "redis://localhost:6379",
        enabled: bool = True
    ):
        """
        Initialize rate limit middleware.

        Args:
            app: FastAPI application
            redis_url: Redis connection URL
            enabled: Whether rate limiting is enabled
        """
        super().__init__(app)

        self.enabled = enabled

        if self.enabled:
            # Initialize Redis
            self.redis = redis.from_url(
                redis_url,
                encoding="utf-8",
                decode_responses=False
            )

            self.limiter = SlidingWindowRateLimiter(self.redis)

            logger.info(f"Rate limiting enabled (Redis: {redis_url})")
        else:
            logger.info("Rate limiting disabled")

    async def dispatch(self, request: Request, call_next):
        """
        Process request with rate limiting.

        Args:
            request: Incoming request
            call_next: Next middleware/handler

        Returns:
            Response with rate limit headers
        """
        if not self.enabled:
            return await call_next(request)

        # Skip rate limiting for certain paths
        if self._should_skip(request):
            return await call_next(request)

        # Get identifier (user ID or IP)
        identifier = await self._get_identifier(request)

        # Get tier configuration
        tier_config = await self._get_tier_config(request)

        # Check rate limit
        allowed, info = await self.limiter.check_multi_window(
            identifier,
            tier_config
        )

        # Add rate limit headers
        headers = {
            "X-RateLimit-Limit": str(info["limit"]),
            "X-RateLimit-Remaining": str(info["remaining"]),
            "X-RateLimit-Reset": str(info["reset"]),
            "X-RateLimit-Window": info.get("window", "minute")
        }

        if not allowed:
            # Rate limit exceeded
            retry_after = info["reset"] - int(time.time())

            logger.warning(
                f"Rate limit exceeded for {identifier} "
                f"(window: {info.get('window')}, "
                f"limit: {info['limit']}, "
                f"current: {info['current']})"
            )

            return HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Please try again in {retry_after} seconds.",
                    "retry_after": retry_after,
                    **info
                },
                headers={
                    **headers,
                    "Retry-After": str(retry_after)
                }
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers to response
        for key, value in headers.items():
            response.headers[key] = value

        return response

    def _should_skip(self, request: Request) -> bool:
        """
        Check if request should skip rate limiting.

        Args:
            request: Incoming request

        Returns:
            True if should skip
        """
        skip_paths = [
            "/health",
            "/metrics",
            "/docs",
            "/openapi.json",
            "/static"
        ]

        return any(request.url.path.startswith(path) for path in skip_paths)

    async def _get_identifier(self, request: Request) -> str:
        """
        Get unique identifier for rate limiting.

        Args:
            request: Incoming request

        Returns:
            Unique identifier (user ID or hashed IP)
        """
        # Try to get user ID from request state (set by auth middleware)
        user_id = getattr(request.state, "user_id", None)

        if user_id:
            return f"user:{user_id}"

        # Fall back to IP address
        ip = request.client.host if request.client else "unknown"

        # Hash IP for privacy
        ip_hash = hashlib.sha256(ip.encode()).hexdigest()[:16]

        return f"ip:{ip_hash}"

    async def _get_tier_config(self, request: Request) -> dict:
        """
        Get rate limit configuration for request.

        Args:
            request: Incoming request

        Returns:
            Tier configuration dict
        """
        # Check user tier (from request state)
        is_premium = getattr(request.state, "is_premium", False)
        is_admin = getattr(request.state, "is_admin", False)

        if is_admin:
            return RateLimitConfig.ADMIN_TIER
        elif is_premium:
            return RateLimitConfig.PREMIUM_TIER
        else:
            return RateLimitConfig.FREE_TIER


# Utility functions for manual rate limiting

async def check_custom_rate_limit(
    redis_client: redis.Redis,
    identifier: str,
    limit: int,
    window_seconds: int
) -> Tuple[bool, dict]:
    """
    Check custom rate limit.

    Args:
        redis_client: Redis client
        identifier: Unique identifier
        limit: Request limit
        window_seconds: Time window

    Returns:
        Tuple of (allowed: bool, info: dict)
    """
    limiter = SlidingWindowRateLimiter(redis_client)
    return await limiter.check_rate_limit(identifier, limit, window_seconds)


def create_rate_limit_key(prefix: str, identifier: str, window: str) -> str:
    """
    Create standardized rate limit key.

    Args:
        prefix: Key prefix
        identifier: Identifier
        window: Time window name

    Returns:
        Redis key
    """
    return f"ratelimit:{prefix}:{identifier}:{window}"
