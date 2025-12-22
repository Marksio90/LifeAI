"""Tests for chat endpoints."""
import pytest
from fastapi import status
from unittest.mock import Mock, patch, AsyncMock
from app.schemas.common import Language


class TestChatSession:
    """Test chat session management."""

    @patch('app.api.chat.get_orchestrator')
    def test_start_chat_success(self, mock_get_orch, client, auth_headers):
        """Test starting a new chat session."""
        mock_orch = Mock()
        mock_orch.create_session.return_value = "session-123"
        mock_get_orch.return_value = mock_orch

        response = client.post(
            "/chat/start",
            headers=auth_headers,
            json={"language": "polish"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["session_id"] == "session-123"
        assert data["language"] == "polish"
        assert "message" in data

    @patch('app.api.chat.get_orchestrator')
    def test_start_chat_default_language(self, mock_get_orch, client, auth_headers):
        """Test starting chat with default language."""
        mock_orch = Mock()
        mock_orch.create_session.return_value = "session-456"
        mock_get_orch.return_value = mock_orch

        response = client.post("/chat/start", headers=auth_headers, json={})

        assert response.status_code == status.HTTP_200_OK
        # Should use default POLISH language
        mock_orch.create_session.assert_called_once()
        call_args = mock_orch.create_session.call_args
        assert call_args.kwargs.get("language") == Language.POLISH

    @patch('app.api.chat.get_orchestrator')
    def test_start_chat_orchestrator_error(self, mock_get_orch, client, auth_headers):
        """Test error handling when orchestrator fails."""
        mock_orch = Mock()
        mock_orch.create_session.side_effect = Exception("Orchestrator error")
        mock_get_orch.return_value = mock_orch

        response = client.post("/chat/start", headers=auth_headers, json={})

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    @patch('app.api.chat.get_orchestrator')
    def test_end_chat_success(self, mock_get_orch, client):
        """Test ending a chat session."""
        mock_orch = Mock()
        mock_orch.end_session.return_value = True
        mock_get_orch.return_value = mock_orch

        response = client.post(
            "/chat/end",
            json={"session_id": "session-123"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        mock_orch.end_session.assert_called_once_with("session-123")

    @patch('app.api.chat.get_orchestrator')
    def test_end_chat_session_not_found(self, mock_get_orch, client):
        """Test ending non-existent session."""
        mock_orch = Mock()
        mock_orch.end_session.return_value = False
        mock_get_orch.return_value = mock_orch

        response = client.post(
            "/chat/end",
            json={"session_id": "invalid-session"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestChatMessage:
    """Test chat message handling."""

    @patch('app.api.chat.get_orchestrator')
    async def test_send_message_success(self, mock_get_orch, client):
        """Test sending a message."""
        # Create mock response
        mock_response = Mock()
        mock_response.content = "Hello! How can I help you?"

        mock_agent_response = Mock()
        mock_agent_response.agent_id = "general_agent"
        mock_response.agent_responses = [mock_agent_response]
        mock_response.metadata = {
            "routing_type": "single",
            "confidence": 0.95
        }

        mock_orch = Mock()
        mock_orch.process_message = AsyncMock(return_value=mock_response)
        mock_get_orch.return_value = mock_orch

        response = client.post(
            "/chat/message",
            json={
                "session_id": "session-123",
                "message": "Hello"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["reply"] == "Hello! How can I help you?"
        assert "metadata" in data
        assert data["metadata"]["agents_used"] == ["general_agent"]
        assert data["metadata"]["routing_type"] == "single"

    def test_send_message_empty_text(self, client):
        """Test sending empty message."""
        response = client.post(
            "/chat/message",
            json={
                "session_id": "session-123",
                "message": ""
            }
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @patch('app.api.chat.get_orchestrator')
    async def test_send_message_orchestrator_error(self, mock_get_orch, client):
        """Test error handling when processing fails."""
        mock_orch = Mock()
        mock_orch.process_message = AsyncMock(side_effect=Exception("Processing error"))
        mock_get_orch.return_value = mock_orch

        response = client.post(
            "/chat/message",
            json={
                "session_id": "session-123",
                "message": "Hello"
            }
        )

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


class TestSessionInfo:
    """Test session information retrieval."""

    @patch('app.api.chat.get_orchestrator')
    def test_get_session_info_success(self, mock_get_orch, client):
        """Test getting session information."""
        mock_context = Mock()
        mock_context.session_id = "session-123"
        mock_context.language = Language.POLISH
        mock_context.history = [Mock(), Mock(), Mock()]  # 3 messages
        mock_context.metadata = {"created_at": "2025-01-01T12:00:00"}

        mock_orch = Mock()
        mock_orch.get_session.return_value = mock_context
        mock_get_orch.return_value = mock_orch

        response = client.get("/chat/session/session-123")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["session_id"] == "session-123"
        assert data["language"] == "polish"
        assert data["message_count"] == 3
        assert data["created_at"] == "2025-01-01T12:00:00"

    @patch('app.api.chat.get_orchestrator')
    def test_get_session_info_not_found(self, mock_get_orch, client):
        """Test getting non-existent session."""
        mock_orch = Mock()
        mock_orch.get_session.return_value = None
        mock_get_orch.return_value = mock_orch

        response = client.get("/chat/session/invalid-session")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestChatStats:
    """Test orchestrator statistics."""

    @patch('app.api.chat.get_orchestrator')
    def test_get_stats_success(self, mock_get_orch, client):
        """Test getting orchestrator stats."""
        mock_stats = {
            "active_sessions": 5,
            "total_agents": 3,
            "messages_processed": 150
        }

        mock_orch = Mock()
        mock_orch.get_stats.return_value = mock_stats
        mock_get_orch.return_value = mock_orch

        response = client.get("/chat/stats")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["active_sessions"] == 5
        assert data["total_agents"] == 3


class TestConversationRetrieval:
    """Test conversation retrieval endpoints."""

    def test_get_conversation_success(self, client, auth_headers, db_session, test_user):
        """Test getting a conversation by ID."""
        from app.models.conversation import Conversation
        from datetime import datetime

        # Create test conversation
        conversation = Conversation(
            session_id="session-123",
            user_id=str(test_user.id),
            title="Test Conversation",
            language="polish",
            messages=[
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"}
            ],
            message_count=2,
            agents_used=["general_agent"],
            summary="A test conversation",
            main_topics=["greeting"]
        )
        db_session.add(conversation)
        db_session.commit()

        response = client.get(
            f"/chat/conversation/{conversation.id}",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Test Conversation"
        assert data["message_count"] == 2
        assert len(data["messages"]) == 2
        assert data["agents_used"] == ["general_agent"]

    def test_get_conversation_not_found(self, client, auth_headers):
        """Test getting non-existent conversation."""
        response = client.get(
            "/chat/conversation/invalid-id",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_conversation_wrong_user(self, client, auth_headers, db_session, test_user):
        """Test getting conversation from different user."""
        from app.models.conversation import Conversation

        # Create conversation for different user
        conversation = Conversation(
            session_id="session-456",
            user_id="different-user-id",
            title="Other User's Conversation",
            language="english",
            message_count=1
        )
        db_session.add(conversation)
        db_session.commit()

        response = client.get(
            f"/chat/conversation/{conversation.id}",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestConversationResume:
    """Test conversation resume functionality."""

    @patch('app.api.chat.get_orchestrator')
    def test_resume_conversation_success(self, mock_get_orch, client, auth_headers, db_session, test_user):
        """Test resuming a previous conversation."""
        from app.models.conversation import Conversation

        # Create test conversation
        conversation = Conversation(
            session_id="old-session",
            user_id=str(test_user.id),
            title="Previous Chat",
            language="polish",
            messages=[
                {
                    "role": "user",
                    "content": "What's the weather?",
                    "timestamp": "2025-01-01T12:00:00"
                },
                {
                    "role": "assistant",
                    "content": "It's sunny!",
                    "timestamp": "2025-01-01T12:00:05",
                    "metadata": {}
                }
            ],
            message_count=2
        )
        db_session.add(conversation)
        db_session.commit()

        # Mock orchestrator
        mock_context = Mock()
        mock_context.history = []

        mock_orch = Mock()
        mock_orch.create_session.return_value = "new-session-123"
        mock_orch.get_session.return_value = mock_context
        mock_get_orch.return_value = mock_orch

        response = client.post(
            f"/chat/resume/{conversation.id}",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["session_id"] == "new-session-123"
        assert data["conversation_id"] == str(conversation.id)
        assert data["message_count"] == 2
        assert "Previous Chat" in data["message"]

    def test_resume_conversation_not_found(self, client, auth_headers):
        """Test resuming non-existent conversation."""
        response = client.post(
            "/chat/resume/invalid-id",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
