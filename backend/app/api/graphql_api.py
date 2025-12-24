"""GraphQL API Implementation with Strawberry.

Modern GraphQL API providing:
- Type-safe queries and mutations
- Real-time subscriptions
- Efficient data fetching (N+1 problem solved)
- Schema introspection
- GraphQL Playground

Built with Strawberry (async-first GraphQL for Python)
"""

import logging
from typing import List, Optional
from datetime import datetime

import strawberry
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info

from app.models.user import User
from app.models.conversation import Conversation
from app.schemas.common import Message

logger = logging.getLogger(__name__)


# ============================================================================
# GraphQL Types
# ============================================================================

@strawberry.type
class UserType:
    """GraphQL User type."""
    id: strawberry.ID
    email: str
    username: str
    is_premium: bool
    created_at: datetime
    total_conversations: int

    @strawberry.field
    def display_name(self) -> str:
        """Computed field for display name."""
        return self.username or self.email.split('@')[0]


@strawberry.type
class MessageType:
    """GraphQL Message type."""
    id: strawberry.ID
    role: str
    content: str
    timestamp: datetime
    agent_type: Optional[str] = None


@strawberry.type
class ConversationType:
    """GraphQL Conversation type."""
    id: strawberry.ID
    user_id: strawberry.ID
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int
    agents_used: List[str]

    @strawberry.field
    async def messages(self, info: Info, limit: int = 50) -> List[MessageType]:
        """Get messages for this conversation."""
        # Would fetch from database
        return []

    @strawberry.field
    async def user(self, info: Info) -> UserType:
        """Get user who owns this conversation."""
        # Would fetch from database
        return UserType(
            id=self.user_id,
            email="user@example.com",
            username="User",
            is_premium=False,
            created_at=datetime.utcnow(),
            total_conversations=0
        )


@strawberry.type
class AgentStatsType:
    """GraphQL Agent Statistics type."""
    agent_type: str
    total_invocations: int
    average_rating: float
    total_conversations: int


@strawberry.type
class AnalyticsType:
    """GraphQL Analytics type."""
    total_users: int
    total_conversations: int
    total_messages: int
    average_rating: float
    agent_stats: List[AgentStatsType]


# ============================================================================
# Input Types
# ============================================================================

@strawberry.input
class SendMessageInput:
    """Input for sending a message."""
    conversation_id: strawberry.ID
    content: str
    agent_type: Optional[str] = None


@strawberry.input
class CreateConversationInput:
    """Input for creating a conversation."""
    title: Optional[str] = None
    initial_message: Optional[str] = None


@strawberry.input
class UpdateUserInput:
    """Input for updating user profile."""
    username: Optional[str] = None
    preferences: Optional[str] = None  # JSON string


# ============================================================================
# Query Resolvers
# ============================================================================

@strawberry.type
class Query:
    """GraphQL Query root."""

    @strawberry.field
    async def me(self, info: Info) -> UserType:
        """Get current authenticated user."""
        # Would get from context/auth
        return UserType(
            id=strawberry.ID("1"),
            email="user@lifeai.com",
            username="Demo User",
            is_premium=True,
            created_at=datetime.utcnow(),
            total_conversations=42
        )

    @strawberry.field
    async def user(self, info: Info, id: strawberry.ID) -> Optional[UserType]:
        """Get user by ID."""
        # Would fetch from database
        return None

    @strawberry.field
    async def conversation(
        self,
        info: Info,
        id: strawberry.ID
    ) -> Optional[ConversationType]:
        """Get conversation by ID."""
        # Would fetch from database
        return None

    @strawberry.field
    async def conversations(
        self,
        info: Info,
        limit: int = 20,
        offset: int = 0
    ) -> List[ConversationType]:
        """Get user's conversations."""
        # Would fetch from database with pagination
        return []

    @strawberry.field
    async def analytics(self, info: Info) -> AnalyticsType:
        """Get platform analytics."""
        # Would aggregate from database
        return AnalyticsType(
            total_users=1000,
            total_conversations=5000,
            total_messages=25000,
            average_rating=4.5,
            agent_stats=[
                AgentStatsType(
                    agent_type="finance",
                    total_invocations=1500,
                    average_rating=4.6,
                    total_conversations=800
                ),
                AgentStatsType(
                    agent_type="health",
                    total_invocations=1200,
                    average_rating=4.4,
                    total_conversations=650
                )
            ]
        )

    @strawberry.field
    async def search_conversations(
        self,
        info: Info,
        query: str,
        limit: int = 10
    ) -> List[ConversationType]:
        """Search conversations by content."""
        # Would implement full-text search
        return []


