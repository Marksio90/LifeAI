"""
Session storage with Redis persistence and in-memory fallback.
"""
import logging
from typing import Optional, Dict
from datetime import datetime, timezone
from app.schemas.common import Context, Message, Language
from app.core.redis_client import get_redis_client

logger = logging.getLogger(__name__)

# Session TTL: 24 hours (sessions auto-expire after 24h of inactivity)
SESSION_TTL = 24 * 60 * 60


class SessionStore:
    """
    Hybrid session storage with Redis persistence and in-memory fallback.

    Features:
    - Primary storage in Redis for persistence across restarts
    - In-memory cache for performance
    - Automatic fallback to in-memory if Redis unavailable
    - Session TTL management
    """

    def __init__(self):
        """Initialize session store."""
        self.redis = get_redis_client()
        self._memory_cache: Dict[str, Context] = {}
        self._use_redis = self.redis.is_connected

        if self._use_redis:
            logger.info("✅ SessionStore initialized with Redis persistence")
        else:
            logger.warning("⚠️ SessionStore using in-memory storage only (Redis unavailable)")

    def _serialize_context(self, context: Context) -> dict:
        """
        Serialize Context to dictionary for Redis storage.

        Args:
            context: Context object to serialize

        Returns:
            Dictionary representation
        """
        return {
            "session_id": context.session_id,
            "user_id": context.user_id,
            "language": context.language.value,
            "history": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
                    "metadata": msg.metadata
                }
                for msg in context.history
            ],
            "user_profile": context.user_profile,
            "relevant_memories": context.relevant_memories,
            "metadata": context.metadata
        }

    def _deserialize_context(self, data: dict) -> Context:
        """
        Deserialize dictionary to Context object.

        Args:
            data: Dictionary from Redis

        Returns:
            Context object
        """
        return Context(
            session_id=data["session_id"],
            user_id=data.get("user_id"),
            language=Language(data.get("language", "pl")),
            history=[
                Message(
                    role=msg["role"],
                    content=msg["content"],
                    timestamp=datetime.fromisoformat(msg["timestamp"]) if msg.get("timestamp") else datetime.now(timezone.utc),
                    metadata=msg.get("metadata", {})
                )
                for msg in data.get("history", [])
            ],
            user_profile=data.get("user_profile"),
            relevant_memories=data.get("relevant_memories", []),
            metadata=data.get("metadata", {})
        )

    def _redis_key(self, session_id: str) -> str:
        """Generate Redis key for session."""
        return f"session:{session_id}"

    def save(self, session_id: str, context: Context) -> bool:
        """
        Save session context.

        Args:
            session_id: Session identifier
            context: Context to save

        Returns:
            True if saved successfully
        """
        # Always save to memory cache
        self._memory_cache[session_id] = context

        # Try to save to Redis if available
        if self._use_redis:
            try:
                data = self._serialize_context(context)
                key = self._redis_key(session_id)
                success = self.redis.set_json(key, data, ex=SESSION_TTL)

                if success:
                    logger.debug(f"💾 Saved session {session_id} to Redis (TTL: {SESSION_TTL}s)")
                    return True
                else:
                    logger.warning(f"⚠️ Failed to save session {session_id} to Redis, using memory only")
                    return True  # Still have memory cache

            except Exception as e:
                logger.error(f"Error saving session {session_id} to Redis: {e}")
                return True  # Still have memory cache

        return True

    def load(self, session_id: str) -> Optional[Context]:
        """
        Load session context.

        Args:
            session_id: Session identifier

        Returns:
            Context if found, None otherwise
        """
        # Check memory cache first (faster)
        if session_id in self._memory_cache:
            logger.debug(f"📦 Loaded session {session_id} from memory cache")
            return self._memory_cache[session_id]

        # Try to load from Redis if available
        if self._use_redis:
            try:
                key = self._redis_key(session_id)
                data = self.redis.get_json(key)

                if data:
                    context = self._deserialize_context(data)
                    # Refresh memory cache
                    self._memory_cache[session_id] = context
                    # Extend TTL on access
                    self.redis.expire(key, SESSION_TTL)
                    logger.debug(f"📦 Loaded session {session_id} from Redis")
                    return context

            except Exception as e:
                logger.error(f"Error loading session {session_id} from Redis: {e}")

        return None

    def delete(self, session_id: str) -> bool:
        """
        Delete session.

        Args:
            session_id: Session identifier

        Returns:
            True if deleted
        """
        # Delete from memory
        if session_id in self._memory_cache:
            del self._memory_cache[session_id]

        # Delete from Redis if available
        if self._use_redis:
            try:
                key = self._redis_key(session_id)
                deleted = self.redis.delete(key)
                logger.debug(f"🗑️ Deleted session {session_id} (Redis: {deleted > 0})")
                return True
            except Exception as e:
                logger.error(f"Error deleting session {session_id} from Redis: {e}")

        return True

    def exists(self, session_id: str) -> bool:
        """
        Check if session exists.

        Args:
            session_id: Session identifier

        Returns:
            True if session exists
        """
        # Check memory first
        if session_id in self._memory_cache:
            return True

        # Check Redis if available
        if self._use_redis:
            try:
                key = self._redis_key(session_id)
                return self.redis.exists(key) > 0
            except Exception as e:
                logger.error(f"Error checking session {session_id} existence: {e}")

        return False

    def get_all_session_ids(self) -> list[str]:
        """
        Get all active session IDs.

        Returns:
            List of session IDs
        """
        session_ids = set(self._memory_cache.keys())

        # Add sessions from Redis if available
        if self._use_redis:
            try:
                redis_keys = self.redis.keys("session:*")
                # Extract session_id from "session:uuid" pattern
                session_ids.update(key.replace("session:", "") for key in redis_keys)
            except Exception as e:
                logger.error(f"Error getting session IDs from Redis: {e}")

        return list(session_ids)

    def get_stats(self) -> dict:
        """
        Get storage statistics.

        Returns:
            Dictionary with stats
        """
        stats = {
            "memory_sessions": len(self._memory_cache),
            "using_redis": self._use_redis,
            "redis_connected": self.redis.is_connected
        }

        if self._use_redis:
            try:
                redis_keys = self.redis.keys("session:*")
                stats["redis_sessions"] = len(redis_keys)
            except Exception as e:
                logger.error(f"Error getting Redis stats: {e}")
                stats["redis_sessions"] = 0

        return stats


# Singleton instance
_session_store: Optional[SessionStore] = None


def get_session_store() -> SessionStore:
    """Get or create SessionStore singleton."""
    global _session_store

    if _session_store is None:
        _session_store = SessionStore()

    return _session_store
