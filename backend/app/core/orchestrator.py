from typing import Dict, Optional
from app.schemas.common import Context, Message, OrchestratorResponse, Language
from app.core.router import route_message
from app.core.agent_registry import AgentRegistry
from app.memory.context_manager import get_context_manager
from app.models.conversation import Conversation
from app.db.session import SessionLocal
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Main orchestrator for the multi-agent system.

    This is the top-level component that:
    1. Manages conversation sessions
    2. Maintains context
    3. Coordinates with the router
    4. Handles memory integration (future)
    """

    def __init__(self):
        """Initialize the orchestrator."""
        self.registry = AgentRegistry()
        self.sessions: Dict[str, Context] = {}
        self.context_manager = get_context_manager()

    def create_session(
        self,
        user_id: Optional[str] = None,
        language: Language = Language.POLISH
    ) -> str:
        """
        Create a new conversation session.

        Args:
            user_id: Optional user identifier
            language: Preferred language

        Returns:
            str: Session ID
        """
        session_id = str(uuid.uuid4())

        context = Context(
            session_id=session_id,
            user_id=user_id,
            language=language,
            history=[],
            user_profile=None,
            relevant_memories=[],
            metadata={"created_at": datetime.utcnow().isoformat()}
        )

        self.sessions[session_id] = context
        logger.info(f"Created new session: {session_id}")

        return session_id

    async def process_message(
        self,
        session_id: str,
        user_message: str
    ) -> OrchestratorResponse:
        """
        Process a user message within a session.

        Args:
            session_id: Session identifier
            user_message: User's message

        Returns:
            OrchestratorResponse: System response
        """
        # Get or create context
        context = self.sessions.get(session_id)
        if not context:
            logger.warning(f"Session {session_id} not found, creating new one")
            session_id = self.create_session()
            context = self.sessions[session_id]

        try:
            # Add user message to history
            user_msg = Message(
                role="user",
                content=user_message,
                timestamp=datetime.utcnow()
            )
            context.history.append(user_msg)

            # Enrich context with relevant memories from vector search
            context = await self.context_manager.enrich_context(context, user_message)
            logger.debug(f"Enriched context with {len(context.relevant_memories)} memories")

            # Route to appropriate agent(s)
            response = await route_message(user_message, context)

            # Add assistant response to history
            assistant_msg = Message(
                role="assistant",
                content=response.content,
                timestamp=datetime.utcnow(),
                metadata=response.metadata
            )
            context.history.append(assistant_msg)

            # Update session
            self.sessions[session_id] = context

            # Store conversation in long-term memory
            await self.context_manager.store_conversation(
                context=context,
                user_message=user_message,
                assistant_response=response.content
            )

            return response

        except Exception as e:
            logger.error(f"Error processing message in session {session_id}: {e}", exc_info=True)
            raise

    def get_session(self, session_id: str) -> Optional[Context]:
        """Get session context."""
        return self.sessions.get(session_id)

    def end_session(self, session_id: str) -> bool:
        """
        End a conversation session.

        Args:
            session_id: Session to end

        Returns:
            bool: True if session existed and was ended
        """
        if session_id in self.sessions:
            context = self.sessions[session_id]

            # Save conversation to database
            self._save_conversation_to_db(context)

            del self.sessions[session_id]
            logger.info(f"Ended session: {session_id}")
            return True

        return False

    def get_session_history(self, session_id: str) -> list[Message]:
        """Get conversation history for a session."""
        context = self.sessions.get(session_id)
        return context.history if context else []

    def update_language(self, session_id: str, language: Language) -> bool:
        """Update language preference for a session."""
        context = self.sessions.get(session_id)
        if context:
            context.language = language
            logger.info(f"Updated session {session_id} language to {language.value}")
            return True
        return False

    def clear_expired_sessions(self, max_age_hours: int = 24) -> int:
        """
        Clear sessions older than max_age_hours.

        Args:
            max_age_hours: Maximum age in hours

        Returns:
            int: Number of sessions cleared
        """
        from datetime import timedelta

        now = datetime.utcnow()
        max_age = timedelta(hours=max_age_hours)
        expired_sessions = []

        for session_id, context in self.sessions.items():
            created_at_str = context.metadata.get("created_at")
            if created_at_str:
                created_at = datetime.fromisoformat(created_at_str)
                if now - created_at > max_age:
                    expired_sessions.append(session_id)

        for session_id in expired_sessions:
            del self.sessions[session_id]

        if expired_sessions:
            logger.info(f"Cleared {len(expired_sessions)} expired sessions")

        return len(expired_sessions)

    async def _fetch_relevant_memories(self, context: Context) -> list:
        """
        Fetch relevant memories from vector database.

        TODO: Implement vector search
        """
        # Placeholder for future implementation
        return []

    async def _store_memory(self, context: Context, response: OrchestratorResponse):
        """
        Store conversation in long-term memory.

        TODO: Implement memory storage with embeddings
        """
        # Placeholder for future implementation
        pass

    async def _generate_session_summary(self, context: Context):
        """
        Generate and store session summary.

        TODO: Implement session summarization
        """
        # Placeholder for future implementation
        pass

    def _save_conversation_to_db(self, context: Context):
        """
        Save conversation to database.

        Args:
            context: Conversation context to save
        """
        try:
            db = SessionLocal()

            # Extract agents used from context
            agents_used = []
            for msg in context.history:
                if msg.role == "assistant" and msg.metadata:
                    agent_id = msg.metadata.get("agent_id")
                    if agent_id and agent_id not in agents_used:
                        agents_used.append(agent_id)

            # Prepare messages for storage
            messages_json = [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "metadata": msg.metadata
                }
                for msg in context.history
            ]

            # Generate simple title from first user message
            title = None
            for msg in context.history:
                if msg.role == "user":
                    title = msg.content[:50] + ("..." if len(msg.content) > 50 else "")
                    break

            # Create conversation record
            conversation = Conversation(
                user_id=context.user_id,
                session_id=context.session_id,
                title=title,
                language=context.language.value,
                messages=messages_json,
                message_count=len(context.history),
                agents_used=agents_used,
                ended_at=datetime.utcnow()
            )

            db.add(conversation)
            db.commit()
            logger.info(f"Saved conversation {context.session_id} to database")

        except Exception as e:
            logger.error(f"Error saving conversation to database: {e}", exc_info=True)
            if db:
                db.rollback()
        finally:
            if db:
                db.close()

    def get_stats(self) -> Dict:
        """Get orchestrator statistics."""
        return {
            "active_sessions": len(self.sessions),
            "registered_agents": len(self.registry),
            "active_agents": len(self.registry.get_all_active())
        }


# Singleton instance
_orchestrator = Orchestrator()


def get_orchestrator() -> Orchestrator:
    """Get the singleton orchestrator instance."""
    return _orchestrator
