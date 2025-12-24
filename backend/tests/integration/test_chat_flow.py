"""Integration tests for complete chat flow.

Tests the end-to-end user journey through the chat system.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.user import User
from app.models.conversation import Conversation


@pytest.mark.asyncio
@pytest.mark.integration
async def test_complete_chat_flow(
    async_client: AsyncClient,
    test_user: User,
    auth_headers: dict
):
    """
    Test complete chat flow from start to end.

    Steps:
    1. Start new chat session
    2. Send multiple messages
    3. Verify agent responses
    4. End session
    5. Verify conversation saved
    """
    # 1. Start new chat session
    response = await async_client.post(
        "/chat/start",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    session_id = data["session_id"]

    # 2. Send first message
    response = await async_client.post(
        "/chat/message",
        json={
            "session_id": session_id,
            "content": "Jak mogę zaoszczędzić 1000 zł miesięcznie?"
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert len(data["reply"]) > 0
    assert data["modality"] == "text"

    # 3. Send follow-up message
    response = await async_client.post(
        "/chat/message",
        json={
            "session_id": session_id,
            "content": "Jakie są najlepsze sposoby na oszczędzanie?"
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data

    # 4. End session
    response = await async_client.post(
        f"/chat/end",
        params={"session_id": session_id},
        headers=auth_headers
    )
    assert response.status_code == 200

    # 5. Verify conversation was saved
    response = await async_client.get(
        "/chat/conversations",
        headers=auth_headers
    )
    assert response.status_code == 200
    conversations = response.json()
    assert len(conversations) > 0

    # Find our conversation
    our_conv = next(
        (c for c in conversations if c["session_id"] == session_id),
        None
    )
    assert our_conv is not None
    assert our_conv["message_count"] >= 4  # 2 user + 2 assistant
    assert "finance" in our_conv.get("agents_used", [])


@pytest.mark.asyncio
@pytest.mark.integration
async def test_multimodal_voice_flow(
    async_client: AsyncClient,
    test_user: User,
    auth_headers: dict
):
    """Test voice input flow."""
    # Note: This is a simplified test
    # In real scenario, you'd upload actual audio file

    # Start session
    response = await async_client.post(
        "/chat/start",
        headers=auth_headers
    )
    session_id = response.json()["session_id"]

    # Mock voice message (in reality, would transcribe audio first)
    response = await async_client.post(
        "/chat/message",
        json={
            "session_id": session_id,
            "content": "Jak schudnąć 5 kg?"
        },
        headers=auth_headers
    )

    assert response.status_code == 200
    assert "reply" in response.json()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_rate_limiting(
    async_client: AsyncClient,
    auth_headers: dict
):
    """Test that rate limiting works correctly."""
    # Start session
    response = await async_client.post(
        "/chat/start",
        headers=auth_headers
    )
    session_id = response.json()["session_id"]

    # Send messages rapidly (should hit rate limit)
    responses = []
    for i in range(65):  # Rate limit is 60/min
        response = await async_client.post(
            "/chat/message",
            json={
                "session_id": session_id,
                "content": f"Test message {i}"
            },
            headers=auth_headers
        )
        responses.append(response)

    # First 60 should succeed
    assert all(r.status_code == 200 for r in responses[:60])

    # Next ones should be rate limited
    assert any(r.status_code == 429 for r in responses[60:])


@pytest.mark.asyncio
@pytest.mark.integration
async def test_invalid_input_sanitization(
    async_client: AsyncClient,
    auth_headers: dict
):
    """Test that dangerous input is sanitized."""
    # Start session
    response = await async_client.post(
        "/chat/start",
        headers=auth_headers
    )
    session_id = response.json()["session_id"]

    # Try to send XSS attack
    dangerous_inputs = [
        "<script>alert('XSS')</script>Normalna treść",
        "javascript:alert('XSS')",
        "<img src=x onerror=alert('XSS')>",
    ]

    for dangerous_input in dangerous_inputs:
        response = await async_client.post(
            "/chat/message",
            json={
                "session_id": session_id,
                "content": dangerous_input
            },
            headers=auth_headers
        )

        # Should either reject (400) or sanitize
        if response.status_code == 200:
            # If accepted, verify it was sanitized
            # (no script tags in any responses)
            assert "<script" not in response.text.lower()
        else:
            assert response.status_code == 400


@pytest.mark.asyncio
@pytest.mark.integration
async def test_multi_agent_collaboration(
    async_client: AsyncClient,
    auth_headers: dict
):
    """Test that multi-agent queries work correctly."""
    # Start session
    response = await async_client.post(
        "/chat/start",
        headers=auth_headers
    )
    session_id = response.json()["session_id"]

    # Send multi-domain query
    response = await async_client.post(
        "/chat/message",
        json={
            "session_id": session_id,
            "content": "Chcę schudnąć 5kg i zaoszczędzić na siłownię"
        },
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Should have both health and finance agents
    # (This depends on implementation details)
    assert "reply" in data
    assert len(data["reply"]) > 100  # Multi-agent response should be comprehensive


# Fixtures
@pytest.fixture
async def test_user(db: AsyncSession):
    """Create a test user."""
    from app.security.auth import hash_password

    user = User(
        email="test@example.com",
        username="testuser",
        password_hash=hash_password("testpassword123"),
        is_active=True,
        is_verified=True
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


@pytest.fixture
async def auth_headers(async_client: AsyncClient, test_user: User):
    """Get authentication headers for test user."""
    # Login
    response = await async_client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )

    assert response.status_code == 200
    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}
