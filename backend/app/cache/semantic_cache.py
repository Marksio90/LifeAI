"""Semantic Caching with Embeddings.

Revolutionary caching that understands meaning, not just exact matches!

Instead of requiring exact query match, semantic cache:
- Computes embeddings for queries
- Finds similar cached queries using cosine similarity
- Returns cached responses for semantically similar questions

Example:
  Query 1: "How can I save money?"
  Query 2: "What are ways to reduce expenses?"
  → Same semantic meaning → Cache HIT! 🎯

This can reduce LLM API costs by 70-90% while maintaining quality!
"""

import logging
import hashlib
import json
from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime, timedelta
import numpy as np

import redis.asyncio as redis
from app.services.llm_client import get_embedding

logger = logging.getLogger(__name__)


class SemanticCache:
    """
    Semantic caching using vector embeddings.

    Uses cosine similarity to find cached responses for semantically
    similar queries, even if the exact wording is different.
    """

    def __init__(
        self,
        redis_client: redis.Redis,
        similarity_threshold: float = 0.92,
        ttl_seconds: int = 3600
    ):
        """
        Initialize semantic cache.

        Args:
            redis_client: Redis client instance
            similarity_threshold: Minimum similarity score (0.0-1.0)
            ttl_seconds: Time to live for cache entries
        """
        self.redis = redis_client
        self.similarity_threshold = similarity_threshold
        self.ttl = ttl_seconds

        # Statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "total_queries": 0,
            "saved_api_calls": 0
        }

        logger.info(
            f"SemanticCache initialized "
            f"(threshold: {similarity_threshold}, TTL: {ttl_seconds}s)"
        )

    async def get(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached response for semantically similar query.

        Args:
            query: User query
            context: Optional context for more precise matching

        Returns:
            Cached response dict or None
        """
        try:
            self.stats["total_queries"] += 1

            # Generate query embedding
            query_embedding = await get_embedding(query)

            # Search for similar cached queries
            similar_entry = await self._find_similar_cached_query(
                query_embedding,
                context
            )

            if similar_entry:
                # Cache HIT
                self.stats["hits"] += 1
                self.stats["saved_api_calls"] += 1

                logger.info(
                    f"Semantic cache HIT (similarity: {similar_entry['similarity']:.3f}): "
                    f"'{query[:50]}...' → '{similar_entry['original_query'][:50]}...'"
                )

                # Update access stats
                await self._update_access_stats(similar_entry["cache_key"])

                return {
                    "response": similar_entry["response"],
                    "original_query": similar_entry["original_query"],
                    "similarity": similar_entry["similarity"],
                    "cached_at": similar_entry["cached_at"],
                    "cache_hit": True
                }

            # Cache MISS
            self.stats["misses"] += 1

            logger.debug(f"Semantic cache MISS: '{query[:50]}...'")

            return None

        except Exception as e:
            logger.error(f"Semantic cache get error: {e}")
            return None

    async def set(
        self,
        query: str,
        response: str,
        context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Cache response with semantic embedding.

        Args:
            query: Original query
            response: LLM response to cache
            context: Optional context
            metadata: Optional metadata

        Returns:
            True if cached successfully
        """
        try:
            # Generate query embedding
            query_embedding = await get_embedding(query)

            # Create cache entry
            cache_key = self._generate_cache_key(query, context)

            entry = {
                "query": query,
                "response": response,
                "embedding": query_embedding.tolist() if isinstance(query_embedding, np.ndarray) else query_embedding,
                "context": context or {},
                "metadata": metadata or {},
                "cached_at": datetime.utcnow().isoformat(),
                "access_count": 0,
                "last_accessed": datetime.utcnow().isoformat()
            }

            # Store in Redis
            await self.redis.setex(
                cache_key,
                self.ttl,
                json.dumps(entry)
            )

            # Add to searchable index (sorted set by timestamp for cleanup)
            index_key = "semantic_cache:index"
            await self.redis.zadd(
                index_key,
                {cache_key: datetime.utcnow().timestamp()}
            )

            logger.info(f"Cached response for: '{query[:50]}...'")

            return True

        except Exception as e:
            logger.error(f"Semantic cache set error: {e}")
            return False

    async def _find_similar_cached_query(
        self,
        query_embedding: List[float],
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Find most similar cached query using cosine similarity.

        Args:
            query_embedding: Query embedding vector
            context: Optional context for filtering

        Returns:
            Most similar cache entry or None
        """
        try:
            # Get all cached entries
            index_key = "semantic_cache:index"
            cache_keys = await self.redis.zrange(index_key, 0, -1)

            if not cache_keys:
                return None

            best_match = None
            best_similarity = 0.0

            # Compare with each cached embedding
            for cache_key in cache_keys:
                # Decode key if needed
                if isinstance(cache_key, bytes):
                    cache_key = cache_key.decode('utf-8')

                # Get cached entry
                entry_json = await self.redis.get(cache_key)
                if not entry_json:
                    continue

                entry = json.loads(entry_json)

                # Check context match (if provided)
                if context and entry.get("context") != context:
                    continue

                # Calculate cosine similarity
                cached_embedding = entry["embedding"]
                similarity = self._cosine_similarity(
                    query_embedding,
                    cached_embedding
                )

                # Update best match
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = {
                        "cache_key": cache_key,
                        "original_query": entry["query"],
                        "response": entry["response"],
                        "similarity": similarity,
                        "cached_at": entry["cached_at"],
                        "metadata": entry.get("metadata", {})
                    }

            # Return if above threshold
            if best_match and best_similarity >= self.similarity_threshold:
                return best_match

            return None

        except Exception as e:
            logger.error(f"Error finding similar query: {e}")
            return None

    def _cosine_similarity(
        self,
        vec1: List[float],
        vec2: List[float]
    ) -> float:
        """
        Calculate cosine similarity between two vectors.

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Similarity score (0.0-1.0)
        """
        try:
            # Convert to numpy arrays
            a = np.array(vec1)
            b = np.array(vec2)

            # Cosine similarity
            dot_product = np.dot(a, b)
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)

            if norm_a == 0 or norm_b == 0:
                return 0.0

            similarity = dot_product / (norm_a * norm_b)

            return float(similarity)

        except Exception as e:
            logger.error(f"Cosine similarity error: {e}")
            return 0.0

    def _generate_cache_key(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate cache key.

        Args:
            query: Query string
            context: Optional context

        Returns:
            Cache key
        """
        # Create unique key based on query and context
        key_data = query

        if context:
            key_data += json.dumps(context, sort_keys=True)

        key_hash = hashlib.sha256(key_data.encode()).hexdigest()

        return f"semantic_cache:entry:{key_hash}"

    async def _update_access_stats(self, cache_key: str):
        """
        Update access statistics for cache entry.

        Args:
            cache_key: Cache key
        """
        try:
            entry_json = await self.redis.get(cache_key)
            if not entry_json:
                return

            entry = json.loads(entry_json)

            entry["access_count"] = entry.get("access_count", 0) + 1
            entry["last_accessed"] = datetime.utcnow().isoformat()

            # Update in Redis (preserve TTL)
            ttl = await self.redis.ttl(cache_key)
            if ttl > 0:
                await self.redis.setex(
                    cache_key,
                    ttl,
                    json.dumps(entry)
                )

        except Exception as e:
            logger.debug(f"Error updating access stats: {e}")

    async def get_statistics(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Statistics dictionary
        """
        total = self.stats["total_queries"]
        hits = self.stats["hits"]
        misses = self.stats["misses"]

        hit_rate = (hits / total * 100) if total > 0 else 0.0

        # Get cache size
        index_key = "semantic_cache:index"
        cache_size = await self.redis.zcard(index_key)

        return {
            "total_queries": total,
            "cache_hits": hits,
            "cache_misses": misses,
            "hit_rate_percent": round(hit_rate, 2),
            "saved_api_calls": self.stats["saved_api_calls"],
            "cache_size": cache_size,
            "similarity_threshold": self.similarity_threshold,
            "ttl_seconds": self.ttl
        }

    async def clear(self):
        """Clear all semantic cache entries."""
        try:
            index_key = "semantic_cache:index"
            cache_keys = await self.redis.zrange(index_key, 0, -1)

            if cache_keys:
                # Delete all entries
                for key in cache_keys:
                    if isinstance(key, bytes):
                        key = key.decode('utf-8')
                    await self.redis.delete(key)

                # Clear index
                await self.redis.delete(index_key)

            logger.info(f"Cleared {len(cache_keys)} semantic cache entries")

        except Exception as e:
            logger.error(f"Error clearing semantic cache: {e}")

    async def cleanup_expired(self):
        """Remove expired entries from index."""
        try:
            index_key = "semantic_cache:index"
            cache_keys = await self.redis.zrange(index_key, 0, -1)

            removed = 0
            for key in cache_keys:
                if isinstance(key, bytes):
                    key = key.decode('utf-8')

                # Check if key exists
                exists = await self.redis.exists(key)
                if not exists:
                    # Remove from index
                    await self.redis.zrem(index_key, key)
                    removed += 1

            if removed > 0:
                logger.info(f"Cleaned up {removed} expired cache entries")

        except Exception as e:
            logger.error(f"Error cleaning up cache: {e}")


# Singleton instance
_semantic_cache: Optional[SemanticCache] = None


def get_semantic_cache() -> Optional[SemanticCache]:
    """
    Get semantic cache instance.

    Returns:
        SemanticCache instance or None
    """
    return _semantic_cache


def initialize_semantic_cache(
    redis_url: str,
    similarity_threshold: float = 0.92,
    ttl_seconds: int = 3600
) -> SemanticCache:
    """
    Initialize semantic cache.

    Args:
        redis_url: Redis connection URL
        similarity_threshold: Similarity threshold
        ttl_seconds: Cache TTL

    Returns:
        SemanticCache instance
    """
    global _semantic_cache

    redis_client = redis.from_url(redis_url, decode_responses=False)

    _semantic_cache = SemanticCache(
        redis_client,
        similarity_threshold,
        ttl_seconds
    )

    logger.info("Semantic cache initialized globally")

    return _semantic_cache
