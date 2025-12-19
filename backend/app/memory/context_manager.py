from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import logging

from app.schemas.common import Context, Message
from app.memory.vector_store import (
    get_vector_store,
    VectorDocument,
    SearchResult
)
from app.memory.embeddings import embed

logger = logging.getLogger(__name__)


class ContextManager:
    """
    Advanced context management with long-term memory.

    Features:
    - Stores conversation history in vector database
    - Retrieves relevant past conversations (semantic search)
    - Maintains user profile and preferences
    - Tracks conversation themes and patterns
    """

    def __init__(self):
        self.vector_store = get_vector_store()

    async def store_conversation(
        self,
        context: Context,
        user_message: str,
        assistant_response: str
    ) -> bool:
        """
        Store a conversation turn in long-term memory.

        Args:
            context: Conversation context
            user_message: User's message
            assistant_response: Assistant's response

        Returns:
            bool: Success status
        """
        try:
            # Create conversation summary for embedding
            conversation_text = f"User: {user_message}\nAssistant: {assistant_response}"

            # Generate embedding
            embedding = await embed(conversation_text)

            # Create document
            document = VectorDocument(
                id=str(uuid.uuid4()),
                content=conversation_text,
                embedding=embedding,
                metadata={
                    "session_id": context.session_id,
                    "user_id": context.user_id or "anonymous",
                    "language": context.language.value,
                    "timestamp": datetime.utcnow().isoformat(),
                    "user_message": user_message,
                    "assistant_response": assistant_response
                }
            )

            # Store in vector database
            success = await self.vector_store.upsert([document])

            if success:
                logger.info(f"Stored conversation in long-term memory (session: {context.session_id})")

            return success

        except Exception as e:
            logger.error(f"Error storing conversation: {e}")
            return False

    async def retrieve_relevant_memories(
        self,
        query: str,
        user_id: Optional[str] = None,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant past conversations based on semantic similarity.

        Args:
            query: Current user query
            user_id: Optional user filter
            top_k: Number of memories to retrieve

        Returns:
            List of relevant past conversations
        """
        try:
            # Generate embedding for query
            query_embedding = await embed(query)

            # Search vector store
            filter_metadata = {"user_id": user_id} if user_id else None
            results: List[SearchResult] = await self.vector_store.search(
                query_embedding=query_embedding,
                top_k=top_k,
                filter_metadata=filter_metadata
            )

            # Format results
            memories = []
            for result in results:
                if result.score > 0.7:  # Only include highly relevant memories
                    memories.append({
                        "content": result.document.content,
                        "score": result.score,
                        "timestamp": result.document.metadata.get("timestamp"),
                        "session_id": result.document.metadata.get("session_id")
                    })

            logger.info(f"Retrieved {len(memories)} relevant memories for query")
            return memories

        except Exception as e:
            logger.error(f"Error retrieving memories: {e}")
            return []

    async def enrich_context(
        self,
        context: Context,
        current_message: str
    ) -> Context:
        """
        Enrich context with relevant memories from past conversations.

        Args:
            context: Current conversation context
            current_message: Current user message

        Returns:
            Enhanced context with relevant memories
        """
        try:
            # Retrieve relevant memories
            memories = await self.retrieve_relevant_memories(
                query=current_message,
                user_id=context.user_id,
                top_k=3
            )

            # Add memories to context
            context.relevant_memories = memories

            logger.debug(f"Enriched context with {len(memories)} memories")

            return context

        except Exception as e:
            logger.error(f"Error enriching context: {e}")
            return context

    async def update_user_preferences(
        self,
        user_id: str,
        preference_key: str,
        preference_value: Any
    ) -> bool:
        """
        Update user preferences for personalization.

        Args:
            user_id: User identifier
            preference_key: Preference key (e.g., "preferred_tone", "topics_of_interest")
            preference_value: Preference value

        Returns:
            bool: Success status
        """
        try:
            # Store preference as a special document
            preference_text = f"User preference: {preference_key} = {preference_value}"
            embedding = await embed(preference_text)

            document = VectorDocument(
                id=f"pref_{user_id}_{preference_key}",
                content=preference_text,
                embedding=embedding,
                metadata={
                    "user_id": user_id,
                    "type": "preference",
                    "key": preference_key,
                    "value": str(preference_value),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )

            success = await self.vector_store.upsert([document])
            logger.info(f"Updated preference {preference_key} for user {user_id}")

            return success

        except Exception as e:
            logger.error(f"Error updating user preference: {e}")
            return False

    async def get_user_profile(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get user profile with aggregated preferences and history.

        Args:
            user_id: User identifier

        Returns:
            User profile dictionary
        """
        try:
            # TODO: Implement more sophisticated profile aggregation
            # For now, return basic structure

            profile = {
                "user_id": user_id,
                "preferences": {},
                "conversation_count": 0,
                "topics_discussed": [],
                "last_interaction": None
            }

            logger.debug(f"Retrieved profile for user {user_id}")
            return profile

        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return {"user_id": user_id}


# Singleton instance
_context_manager: Optional[ContextManager] = None


def get_context_manager() -> ContextManager:
    """Get the global context manager instance."""
    global _context_manager
    if _context_manager is None:
        _context_manager = ContextManager()
        logger.info("Initialized context manager")
    return _context_manager
