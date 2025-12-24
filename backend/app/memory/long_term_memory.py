"""Long-Term Memory System for LifeAI.

Implements intelligent memory management that:
- Stores important user interactions and preferences
- Retrieves relevant context from past conversations
- Learns user patterns and preferences over time
- Provides personalized responses based on memory
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import hashlib
import json

from app.memory.vector_factory import get_vector_store
from app.services.llm_client import get_embedding

logger = logging.getLogger(__name__)


class MemoryType:
    """Types of memories stored in the system."""
    PREFERENCE = "preference"  # User preferences (e.g., "prefers formal tone")
    FACT = "fact"  # Facts about user (e.g., "has 2 children")
    GOAL = "goal"  # User goals (e.g., "wants to save 1000 PLN monthly")
    INTERACTION = "interaction"  # Important interactions
    CONTEXT = "context"  # Conversational context


class MemoryImportance:
    """Importance levels for memory retention."""
    CRITICAL = 5  # Never forget (e.g., allergies, medical info)
    HIGH = 4  # Very important (e.g., major goals)
    MEDIUM = 3  # Moderately important (e.g., preferences)
    LOW = 2  # Minor details
    TRANSIENT = 1  # Temporary context


class LongTermMemory:
    """Manages long-term memory for users using vector storage."""

    def __init__(self):
        """Initialize long-term memory system."""
        self.vector_store = get_vector_store()
        logger.info("Long-term memory system initialized")

    async def store_memory(
        self,
        user_id: str,
        content: str,
        memory_type: str = MemoryType.INTERACTION,
        importance: int = MemoryImportance.MEDIUM,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Store a memory in long-term storage.

        Args:
            user_id: User identifier
            content: Memory content to store
            memory_type: Type of memory (preference, fact, goal, etc.)
            importance: Importance level (1-5)
            metadata: Additional metadata

        Returns:
            True if stored successfully
        """
        try:
            # Generate embedding for the memory
            embedding = await get_embedding(content)

            # Create memory document
            memory_id = self._generate_memory_id(user_id, content)

            memory_metadata = {
                "user_id": user_id,
                "memory_type": memory_type,
                "importance": importance,
                "created_at": datetime.utcnow().isoformat(),
                "access_count": 0,
                "last_accessed": datetime.utcnow().isoformat(),
                **(metadata or {})
            }

            from app.memory.vector_store import VectorDocument
            document = VectorDocument(
                id=memory_id,
                content=content,
                embedding=embedding,
                metadata=memory_metadata
            )

            # Store in vector database
            success = await self.vector_store.upsert([document])

            if success:
                logger.info(
                    f"Stored {memory_type} memory for user {user_id}: {content[:50]}..."
                )

            return success

        except Exception as e:
            logger.error(f"Error storing memory: {e}")
            return False

    async def retrieve_relevant_memories(
        self,
        user_id: str,
        query: str,
        top_k: int = 5,
        memory_types: Optional[List[str]] = None,
        min_importance: int = MemoryImportance.LOW
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant memories for a given query.

        Args:
            user_id: User identifier
            query: Query to find relevant memories
            top_k: Number of memories to retrieve
            memory_types: Filter by specific memory types
            min_importance: Minimum importance level

        Returns:
            List of relevant memories with metadata
        """
        try:
            # Generate query embedding
            query_embedding = await get_embedding(query)

            # Build metadata filter
            filter_metadata = {"user_id": user_id}

            # Search vector store
            results = await self.vector_store.search(
                query_embedding=query_embedding,
                top_k=top_k * 2,  # Get more to filter
                filter_metadata=filter_metadata
            )

            # Filter and format results
            memories = []
            for result in results:
                metadata = result.document.metadata

                # Apply filters
                if memory_types and metadata.get("memory_type") not in memory_types:
                    continue

                if metadata.get("importance", 0) < min_importance:
                    continue

                memories.append({
                    "content": result.document.content,
                    "type": metadata.get("memory_type"),
                    "importance": metadata.get("importance"),
                    "created_at": metadata.get("created_at"),
                    "relevance_score": result.score,
                    "metadata": metadata
                })

                # Update access statistics
                await self._update_memory_access(result.document.id, metadata)

            # Sort by relevance and importance
            memories.sort(
                key=lambda m: (m["relevance_score"] * 0.7 + m["importance"] * 0.06),
                reverse=True
            )

            logger.info(
                f"Retrieved {len(memories)} relevant memories for user {user_id}"
            )

            return memories[:top_k]

        except Exception as e:
            logger.error(f"Error retrieving memories: {e}")
            return []

    async def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Get all stored preferences for a user.

        Args:
            user_id: User identifier

        Returns:
            Dictionary of user preferences
        """
        try:
            # Search for preference memories
            query_embedding = await get_embedding("user preferences and settings")

            results = await self.vector_store.search(
                query_embedding=query_embedding,
                top_k=20,
                filter_metadata={
                    "user_id": user_id,
                    "memory_type": MemoryType.PREFERENCE
                }
            )

            preferences = {}
            for result in results:
                content = result.document.content
                metadata = result.document.metadata

                # Parse preference content
                # Expected format: "prefers X" or "likes Y" or "dislikes Z"
                preferences[metadata.get("preference_key", "unknown")] = {
                    "value": content,
                    "confidence": result.score,
                    "last_updated": metadata.get("created_at")
                }

            return preferences

        except Exception as e:
            logger.error(f"Error getting user preferences: {e}")
            return {}

    async def get_user_facts(self, user_id: str, top_k: int = 10) -> List[str]:
        """
        Get important facts about the user.

        Args:
            user_id: User identifier
            top_k: Number of facts to retrieve

        Returns:
            List of fact strings
        """
        try:
            query_embedding = await get_embedding("important facts about user")

            results = await self.vector_store.search(
                query_embedding=query_embedding,
                top_k=top_k,
                filter_metadata={
                    "user_id": user_id,
                    "memory_type": MemoryType.FACT
                }
            )

            facts = [result.document.content for result in results]
            return facts

        except Exception as e:
            logger.error(f"Error getting user facts: {e}")
            return []

    async def learn_from_conversation(
        self,
        user_id: str,
        conversation_messages: List[Dict[str, str]]
    ) -> int:
        """
        Extract and store memories from a conversation.

        Uses LLM to identify important information to remember.

        Args:
            user_id: User identifier
            conversation_messages: List of conversation messages

        Returns:
            Number of memories stored
        """
        try:
            from app.services.llm_client import call_llm

            # Prepare conversation for analysis
            conversation_text = "\n".join([
                f"{msg['role']}: {msg['content']}"
                for msg in conversation_messages[-10:]  # Last 10 messages
            ])

            # Ask LLM to extract important information
            analysis_prompt = f"""Analyze this conversation and extract important information to remember about the user.

Conversation:
{conversation_text}

Extract:
1. User preferences (tone, style, communication preferences)
2. Important facts (family, job, situation)
3. Goals and objectives
4. Recurring topics or concerns

Format each memory as:
TYPE|IMPORTANCE|CONTENT

Where:
- TYPE: preference, fact, goal, or context
- IMPORTANCE: 1-5 (5 = critical, 1 = transient)
- CONTENT: The actual information to remember

Example:
preference|3|Prefers detailed explanations with examples
fact|4|Has 2 children and works as a teacher
goal|5|Wants to save 1000 PLN monthly for vacation

Only extract truly important information. Skip generic pleasantries."""

            response = await call_llm([
                {"role": "system", "content": "You are a memory extraction expert."},
                {"role": "user", "content": analysis_prompt}
            ])

            # Parse response and store memories
            memories_stored = 0
            lines = response.strip().split("\n")

            for line in lines:
                line = line.strip()
                if not line or "|" not in line:
                    continue

                try:
                    parts = line.split("|")
                    if len(parts) != 3:
                        continue

                    memory_type, importance_str, content = parts
                    memory_type = memory_type.strip().lower()
                    importance = int(importance_str.strip())
                    content = content.strip()

                    # Validate
                    if memory_type not in [
                        MemoryType.PREFERENCE,
                        MemoryType.FACT,
                        MemoryType.GOAL,
                        MemoryType.CONTEXT
                    ]:
                        continue

                    if not (1 <= importance <= 5):
                        continue

                    # Store memory
                    success = await self.store_memory(
                        user_id=user_id,
                        content=content,
                        memory_type=memory_type,
                        importance=importance,
                        metadata={"source": "conversation_analysis"}
                    )

                    if success:
                        memories_stored += 1

                except (ValueError, IndexError) as e:
                    logger.warning(f"Failed to parse memory line: {line} - {e}")
                    continue

            logger.info(
                f"Learned {memories_stored} new memories from conversation for user {user_id}"
            )

            return memories_stored

        except Exception as e:
            logger.error(f"Error learning from conversation: {e}")
            return 0

    async def cleanup_old_memories(
        self,
        user_id: str,
        days_threshold: int = 90,
        min_importance: int = MemoryImportance.MEDIUM
    ) -> int:
        """
        Clean up old, low-importance memories.

        Args:
            user_id: User identifier
            days_threshold: Delete memories older than this many days
            min_importance: Only delete memories below this importance

        Returns:
            Number of memories deleted
        """
        try:
            # This would require listing all user memories
            # For now, implement as a placeholder
            # In production, you'd scan the vector store and delete based on metadata

            logger.info(
                f"Memory cleanup for user {user_id}: "
                f"threshold={days_threshold} days, min_importance={min_importance}"
            )

            # TODO: Implement actual cleanup logic
            # This requires vector store to support filtering by metadata date

            return 0

        except Exception as e:
            logger.error(f"Error cleaning up memories: {e}")
            return 0

    async def get_memory_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Get a summary of user's stored memories.

        Args:
            user_id: User identifier

        Returns:
            Summary statistics
        """
        try:
            # Get samples from each memory type
            preferences = await self.retrieve_relevant_memories(
                user_id=user_id,
                query="preferences",
                top_k=5,
                memory_types=[MemoryType.PREFERENCE]
            )

            facts = await self.retrieve_relevant_memories(
                user_id=user_id,
                query="facts",
                top_k=5,
                memory_types=[MemoryType.FACT]
            )

            goals = await self.retrieve_relevant_memories(
                user_id=user_id,
                query="goals",
                top_k=5,
                memory_types=[MemoryType.GOAL]
            )

            return {
                "total_preferences": len(preferences),
                "total_facts": len(facts),
                "total_goals": len(goals),
                "sample_preferences": [m["content"] for m in preferences[:3]],
                "sample_facts": [m["content"] for m in facts[:3]],
                "sample_goals": [m["content"] for m in goals[:3]]
            }

        except Exception as e:
            logger.error(f"Error getting memory summary: {e}")
            return {}

    def _generate_memory_id(self, user_id: str, content: str) -> str:
        """Generate unique ID for memory."""
        unique_string = f"{user_id}:{content}:{datetime.utcnow().isoformat()}"
        return f"memory:{hashlib.sha256(unique_string.encode()).hexdigest()[:16]}"

    async def _update_memory_access(self, memory_id: str, metadata: Dict[str, Any]):
        """Update memory access statistics."""
        try:
            # Increment access count
            access_count = metadata.get("access_count", 0) + 1
            metadata["access_count"] = access_count
            metadata["last_accessed"] = datetime.utcnow().isoformat()

            # Note: This requires vector store to support metadata updates
            # For now, just log it
            logger.debug(f"Memory {memory_id} accessed (count: {access_count})")

        except Exception as e:
            logger.debug(f"Could not update memory access stats: {e}")


# Singleton instance
_long_term_memory: Optional[LongTermMemory] = None


def get_long_term_memory() -> LongTermMemory:
    """Get or create long-term memory instance."""
    global _long_term_memory

    if _long_term_memory is None:
        _long_term_memory = LongTermMemory()

    return _long_term_memory
