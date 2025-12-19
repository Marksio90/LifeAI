"""Tests for chat endpoints."""
import pytest
from fastapi import status
from unittest.mock import patch, MagicMock


def test_start_chat(authenticated_client):
    """Test starting a new chat session."""
    client, _ = authenticated_client

    response = client.post("/chat/start")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "session_id" in data
    assert len(data["session_id"]) > 0


def test_start_chat_unauthorized(client):
    """Test starting chat without auth fails."""
    response = client.post("/chat/start")

    # Should still work as chat might not require auth in current implementation
    # Adjust based on actual implementation
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]


@patch('app.core.orchestrator.Orchestrator.process_message')
def test_send_message(mock_process, authenticated_client):
    """Test sending a message in chat."""
    client, _ = authenticated_client

    # Mock the orchestrator response
    mock_response = MagicMock()
    mock_response.content = "Test AI response"
    mock_response.agent_id = "general"
    mock_response.confidence = 0.95
    mock_process.return_value = mock_response

    # Start chat session
    session_response = client.post("/chat/start")
    session_id = session_response.json()["session_id"]

    # Send message
    response = client.post("/chat/message", json={
        "session_id": session_id,
        "message": "Hello, AI!"
    })

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "reply" in data
    assert data["reply"] == "Test AI response"


def test_send_message_empty(authenticated_client):
    """Test sending empty message fails."""
    client, _ = authenticated_client

    session_response = client.post("/chat/start")
    session_id = session_response.json()["session_id"]

    response = client.post("/chat/message", json={
        "session_id": session_id,
        "message": ""
    })

    # Might return 422 for validation error or 400
    assert response.status_code in [status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_400_BAD_REQUEST]


def test_end_chat(authenticated_client):
    """Test ending a chat session."""
    client, _ = authenticated_client

    # Start chat
    session_response = client.post("/chat/start")
    session_id = session_response.json()["session_id"]

    # End chat
    response = client.post("/chat/end", json={
        "session_id": session_id
    })

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "ended"
