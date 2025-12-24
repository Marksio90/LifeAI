"""Response Caching Layer for LLM calls.

Reduces LLM API costs by caching responses based on user, message, and context.
Expected impact: 50-80% reduction in LLM calls for repeated queries.
"""

import hashlib
import json
import logging
from typing import Optional, Dict, Any
from datetime import timedelta

logger = logging.getLogger(__name__)


class ResponseCache:
    """Redis-based caching for LLM responses."""

    def __init__(self, redis_client, default_ttl: int = 3600):
        """
        Initialize response cache.

        Args:
            redis_client: Redis client instance
            default_ttl: Default time-to-live in seconds (1 hour)
        """
        self.redis = redis_client
        self.default_ttl = default_ttl
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0
        }

    def _generate_key(
        self,
        user_id: str,
        message: str,
        context_hash: str
    ) -> str:
        """
        Generate cache key based on user, message, and context.

        Uses SHA256 to create consistent, collision-resistant keys.
        Format: cache:response:{hash}

        Args:
            user_id: User identifier
            message: User message (normalized)
            context_hash: Hash of conversation context

        Returns:
            Cache key string
        """
        # Normalize message (lowercase, strip whitespace)
        normalized_message = message.lower().strip()

        # Create composite key
        content = f"{user_id}:{normalized_message}:{context_hash}"

        # Hash for consistent key length and security
        hash_digest = hashlib.sha256(content.encode()).hexdigest()

        return f"cache:response:{hash_digest}"

    def _hash_context(self, context: Dict[str, Any]) -> str:
        """
        Create hash of context dictionary.

        Args:
            context: Context dictionary (user preferences, recent history, etc.)

        Returns:
            MD5 hash of sorted context
        """
        # Sort keys for consistent hashing
        context_json = json.dumps(context, sort_keys=True)
        return hashlib.md5(context_json.encode()).hexdigest()

    async def get(
        self,
        user_id: str,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Get cached response if exists.

        Args:
            user_id: User identifier
            message: User message
            context: Optional context dictionary

        Returns:
            Cached response string or None if not found
        """
        try:
            # Generate context hash
            context_hash = self._hash_context(context or {})

            # Generate cache key
            key = self._generate_key(user_id, message, context_hash)

            # Try to get from Redis
            cached = await self.redis.get(key)

            if cached:
                self.stats["hits"] += 1
                logger.info(
                    f"Cache HIT for user {user_id[:8]}... "
                    f"(hit rate: {self.get_hit_rate():.2%})"
                )
                return json.loads(cached)

            self.stats["misses"] += 1
            logger.debug(f"Cache MISS for user {user_id[:8]}...")
            return None

        except Exception as e:
            logger.error(f"Error getting from cache: {e}")
            return None

    async def set(
        self,
        user_id: str,
        message: str,
        context: Optional[Dict[str, Any]],
        response: str,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Cache response.

        Args:
            user_id: User identifier
            message: User message
            context: Optional context dictionary
            response: LLM response to cache
            ttl: Optional time-to-live (seconds), defaults to default_ttl

        Returns:
            True if successfully cached, False otherwise
        """
        try:
            # Generate context hash
            context_hash = self._hash_context(context or {})

            # Generate cache key
            key = self._generate_key(user_id, message, context_hash)

            # Determine TTL
            expiry = ttl or self.default_ttl

            # Set in Redis with expiration
            await self.redis.setex(
                key,
                expiry,
                json.dumps(response)
            )

            self.stats["sets"] += 1
            logger.debug(
                f"Cached response for user {user_id[:8]}... "
                f"(TTL: {expiry}s)"
            )
            return True

        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            return False

    async def invalidate(
        self,
        user_id: str,
        message: Optional[str] = None
    ) -> int:
        """
        Invalidate cache entries.

        Args:
            user_id: User identifier
            message: Optional specific message to invalidate
                    If None, invalidates all user's cache

        Returns:
            Number of keys deleted
        """
        try:
            if message:
                # Invalidate specific message
                # Need to iterate through possible context hashes
                # This is expensive - better to just let TTL expire
                logger.warning(
                    "Specific message invalidation not fully supported. "
                    "Consider using shorter TTLs instead."
                )
                return 0
            else:
                # Invalidate all user cache
                pattern = f"cache:response:*{user_id}*"
                keys = await self.redis.keys(pattern)
                if keys:
                    deleted = await self.redis.delete(*keys)
                    logger.info(f"Invalidated {deleted} cache entries for user {user_id[:8]}...")
                    return deleted
                return 0

        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")
            return 0

    def get_hit_rate(self) -> float:
        """
        Calculate cache hit rate.

        Returns:
            Hit rate as float (0.0 to 1.0)
        """
        total = self.stats["hits"] + self.stats["misses"]
        if total == 0:
            return 0.0
        return self.stats["hits"] / total

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        return {
            **self.stats,
            "hit_rate": self.get_hit_rate(),
            "total_requests": self.stats["hits"] + self.stats["misses"]
        }

    async def clear_all(self) -> int:
        """
        Clear all cached responses.

        WARNING: This deletes ALL response cache entries.

        Returns:
            Number of keys deleted
        """
        try:
            pattern = "cache:response:*"
            keys = await self.redis.keys(pattern)
            if keys:
                deleted = await self.redis.delete(*keys)
                logger.warning(f"Cleared ALL cache: {deleted} keys deleted")
                return deleted
            return 0

        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return 0


# Convenience function for creating cache instance
def create_response_cache(redis_client, ttl: int = 3600) -> ResponseCache:
    """
    Create ResponseCache instance.

    Args:
        redis_client: Redis client
        ttl: Time-to-live in seconds (default: 1 hour)

    Returns:
        ResponseCache instance
    """
    return ResponseCache(redis_client, default_ttl=ttl)
