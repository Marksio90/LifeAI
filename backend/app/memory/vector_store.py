from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class VectorDocument:
    """Document with vector embedding"""
    id: str
    content: str
    embedding: List[float]
    metadata: Dict[str, Any]


@dataclass
class SearchResult:
    """Search result from vector store"""
    document: VectorDocument
    score: float  # Similarity score


class VectorStore(ABC):
    """
    Abstract base class for vector database implementations.

    Supports multiple backends: Pinecone, Weaviate, Qdrant, or simple in-memory.
    """

    @abstractmethod
    async def upsert(
        self,
        documents: List[VectorDocument]
    ) -> bool:
        """
        Insert or update documents in the vector store.

        Args:
            documents: List of documents with embeddings

        Returns:
            bool: Success status
        """
        pass

    @abstractmethod
    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Search for similar documents.

        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            filter_metadata: Optional metadata filters

        Returns:
            List of search results sorted by similarity
        """
        pass

    @abstractmethod
    async def delete(
        self,
        document_ids: List[str]
    ) -> bool:
        """Delete documents by IDs."""
        pass

    @abstractmethod
    async def get_by_id(
        self,
        document_id: str
    ) -> Optional[VectorDocument]:
        """Get document by ID."""
        pass


class InMemoryVectorStore(VectorStore):
    """
    Simple in-memory vector store for development/testing.

    For production, use Pinecone, Weaviate, or Qdrant.
    """

    def __init__(self):
        self.documents: Dict[str, VectorDocument] = {}

    async def upsert(self, documents: List[VectorDocument]) -> bool:
        """Insert or update documents."""
        try:
            for doc in documents:
                self.documents[doc.id] = doc
            logger.info(f"Upserted {len(documents)} documents to in-memory store")
            return True
        except Exception as e:
            logger.error(f"Error upserting documents: {e}")
            return False

    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search using cosine similarity."""
        try:
            results = []

            for doc in self.documents.values():
                # Apply metadata filter if provided
                if filter_metadata:
                    if not all(
                        doc.metadata.get(k) == v
                        for k, v in filter_metadata.items()
                    ):
                        continue

                # Calculate cosine similarity
                score = self._cosine_similarity(query_embedding, doc.embedding)
                results.append(SearchResult(document=doc, score=score))

            # Sort by score (descending) and take top_k
            results.sort(key=lambda x: x.score, reverse=True)
            return results[:top_k]

        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []

    async def delete(self, document_ids: List[str]) -> bool:
        """Delete documents."""
        try:
            for doc_id in document_ids:
                self.documents.pop(doc_id, None)
            logger.info(f"Deleted {len(document_ids)} documents")
            return True
        except Exception as e:
            logger.error(f"Error deleting documents: {e}")
            return False

    async def get_by_id(self, document_id: str) -> Optional[VectorDocument]:
        """Get document by ID."""
        return self.documents.get(document_id)

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        import math

        dot_product = sum(x * y for x, y in zip(a, b))
        magnitude_a = math.sqrt(sum(x * x for x in a))
        magnitude_b = math.sqrt(sum(y * y for y in b))

        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0

        return dot_product / (magnitude_a * magnitude_b)

    def clear(self):
        """Clear all documents (for testing)."""
        self.documents.clear()
        logger.info("Cleared in-memory vector store")


# Singleton instance
_vector_store: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    """Get the global vector store instance."""
    global _vector_store
    if _vector_store is None:
        # For now, use in-memory store
        # In production, initialize Pinecone/Weaviate/Qdrant here
        _vector_store = InMemoryVectorStore()
        logger.info("Initialized in-memory vector store")
    return _vector_store


def set_vector_store(store: VectorStore):
    """Set custom vector store (useful for testing or production setup)."""
    global _vector_store
    _vector_store = store
    logger.info(f"Set vector store to {type(store).__name__}")
