"""Production vector database implementation using Pinecone."""
from typing import List, Optional, Dict, Any
import os
import logging
from pinecone import Pinecone, ServerlessSpec

from app.memory.vector_store import VectorStore, VectorDocument, SearchResult

logger = logging.getLogger(__name__)


class PineconeVectorStore(VectorStore):
    """Production vector store implementation using Pinecone."""

    def __init__(self):
        """Initialize Pinecone client and index."""
        self.api_key = os.getenv("PINECONE_API_KEY")
        self.environment = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
        self.index_name = os.getenv("PINECONE_INDEX_NAME", "lifeai-embeddings")

        if not self.api_key:
            raise ValueError("PINECONE_API_KEY environment variable is required")

        # Initialize Pinecone
        self.pc = Pinecone(api_key=self.api_key)

        # Create index if it doesn't exist
        self._ensure_index_exists()

        # Connect to index
        self.index = self.pc.Index(self.index_name)

        logger.info(f"Pinecone vector store initialized: {self.index_name}")

    def _ensure_index_exists(self):
        """Create Pinecone index if it doesn't exist."""
        existing_indexes = [index.name for index in self.pc.list_indexes()]

        if self.index_name not in existing_indexes:
            logger.info(f"Creating Pinecone index: {self.index_name}")

            self.pc.create_index(
                name=self.index_name,
                dimension=1536,  # OpenAI text-embedding-3-small dimension
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region=self.environment
                )
            )

            logger.info(f"Pinecone index created: {self.index_name}")

    async def upsert(self, documents: List[VectorDocument]) -> bool:
        """
        Insert or update vectors in Pinecone.

        Args:
            documents: List of vector documents to upsert

        Returns:
            True if successful, False otherwise
        """
        try:
            # Prepare vectors for Pinecone
            vectors = []
            for doc in documents:
                vectors.append({
                    "id": doc.id,
                    "values": doc.embedding,
                    "metadata": {
                        **doc.metadata,
                        "content": doc.content[:1000]  # Pinecone metadata limit
                    }
                })

            # Upsert in batches of 100
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                self.index.upsert(vectors=batch)

            logger.info(f"Upserted {len(documents)} documents to Pinecone")
            return True

        except Exception as e:
            logger.error(f"Error upserting to Pinecone: {e}")
            return False

    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Search for similar vectors in Pinecone.

        Args:
            query_embedding: Query vector embedding
            top_k: Number of results to return
            filter_metadata: Metadata filters (e.g., {"user_id": "123"})

        Returns:
            List of search results sorted by similarity
        """
        try:
            # Build filter if provided
            pinecone_filter = None
            if filter_metadata:
                pinecone_filter = filter_metadata

            # Query Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                filter=pinecone_filter,
                include_metadata=True
            )

            # Convert to SearchResult objects
            search_results = []
            for match in results.matches:
                doc = VectorDocument(
                    id=match.id,
                    content=match.metadata.get("content", ""),
                    embedding=[],  # Not returned by Pinecone
                    metadata={k: v for k, v in match.metadata.items() if k != "content"}
                )

                search_results.append(SearchResult(
                    document=doc,
                    score=match.score
                ))

            logger.info(f"Found {len(search_results)} results in Pinecone")
            return search_results

        except Exception as e:
            logger.error(f"Error searching Pinecone: {e}")
            return []

    async def delete(self, document_ids: List[str]) -> bool:
        """
        Delete vectors from Pinecone.

        Args:
            document_ids: List of document IDs to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            self.index.delete(ids=document_ids)
            logger.info(f"Deleted {len(document_ids)} documents from Pinecone")
            return True

        except Exception as e:
            logger.error(f"Error deleting from Pinecone: {e}")
            return False

    async def clear(self) -> bool:
        """Clear all vectors from the index."""
        try:
            self.index.delete(delete_all=True)
            logger.info("Cleared all documents from Pinecone")
            return True

        except Exception as e:
            logger.error(f"Error clearing Pinecone: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        try:
            stats = self.index.describe_index_stats()
            return {
                "total_vectors": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness
            }
        except Exception as e:
            logger.error(f"Error getting Pinecone stats: {e}")
            return {}
