"""Tests for timeline endpoints."""
import pytest
from fastapi import status
from datetime import datetime, timedelta


class TestTimelineList:
    """Test timeline listing with filters."""

    def test_get_timeline_empty(self, client, auth_headers, db_session, test_user):
        """Test getting timeline when no conversations exist."""
        response = client.get("/timeline/", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_timeline_with_conversations(self, client, auth_headers, db_session, test_user):
        """Test getting timeline with conversations."""
        from app.models.conversation import Conversation

        # Create test conversations
        conv1 = Conversation(
            session_id="session-1",
            user_id=str(test_user.id),
            title="First Conversation",
            language="polish",
            message_count=5,
            agents_used=["general_agent"],
            summary="Test summary 1",
            main_topics=["topic1"]
        )
        conv2 = Conversation(
            session_id="session-2",
            user_id=str(test_user.id),
            title="Second Conversation",
            language="english",
            message_count=3,
            agents_used=["health_agent"],
            summary="Test summary 2",
            main_topics=["topic2"]
        )
        db_session.add(conv1)
        db_session.add(conv2)
        db_session.commit()

        response = client.get("/timeline/", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        assert data[0]["title"] == "Second Conversation"  # Most recent first
        assert data[1]["title"] == "First Conversation"

    def test_get_timeline_search_by_title(self, client, auth_headers, db_session, test_user):
        """Test searching timeline by title."""
        from app.models.conversation import Conversation

        conv1 = Conversation(
            session_id="session-1",
            user_id=str(test_user.id),
            title="Python Tutorial",
            language="polish",
            message_count=5
        )
        conv2 = Conversation(
            session_id="session-2",
            user_id=str(test_user.id),
            title="JavaScript Guide",
            language="polish",
            message_count=3
        )
        db_session.add(conv1)
        db_session.add(conv2)
        db_session.commit()

        response = client.get(
            "/timeline/",
            headers=auth_headers,
            params={"search": "Python"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Python Tutorial"

    def test_get_timeline_search_case_insensitive(self, client, auth_headers, db_session, test_user):
        """Test search is case-insensitive."""
        from app.models.conversation import Conversation

        conv = Conversation(
            session_id="session-1",
            user_id=str(test_user.id),
            title="React Tutorial",
            language="polish",
            message_count=5
        )
        db_session.add(conv)
        db_session.commit()

        response = client.get(
            "/timeline/",
            headers=auth_headers,
            params={"search": "react"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "React Tutorial"

    def test_get_timeline_filter_by_days(self, client, auth_headers, db_session, test_user):
        """Test filtering by days."""
        from app.models.conversation import Conversation

        # Create old conversation
        old_conv = Conversation(
            session_id="session-old",
            user_id=str(test_user.id),
            title="Old Conversation",
            language="polish",
            message_count=2
        )
        old_conv.created_at = datetime.utcnow() - timedelta(days=30)

        # Create recent conversation
        recent_conv = Conversation(
            session_id="session-recent",
            user_id=str(test_user.id),
            title="Recent Conversation",
            language="polish",
            message_count=3
        )

        db_session.add(old_conv)
        db_session.add(recent_conv)
        db_session.commit()

        # Filter for last 7 days
        response = client.get(
            "/timeline/",
            headers=auth_headers,
            params={"days": 7}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Recent Conversation"

    def test_get_timeline_sort_by_message_count(self, client, auth_headers, db_session, test_user):
        """Test sorting by message count."""
        from app.models.conversation import Conversation

        conv1 = Conversation(
            session_id="session-1",
            user_id=str(test_user.id),
            title="Small Chat",
            language="polish",
            message_count=2
        )
        conv2 = Conversation(
            session_id="session-2",
            user_id=str(test_user.id),
            title="Big Chat",
            language="polish",
            message_count=20
        )
        db_session.add(conv1)
        db_session.add(conv2)
        db_session.commit()

        response = client.get(
            "/timeline/",
            headers=auth_headers,
            params={"sort_by": "message_count", "sort_order": "desc"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data[0]["title"] == "Big Chat"
        assert data[1]["title"] == "Small Chat"

    def test_get_timeline_sort_ascending(self, client, auth_headers, db_session, test_user):
        """Test ascending sort order."""
        from app.models.conversation import Conversation

        conv1 = Conversation(
            session_id="session-1",
            user_id=str(test_user.id),
            title="A Chat",
            language="polish",
            message_count=1
        )
        conv2 = Conversation(
            session_id="session-2",
            user_id=str(test_user.id),
            title="B Chat",
            language="polish",
            message_count=1
        )
        db_session.add(conv1)
        db_session.add(conv2)
        db_session.commit()

        response = client.get(
            "/timeline/",
            headers=auth_headers,
            params={"sort_by": "title", "sort_order": "asc"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data[0]["title"] == "A Chat"
        assert data[1]["title"] == "B Chat"

    def test_get_timeline_pagination(self, client, auth_headers, db_session, test_user):
        """Test pagination with limit and offset."""
        from app.models.conversation import Conversation

        # Create 5 conversations
        for i in range(5):
            conv = Conversation(
                session_id=f"session-{i}",
                user_id=str(test_user.id),
                title=f"Conversation {i}",
                language="polish",
                message_count=1
            )
            db_session.add(conv)
        db_session.commit()

        # Get first 2
        response = client.get(
            "/timeline/",
            headers=auth_headers,
            params={"limit": 2, "offset": 0}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2

        # Get next 2
        response = client.get(
            "/timeline/",
            headers=auth_headers,
            params={"limit": 2, "offset": 2}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2

    def test_get_timeline_only_own_conversations(self, client, auth_headers, db_session, test_user):
        """Test that users only see their own conversations."""
        from app.models.conversation import Conversation

        # User's conversation
        user_conv = Conversation(
            session_id="session-user",
            user_id=str(test_user.id),
            title="My Conversation",
            language="polish",
            message_count=1
        )

        # Other user's conversation
        other_conv = Conversation(
            session_id="session-other",
            user_id="other-user-id",
            title="Other Conversation",
            language="polish",
            message_count=1
        )

        db_session.add(user_conv)
        db_session.add(other_conv)
        db_session.commit()

        response = client.get("/timeline/", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "My Conversation"


class TestConversationDetail:
    """Test conversation detail endpoint."""

    def test_get_conversation_detail(self, client, db_session, test_user):
        """Test getting detailed conversation."""
        from app.models.conversation import Conversation

        conversation = Conversation(
            session_id="session-123",
            user_id=str(test_user.id),
            title="Test Conversation",
            language="polish",
            messages=[
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi!"}
            ],
            message_count=2,
            agents_used=["general_agent"],
            summary="Test summary",
            main_topics=["greeting"]
        )
        db_session.add(conversation)
        db_session.commit()

        response = client.get(f"/timeline/conversation/{conversation.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Test Conversation"
        assert len(data["messages"]) == 2
        assert data["message_count"] == 2

    def test_get_conversation_detail_not_found(self, client):
        """Test getting non-existent conversation."""
        response = client.get("/timeline/conversation/invalid-id")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestConversationDelete:
    """Test conversation deletion."""

    def test_delete_conversation_success(self, client, db_session, test_user):
        """Test deleting a conversation."""
        from app.models.conversation import Conversation

        conversation = Conversation(
            session_id="session-123",
            user_id=str(test_user.id),
            title="To Delete",
            language="polish",
            message_count=1
        )
        db_session.add(conversation)
        db_session.commit()
        conv_id = conversation.id

        response = client.delete(f"/timeline/conversation/{conv_id}")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["success"] is True

        # Verify deletion
        deleted_conv = db_session.query(Conversation).filter(
            Conversation.id == conv_id
        ).first()
        assert deleted_conv is None

    def test_delete_conversation_not_found(self, client):
        """Test deleting non-existent conversation."""
        response = client.delete("/timeline/conversation/invalid-id")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUserStats:
    """Test user statistics endpoint."""

    def test_get_user_stats(self, client, db_session, test_user):
        """Test getting user statistics."""
        from app.models.conversation import Conversation

        # Create conversations with different agents
        conv1 = Conversation(
            session_id="session-1",
            user_id=str(test_user.id),
            title="Conv 1",
            language="polish",
            message_count=10,
            agents_used=["general_agent", "health_agent"]
        )
        conv2 = Conversation(
            session_id="session-2",
            user_id=str(test_user.id),
            title="Conv 2",
            language="polish",
            message_count=5,
            agents_used=["general_agent"]
        )
        db_session.add(conv1)
        db_session.add(conv2)
        db_session.commit()

        response = client.get(f"/timeline/stats/{test_user.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_conversations"] == 2
        assert data["total_messages"] == 15
        assert "agent_usage" in data
        assert data["agent_usage"]["general_agent"] == 2
        assert data["agent_usage"]["health_agent"] == 1

    def test_get_user_stats_recent_activity(self, client, db_session, test_user):
        """Test recent activity in stats."""
        from app.models.conversation import Conversation

        # Create old conversation
        old_conv = Conversation(
            session_id="session-old",
            user_id=str(test_user.id),
            title="Old",
            language="polish",
            message_count=5
        )
        old_conv.created_at = datetime.utcnow() - timedelta(days=30)

        # Create recent conversation
        recent_conv = Conversation(
            session_id="session-recent",
            user_id=str(test_user.id),
            title="Recent",
            language="polish",
            message_count=3
        )

        db_session.add(old_conv)
        db_session.add(recent_conv)
        db_session.commit()

        response = client.get(f"/timeline/stats/{test_user.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_conversations"] == 2
        assert data["recent_activity"]["conversations_last_7_days"] == 1
        assert data["recent_activity"]["messages_last_7_days"] == 3

    def test_get_user_stats_most_used_agents(self, client, db_session, test_user):
        """Test most used agents in stats."""
        from app.models.conversation import Conversation

        # Create conversations with different agent usage
        for i in range(5):
            conv = Conversation(
                session_id=f"session-{i}",
                user_id=str(test_user.id),
                title=f"Conv {i}",
                language="polish",
                message_count=1,
                agents_used=["general_agent"]
            )
            db_session.add(conv)

        # One conversation with health agent
        health_conv = Conversation(
            session_id="session-health",
            user_id=str(test_user.id),
            title="Health",
            language="polish",
            message_count=1,
            agents_used=["health_agent"]
        )
        db_session.add(health_conv)
        db_session.commit()

        response = client.get(f"/timeline/stats/{test_user.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        most_used = data["most_used_agents"]
        assert len(most_used) > 0
        # general_agent should be first
        assert most_used[0][0] == "general_agent"
        assert most_used[0][1] == 5
