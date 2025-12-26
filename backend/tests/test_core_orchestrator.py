"""Tests for core orchestrator module."""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.core.orchestrator import Orchestrator
from app.schemas.common import Language, OrchestratorResponse
import uuid


class TestOrchestrator:
    """Test suite for Orchestrator class."""

    @pytest.fixture
    def orchestrator(self):
        """Create an orchestrator instance."""
        return Orchestrator()

    def test_orchestrator_initialization(self, orchestrator):
        """Test that orchestrator initializes correctly."""
        assert orchestrator is not None
        assert orchestrator.registry is not None
        assert orchestrator.session_store is not None
        assert orchestrator.context_manager is not None

    def test_create_session_default_language(self, orchestrator):
        """Test creating a session with default language."""
        session_id = orchestrator.create_session()

        assert session_id is not None
        assert isinstance(session_id, str)
        # Verify it's a valid UUID
        uuid.UUID(session_id)

    def test_create_session_custom_language(self, orchestrator):
        """Test creating a session with custom language."""
        session_id = orchestrator.create_session(language=Language.ENGLISH)

        assert session_id is not None
        context = orchestrator.session_store.get(session_id)
        assert context is not None
        assert context.language == Language.ENGLISH

    def test_create_session_with_user_id(self, orchestrator):
        """Test creating a session with user ID."""
        user_id = "test-user-123"
        session_id = orchestrator.create_session(user_id=user_id)

        assert session_id is not None
        context = orchestrator.session_store.get(session_id)
        assert context.user_id == user_id

    @pytest.mark.asyncio
    async def test_process_message_basic(self, orchestrator):
        """Test processing a basic message."""
        session_id = orchestrator.create_session()

        with patch('app.core.router.route_message', new_callable=AsyncMock) as mock_route:
            mock_route.return_value = OrchestratorResponse(
                response="Test response",
                agents_used=["general_agent"],
                confidence=0.95,
                intent="general_query"
            )

            response = await orchestrator.process_message(
                session_id=session_id,
                message="Hello, how are you?"
            )

            assert response is not None
            assert response.response == "Test response"
            assert "general_agent" in response.agents_used
            mock_route.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_message_updates_context(self, orchestrator):
        """Test that processing a message updates conversation history."""
        session_id = orchestrator.create_session()

        with patch('app.core.router.route_message', new_callable=AsyncMock) as mock_route:
            mock_route.return_value = OrchestratorResponse(
                response="Test response",
                agents_used=["general_agent"],
                confidence=0.95,
                intent="general_query"
            )

            await orchestrator.process_message(session_id, "Hello")

            context = orchestrator.session_store.get(session_id)
            assert len(context.conversation_history) > 0

    def test_get_session_info_exists(self, orchestrator):
        """Test getting session info for existing session."""
        session_id = orchestrator.create_session(user_id="test-user")

        info = orchestrator.get_session_info(session_id)

        assert info is not None
        assert info["session_id"] == session_id
        assert info["user_id"] == "test-user"
        assert "message_count" in info

    def test_get_session_info_not_exists(self, orchestrator):
        """Test getting session info for non-existent session."""
        fake_session_id = str(uuid.uuid4())

        info = orchestrator.get_session_info(fake_session_id)

        assert info is None

    def test_end_session(self, orchestrator):
        """Test ending a session."""
        session_id = orchestrator.create_session()

        # Verify session exists
        assert orchestrator.session_store.get(session_id) is not None

        # End session
        orchestrator.end_session(session_id)

        # Verify session is removed
        assert orchestrator.session_store.get(session_id) is None

    def test_multiple_sessions_independent(self, orchestrator):
        """Test that multiple sessions are independent."""
        session1 = orchestrator.create_session(user_id="user1")
        session2 = orchestrator.create_session(user_id="user2")

        assert session1 != session2

        context1 = orchestrator.session_store.get(session1)
        context2 = orchestrator.session_store.get(session2)

        assert context1.user_id == "user1"
        assert context2.user_id == "user2"

    @pytest.mark.asyncio
    async def test_process_message_invalid_session(self, orchestrator):
        """Test processing message with invalid session ID."""
        fake_session_id = str(uuid.uuid4())

        with pytest.raises(Exception):  # Should raise an error
            await orchestrator.process_message(fake_session_id, "Hello")

    def test_get_stats(self, orchestrator):
        """Test getting orchestrator statistics."""
        # Create a few sessions
        orchestrator.create_session()
        orchestrator.create_session()

        stats = orchestrator.get_stats()

        assert stats is not None
        assert "active_sessions" in stats
        assert "registered_agents" in stats
        assert stats["active_sessions"] >= 0

    @pytest.mark.asyncio
    async def test_conversation_history_accumulation(self, orchestrator):
        """Test that conversation history accumulates correctly."""
        session_id = orchestrator.create_session()

        with patch('app.core.router.route_message', new_callable=AsyncMock) as mock_route:
            mock_route.return_value = OrchestratorResponse(
                response="Response",
                agents_used=["general_agent"],
                confidence=0.95,
                intent="general_query"
            )

            # Send multiple messages
            await orchestrator.process_message(session_id, "Message 1")
            await orchestrator.process_message(session_id, "Message 2")
            await orchestrator.process_message(session_id, "Message 3")

            context = orchestrator.session_store.get(session_id)
            # Should have user messages + assistant responses
            assert len(context.conversation_history) >= 3

    def test_session_language_persistence(self, orchestrator):
        """Test that session language persists across operations."""
        session_id = orchestrator.create_session(language=Language.GERMAN)

        context = orchestrator.session_store.get(session_id)
        assert context.language == Language.GERMAN

        # Language should persist
        context_again = orchestrator.session_store.get(session_id)
        assert context_again.language == Language.GERMAN
