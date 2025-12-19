from typing import Dict, Optional
from app.schemas.common import Context, Message, OrchestratorResponse, Language
from app.core.router import route_message
from app.core.agent_registry import AgentRegistry
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

            # TODO: Enrich context with memories (vector search)
            # context.relevant_memories = await self._fetch_relevant_memories(context)

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

            # TODO: Store conversation in long-term memory
            # await self._store_memory(context, response)

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

            # TODO: Generate final summary and store in database
            # await self._generate_session_summary(context)

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
