"""LLM Response Cache using Redis for semantic caching."""
import hashlib
import json
import logging
from typing import Optional, List, Dict, Any
import redis
import os

logger = logging.getLogger(__name__)


class LLMCache:
    """
    Cache for LLM responses with semantic similarity support.

    This cache stores LLM responses based on:
    1. Exact match (hash of messages + parameters)
    2. TTL-based expiration
    3. Optional semantic similarity (future enhancement)
    """

    def __init__(self, redis_url: Optional[str] = None, ttl: int = 3600):
        """
        Initialize LLM cache.

        Args:
            redis_url: Redis connection URL (default: from env)
            ttl: Time-to-live for cache entries in seconds (default: 1 hour)
        """
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.ttl = ttl
        self.prefix = "llm_cache:"

        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            # Test connection
            self.redis_client.ping()
            logger.info("LLM cache initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize LLM cache: {e}. Cache will be disabled.")
            self.redis_client = None

    def _generate_cache_key(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        **kwargs
    ) -> str:
        """
        Generate cache key from request parameters.

        Args:
            messages: Chat messages
            model: Model name
            temperature: Temperature parameter
            **kwargs: Additional parameters

        Returns:
            Cache key (hash)
        """
        # Create deterministic representation of the request
        cache_data = {
            "messages": messages,
            "model": model,
            "temperature": temperature,
            # Only include relevant kwargs
            "max_tokens": kwargs.get("max_tokens"),
            "top_p": kwargs.get("top_p"),
            "frequency_penalty": kwargs.get("frequency_penalty"),
            "presence_penalty": kwargs.get("presence_penalty"),
        }

        # Generate hash
        cache_str = json.dumps(cache_data, sort_keys=True)
        cache_hash = hashlib.sha256(cache_str.encode()).hexdigest()

        return f"{self.prefix}{cache_hash}"

    def get(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        **kwargs
    ) -> Optional[str]:
        """
        Get cached LLM response if available.

        Args:
            messages: Chat messages
            model: Model name
            temperature: Temperature parameter
            **kwargs: Additional parameters

        Returns:
            Cached response or None if not found
        """
        if not self.redis_client:
            return None

        try:
            cache_key = self._generate_cache_key(messages, model, temperature, **kwargs)
            cached_response = self.redis_client.get(cache_key)

            if cached_response:
                logger.info(f"Cache HIT for key: {cache_key[:16]}...")
                return cached_response
            else:
                logger.debug(f"Cache MISS for key: {cache_key[:16]}...")
                return None

        except Exception as e:
            logger.error(f"Error getting from cache: {e}")
            return None

    def set(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        response: str,
        **kwargs
    ) -> bool:
        """
        Store LLM response in cache.

        Args:
            messages: Chat messages
            model: Model name
            temperature: Temperature parameter
            response: LLM response to cache
            **kwargs: Additional parameters

        Returns:
            True if cached successfully, False otherwise
        """
        if not self.redis_client:
            return False

        try:
            cache_key = self._generate_cache_key(messages, model, temperature, **kwargs)
            self.redis_client.setex(cache_key, self.ttl, response)
            logger.debug(f"Cached response with key: {cache_key[:16]}... (TTL: {self.ttl}s)")
            return True

        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            return False

    def invalidate(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        **kwargs
    ) -> bool:
        """
        Invalidate specific cache entry.

        Args:
            messages: Chat messages
            model: Model name
            temperature: Temperature parameter
            **kwargs: Additional parameters

        Returns:
            True if invalidated successfully
        """
        if not self.redis_client:
            return False

        try:
            cache_key = self._generate_cache_key(messages, model, temperature, **kwargs)
            self.redis_client.delete(cache_key)
            logger.debug(f"Invalidated cache key: {cache_key[:16]}...")
            return True

        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")
            return False

    def clear_all(self) -> int:
        """
        Clear all LLM cache entries.

        Returns:
            Number of keys deleted
        """
        if not self.redis_client:
            return 0

        try:
            keys = self.redis_client.keys(f"{self.prefix}*")
            if keys:
                count = self.redis_client.delete(*keys)
                logger.info(f"Cleared {count} cache entries")
                return count
            return 0

        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        if not self.redis_client:
            return {"enabled": False}

        try:
            keys = self.redis_client.keys(f"{self.prefix}*")
            return {
                "enabled": True,
                "total_entries": len(keys),
                "ttl": self.ttl,
                "redis_url": self.redis_url
            }

        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"enabled": False, "error": str(e)}


# Singleton instance
_cache_instance: Optional[LLMCache] = None


def get_llm_cache(ttl: int = 3600) -> LLMCache:
    """
    Get singleton LLM cache instance.

    Args:
        ttl: Time-to-live for cache entries in seconds

    Returns:
        LLMCache instance
    """
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = LLMCache(ttl=ttl)
    return _cache_instance
