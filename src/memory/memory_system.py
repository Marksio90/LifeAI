"""
Memory System (Layer 4)
Manages short-term and long-term memory for the platform
- Short-term: Current conversation context
- Long-term: User history, patterns, preferences
- Learning: Feedback loop for continuous improvement
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from loguru import logger
from dataclasses import dataclass
import json

from openai import AsyncOpenAI
from config import settings


@dataclass
class Message:
    """Single message in conversation"""
    role: str  # user, assistant, system
    content: str
    timestamp: datetime
    metadata: Dict[str, Any]


@dataclass
class ConversationSession:
    """A conversation session"""
    session_id: str
    user_id: str
    messages: List[Message]
    started_at: datetime
    last_activity: datetime
    context: Dict[str, Any]


class MemorySystem:
    """
    Manages all memory operations for the platform
    """

    def __init__(
        self,
        redis_client=None,
        vector_db=None,
        postgres_db=None
    ):
        self.redis_client = redis_client  # Short-term memory
        self.vector_db = vector_db  # Semantic search
        self.postgres_db = postgres_db  # Long-term storage

        # In-memory cache for active sessions
        self.active_sessions: Dict[str, ConversationSession] = {}

        # OpenAI client for embeddings
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

        logger.info("Memory System initialized")

    async def create_session(
        self,
        session_id: str,
        user_id: str,
        initial_context: Optional[Dict[str, Any]] = None
    ) -> ConversationSession:
        """
        Create new conversation session
        """
        session = ConversationSession(
            session_id=session_id,
            user_id=user_id,
            messages=[],
            started_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
            context=initial_context or {}
        )

        self.active_sessions[session_id] = session
        logger.info(f"Created session {session_id} for user {user_id}")

        return session

    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Add message to conversation session
        """
        if session_id not in self.active_sessions:
            logger.warning(f"Session {session_id} not found, creating new")
            await self.create_session(session_id, "unknown")

        session = self.active_sessions[session_id]

        message = Message(
            role=role,
            content=content,
            timestamp=datetime.utcnow(),
            metadata=metadata or {}
        )

        session.messages.append(message)
        session.last_activity = datetime.utcnow()

        # Save to Redis for quick access
        if self.redis_client:
            await self._save_to_redis(session)

        # Create embedding for semantic search
        if self.vector_db and len(content) > 10:
            await self._store_embedding(session_id, content, message.timestamp)

        logger.debug(f"Added {role} message to session {session_id}")

    async def get_context(
        self,
        session_id: str,
        max_messages: int = 10
    ) -> List[Dict[str, str]]:
        """
        Get conversation context for LLM
        Returns messages in OpenAI format
        """
        if session_id not in self.active_sessions:
            return []

        session = self.active_sessions[session_id]
        recent_messages = session.messages[-max_messages:]

        return [
            {
                "role": msg.role,
                "content": msg.content
            }
            for msg in recent_messages
        ]

    async def search_similar_conversations(
        self,
        query: str,
        user_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for similar past conversations
        Uses vector similarity search
        """
        if not self.vector_db:
            return []

        try:
            # Create embedding for query
            embedding = await self._create_embedding(query)

            # Search in vector DB
            # This is a placeholder - actual implementation depends on vector DB choice
            results = []

            return results

        except Exception as e:
            logger.error(f"Error searching conversations: {str(e)}")
            return []

    async def summarize_session(
        self,
        session_id: str
    ) -> Optional[str]:
        """
        Create summary of conversation session
        """
        if session_id not in self.active_sessions:
            return None

        session = self.active_sessions[session_id]

        if len(session.messages) < 3:
            return "Short conversation, no summary needed"

        try:
            # Build conversation text
            conversation = "\n".join([
                f"{msg.role}: {msg.content}"
                for msg in session.messages
            ])

            # Use LLM to summarize
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Use cheaper model for summaries
                messages=[
                    {
                        "role": "system",
                        "content": "Summarize this conversation concisely, focusing on key points, decisions, and insights."
                    },
                    {
                        "role": "user",
                        "content": conversation
                    }
                ],
                temperature=0.3,
                max_tokens=300
            )

            summary = response.choices[0].message.content
            return summary

        except Exception as e:
            logger.error(f"Error summarizing session: {str(e)}")
            return None

    async def store_feedback(
        self,
        session_id: str,
        message_index: int,
        feedback: Dict[str, Any]
    ):
        """
        Store user feedback for learning
        """
        if session_id not in self.active_sessions:
            return

        session = self.active_sessions[session_id]

        if message_index < len(session.messages):
            message = session.messages[message_index]
            if "feedback" not in message.metadata:
                message.metadata["feedback"] = []
            message.metadata["feedback"].append({
                "timestamp": datetime.utcnow().isoformat(),
                "feedback": feedback
            })

            logger.info(f"Stored feedback for session {session_id}")

            # Save to long-term storage
            if self.postgres_db:
                await self._save_feedback_to_db(session_id, message_index, feedback)

    async def get_user_patterns(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Analyze user patterns from history
        """
        # TODO: Implement pattern analysis
        # This will analyze:
        # - Common topics
        # - Emotional patterns
        # - Decision patterns
        # - Time patterns (when most active)
        # - Response preferences

        return {
            "common_topics": [],
            "emotional_patterns": {},
            "decision_patterns": {},
            "preferences": {}
        }

    async def cleanup_old_sessions(self, days: int = 7):
        """
        Clean up old inactive sessions
        """
        cutoff = datetime.utcnow() - timedelta(days=days)

        sessions_to_remove = []
        for session_id, session in self.active_sessions.items():
            if session.last_activity < cutoff:
                # Save to long-term storage first
                await self._archive_session(session)
                sessions_to_remove.append(session_id)

        for session_id in sessions_to_remove:
            del self.active_sessions[session_id]

        if sessions_to_remove:
            logger.info(f"Cleaned up {len(sessions_to_remove)} old sessions")

    async def _create_embedding(self, text: str) -> List[float]:
        """Create embedding for text"""
        try:
            response = await self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error creating embedding: {str(e)}")
            return []

    async def _store_embedding(
        self,
        session_id: str,
        content: str,
        timestamp: datetime
    ):
        """Store embedding in vector database"""
        # TODO: Implement vector DB storage
        pass

    async def _save_to_redis(self, session: ConversationSession):
        """Save session to Redis"""
        # TODO: Implement Redis storage
        pass

    async def _save_feedback_to_db(
        self,
        session_id: str,
        message_index: int,
        feedback: Dict[str, Any]
    ):
        """Save feedback to PostgreSQL"""
        # TODO: Implement database storage
        pass

    async def _archive_session(self, session: ConversationSession):
        """Archive session to long-term storage"""
        # TODO: Implement archiving
        logger.debug(f"Archiving session {session.session_id}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        total_messages = sum(
            len(session.messages)
            for session in self.active_sessions.values()
        )

        return {
            "active_sessions": len(self.active_sessions),
            "total_messages": total_messages,
            "avg_messages_per_session": (
                total_messages / len(self.active_sessions)
                if self.active_sessions else 0
            )
        }
