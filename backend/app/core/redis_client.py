"""
Redis client for session storage and caching.
"""
import json
import logging
from typing import Optional, Any
from redis import Redis, ConnectionPool
from redis.exceptions import RedisError, ConnectionError as RedisConnectionError
import os

logger = logging.getLogger(__name__)


class RedisClient:
    """
    Redis client wrapper for session management and caching.

    Provides methods for:
    - Session storage with TTL
    - Context serialization/deserialization
    - Graceful fallback on connection errors
    """

    def __init__(self, url: Optional[str] = None, decode_responses: bool = True):
        """
        Initialize Redis client.

        Args:
            url: Redis connection URL (e.g., redis://localhost:6379/0)
            decode_responses: If True, decode byte responses to strings
        """
        self.url = url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.decode_responses = decode_responses
        self._client: Optional[Redis] = None
        self._pool: Optional[ConnectionPool] = None
        self._connected = False

        self._connect()

    def _connect(self):
        """Establish connection to Redis."""
        try:
            self._pool = ConnectionPool.from_url(
                self.url,
                decode_responses=self.decode_responses,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                max_connections=20
            )
            self._client = Redis(connection_pool=self._pool)

            # Test connection
            self._client.ping()
            self._connected = True
            logger.info(f"✅ Connected to Redis at {self.url}")

        except RedisConnectionError as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            logger.warning("⚠️ Running without Redis - sessions will be in-memory only")
            self._connected = False
        except Exception as e:
            logger.error(f"❌ Unexpected Redis error: {e}", exc_info=True)
            self._connected = False

    @property
    def is_connected(self) -> bool:
        """Check if Redis is connected."""
        return self._connected and self._client is not None

    def get(self, key: str) -> Optional[str]:
        """
        Get value by key.

        Args:
            key: Redis key

        Returns:
            Value as string, or None if not found or error
        """
        if not self.is_connected:
            return None

        try:
            return self._client.get(key)
        except RedisError as e:
            logger.error(f"Redis GET error for key '{key}': {e}")
            return None

    def set(
        self,
        key: str,
        value: str,
        ex: Optional[int] = None,
        nx: bool = False
    ) -> bool:
        """
        Set key-value pair.

        Args:
            key: Redis key
            value: Value to store
            ex: Expiration time in seconds
            nx: Only set if key doesn't exist

        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected:
            return False

        try:
            result = self._client.set(key, value, ex=ex, nx=nx)
            return bool(result)
        except RedisError as e:
            logger.error(f"Redis SET error for key '{key}': {e}")
            return False

    def get_json(self, key: str) -> Optional[Any]:
        """
        Get JSON value by key.

        Args:
            key: Redis key

        Returns:
            Deserialized JSON object, or None if not found or error
        """
        value = self.get(key)
        if value is None:
            return None

        try:
            return json.loads(value)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error for key '{key}': {e}")
            return None

    def set_json(
        self,
        key: str,
        value: Any,
        ex: Optional[int] = None,
        nx: bool = False
    ) -> bool:
        """
        Set JSON value.

        Args:
            key: Redis key
            value: Object to serialize to JSON
            ex: Expiration time in seconds
            nx: Only set if key doesn't exist

        Returns:
            True if successful, False otherwise
        """
        try:
            json_str = json.dumps(value, default=str)
            return self.set(key, json_str, ex=ex, nx=nx)
        except (TypeError, ValueError) as e:
            logger.error(f"JSON encode error for key '{key}': {e}")
            return False

    def delete(self, *keys: str) -> int:
        """
        Delete one or more keys.

        Args:
            *keys: Keys to delete

        Returns:
            Number of keys deleted
        """
        if not self.is_connected or not keys:
            return 0

        try:
            return self._client.delete(*keys)
        except RedisError as e:
            logger.error(f"Redis DELETE error: {e}")
            return 0

    def exists(self, *keys: str) -> int:
        """
        Check if keys exist.

        Args:
            *keys: Keys to check

        Returns:
            Number of existing keys
        """
        if not self.is_connected or not keys:
            return 0

        try:
            return self._client.exists(*keys)
        except RedisError as e:
            logger.error(f"Redis EXISTS error: {e}")
            return 0

    def expire(self, key: str, seconds: int) -> bool:
        """
        Set expiration time on a key.

        Args:
            key: Redis key
            seconds: Expiration time in seconds

        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected:
            return False

        try:
            return bool(self._client.expire(key, seconds))
        except RedisError as e:
            logger.error(f"Redis EXPIRE error for key '{key}': {e}")
            return False

    def ttl(self, key: str) -> int:
        """
        Get remaining TTL for a key.

        Args:
            key: Redis key

        Returns:
            TTL in seconds, -1 if no expiration, -2 if key doesn't exist
        """
        if not self.is_connected:
            return -2

        try:
            return self._client.ttl(key)
        except RedisError as e:
            logger.error(f"Redis TTL error for key '{key}': {e}")
            return -2

    def keys(self, pattern: str = "*") -> list[str]:
        """
        Get keys matching pattern.

        Args:
            pattern: Redis key pattern (e.g., "session:*")

        Returns:
            List of matching keys
        """
        if not self.is_connected:
            return []

        try:
            return self._client.keys(pattern)
        except RedisError as e:
            logger.error(f"Redis KEYS error: {e}")
            return []

    def close(self):
        """Close Redis connection."""
        if self._client:
            try:
                self._client.close()
                logger.info("Closed Redis connection")
            except Exception as e:
                logger.error(f"Error closing Redis connection: {e}")

        if self._pool:
            try:
                self._pool.disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting Redis pool: {e}")

        self._connected = False


# Singleton instance
_redis_client: Optional[RedisClient] = None


def get_redis_client() -> RedisClient:
    """Get or create Redis client singleton."""
    global _redis_client

    if _redis_client is None:
        _redis_client = RedisClient()

    return _redis_client


def close_redis_client():
    """Close Redis client connection."""
    global _redis_client

    if _redis_client:
        _redis_client.close()
        _redis_client = None