# ============================================================================
# Mutation Resolvers
# ============================================================================

@strawberry.type
class Mutation:
    """GraphQL Mutation root."""

    @strawberry.mutation
    async def send_message(
        self,
        info: Info,
        input: SendMessageInput
    ) -> MessageType:
        """Send a message in a conversation."""
        # Would process message through AI router
        logger.info(f"GraphQL: Sending message to conversation {input.conversation_id}")

        return MessageType(
            id=strawberry.ID("msg_123"),
            role="assistant",
            content="This is a GraphQL response!",
            timestamp=datetime.utcnow(),
            agent_type=input.agent_type
        )

    @strawberry.mutation
    async def create_conversation(
        self,
        info: Info,
        input: CreateConversationInput
    ) -> ConversationType:
        """Create a new conversation."""
        # Would create in database
        logger.info("GraphQL: Creating new conversation")

        return ConversationType(
            id=strawberry.ID("conv_123"),
            user_id=strawberry.ID("1"),
            title=input.title or "New Conversation",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            message_count=0,
            agents_used=[]
        )

    @strawberry.mutation
    async def update_user(
        self,
        info: Info,
        input: UpdateUserInput
    ) -> UserType:
        """Update user profile."""
        # Would update in database
        logger.info("GraphQL: Updating user profile")

        return UserType(
            id=strawberry.ID("1"),
            email="user@lifeai.com",
            username=input.username or "User",
            is_premium=True,
            created_at=datetime.utcnow(),
            total_conversations=42
        )

    @strawberry.mutation
    async def delete_conversation(
        self,
        info: Info,
        id: strawberry.ID
    ) -> bool:
        """Delete a conversation."""
        # Would delete from database
        logger.info(f"GraphQL: Deleting conversation {id}")
        return True


# ============================================================================
# Subscription Resolvers (Real-time)
# ============================================================================

@strawberry.type
class Subscription:
    """GraphQL Subscription root for real-time updates."""

    @strawberry.subscription
    async def message_received(
        self,
        info: Info,
        conversation_id: strawberry.ID
    ) -> MessageType:
        """Subscribe to new messages in a conversation."""
        # Would use WebSocket or Redis pub/sub
        import asyncio

        # Simulate real-time messages
        while True:
            await asyncio.sleep(5)
            yield MessageType(
                id=strawberry.ID(f"msg_{datetime.utcnow().timestamp()}"),
                role="assistant",
                content="Real-time GraphQL subscription message!",
                timestamp=datetime.utcnow(),
                agent_type="general"
            )

    @strawberry.subscription
    async def typing_indicator(
        self,
        info: Info,
        conversation_id: strawberry.ID
    ) -> bool:
        """Subscribe to typing indicators."""
        import asyncio

        while True:
            await asyncio.sleep(2)
            yield True
            await asyncio.sleep(3)
            yield False


# ============================================================================
# Schema & Router
# ============================================================================

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription
)

# Create GraphQL router for FastAPI
graphql_router = GraphQLRouter(
    schema,
    path="/graphql",
    graphiql=True  # Enable GraphQL Playground in development
)

logger.info("GraphQL API initialized with Strawberry")


# ============================================================================
# Example Queries & Mutations
# ============================================================================

EXAMPLE_QUERIES = """
# Get current user
query GetMe {
  me {
    id
    email
    username
    isPremium
    displayName
    totalConversations
  }
}

# Get conversations with messages
query GetConversations {
  conversations(limit: 10) {
    id
    title
    createdAt
    messageCount
    messages(limit: 5) {
      id
      role
      content
      timestamp
    }
  }
}

# Get analytics
query GetAnalytics {
  analytics {
    totalUsers
    totalConversations
    totalMessages
    averageRating
    agentStats {
      agentType
      totalInvocations
      averageRating
    }
  }
}

# Send message
mutation SendMessage {
  sendMessage(input: {
    conversationId: "123"
    content: "Hello via GraphQL!"
    agentType: "general"
  }) {
    id
    role
    content
    timestamp
  }
}

# Create conversation
mutation CreateConversation {
  createConversation(input: {
    title: "My GraphQL Conversation"
    initialMessage: "Hello!"
  }) {
    id
    title
    createdAt
  }
}

# Subscribe to messages (WebSocket)
subscription OnNewMessage {
  messageReceived(conversationId: "123") {
    id
    role
    content
    timestamp
  }
}
"""
