"""Vector store factory for selecting production or development storage."""
import os
import logging
from typing import Optional

from app.memory.vector_store import VectorStore
from app.memory.in_memory_store import InMemoryVectorStore

logger = logging.getLogger(__name__)


def get_vector_store() -> VectorStore:
    """
    Get the configured vector store based on environment.

    Returns:
        VectorStore instance (Pinecone for production, in-memory for development)
    """
    vector_db_type = os.getenv("VECTOR_DB_TYPE", "in-memory").lower()

    if vector_db_type == "pinecone":
        try:
            from app.memory.pinecone_store import PineconeVectorStore
            logger.info("Using Pinecone vector store")
            return PineconeVectorStore()
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {e}")
            logger.warning("Falling back to in-memory vector store")
            return InMemoryVectorStore()

    elif vector_db_type == "weaviate":
        try:
            # TODO: Implement Weaviate integration
            logger.warning("Weaviate not yet implemented, using in-memory store")
            return InMemoryVectorStore()
        except Exception as e:
            logger.error(f"Failed to initialize Weaviate: {e}")
            logger.warning("Falling back to in-memory vector store")
            return InMemoryVectorStore()

    else:
        logger.info("Using in-memory vector store")
        return InMemoryVectorStore()


# Global vector store instance
_vector_store: Optional[VectorStore] = None


def initialize_vector_store() -> VectorStore:
    """Initialize and return the global vector store instance."""
    global _vector_store
    if _vector_store is None:
        _vector_store = get_vector_store()
    return _vector_store
