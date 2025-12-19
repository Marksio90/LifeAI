import os
from typing import List
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class EmbeddingsService:
    """
    Service for generating text embeddings.

    Uses OpenAI's text-embedding-3-small model for efficient,
    high-quality embeddings.
    """

    MODEL = "text-embedding-3-small"  # 1536 dimensions, cost-effective
    # Alternative: "text-embedding-3-large" for higher quality (3072 dims)

    @staticmethod
    async def generate_embedding(text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Input text

        Returns:
            List of floats representing the embedding vector
        """
        try:
            response = client.embeddings.create(
                model=EmbeddingsService.MODEL,
                input=text
            )
            embedding = response.data[0].embedding
            logger.debug(f"Generated embedding for text of length {len(text)}")
            return embedding

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            # Return zero vector as fallback
            return [0.0] * 1536

    @staticmethod
    async def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batch.

        More efficient than individual requests.

        Args:
            texts: List of input texts

        Returns:
            List of embedding vectors
        """
        try:
            response = client.embeddings.create(
                model=EmbeddingsService.MODEL,
                input=texts
            )
            embeddings = [data.embedding for data in response.data]
            logger.info(f"Generated {len(embeddings)} embeddings in batch")
            return embeddings

        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            # Return zero vectors as fallback
            return [[0.0] * 1536 for _ in texts]


# Convenience functions
async def embed(text: str) -> List[float]:
    """Generate embedding for text."""
    return await EmbeddingsService.generate_embedding(text)


async def embed_batch(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for multiple texts."""
    return await EmbeddingsService.generate_embeddings_batch(texts)
