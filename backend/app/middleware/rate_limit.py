"""Rate limiting middleware using Redis."""
import logging
import time
from typing import Optional, Callable
from fastapi import Request, HTTPException, status
from functools import wraps
import redis
import os

logger = logging.getLogger(__name__)

# Initialize Redis client
redis_client = redis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    decode_responses=True
)


class RateLimiter:
    """Redis-based rate limiter."""
    
    def __init__(
        self,
        calls: int,
        period: int,
        scope: str = "default"
    ):
        """
        Initialize rate limiter.
        
        Args:
            calls: Number of allowed calls
            period: Time period in seconds
            scope: Scope identifier (e.g., "login", "chat")
        """
        self.calls = calls
        self.period = period
        self.scope = scope
    
    def _get_identifier(self, request: Request) -> str:
        """
        Get unique identifier for rate limiting.
        
        Uses IP address or user ID if authenticated.
        """
        # Try to get user ID from request state (set by auth middleware)
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"user:{user_id}"
        
        # Fall back to IP address
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"
        
        return f"ip:{ip}"
    
    def _check_rate_limit(self, identifier: str) -> tuple[bool, Optional[int]]:
        """
        Check if request is within rate limit.
        
        Returns:
            (is_allowed, retry_after_seconds)
        """
        key = f"ratelimit:{self.scope}:{identifier}"
        
        try:
            # Get current count
            current = redis_client.get(key)
            
            if current is None:
                # First request in this period
                redis_client.setex(key, self.period, 1)
                return True, None
            
            current_count = int(current)
            
            if current_count < self.calls:
                # Still within limit
                redis_client.incr(key)
                return True, None
            
            # Rate limit exceeded
            ttl = redis_client.ttl(key)
            retry_after = max(1, ttl)  # At least 1 second
            
            logger.warning(
                f"Rate limit exceeded for {identifier} on {self.scope}. "
                f"Retry after {retry_after}s"
            )
            
            return False, retry_after
        
        except redis.RedisError as e:
            logger.error(f"Redis error in rate limiter: {e}")
            # On Redis error, allow request (fail open)
            return True, None
    
    async def __call__(self, request: Request):
        """Dependency for FastAPI endpoints."""
        identifier = self._get_identifier(request)
        is_allowed, retry_after = self._check_rate_limit(identifier)
        
        if not is_allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Try again in {retry_after} seconds.",
                headers={"Retry-After": str(retry_after)}
            )


# Pre-configured rate limiters for common use cases
login_limiter = RateLimiter(calls=5, period=900, scope="login")  # 5 per 15 min
chat_limiter = RateLimiter(calls=60, period=60, scope="chat")  # 60 per minute
multimodal_limiter = RateLimiter(calls=20, period=60, scope="multimodal")  # 20 per minute
api_limiter = RateLimiter(calls=100, period=60, scope="api")  # 100 per minute (general)
