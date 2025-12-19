from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Float, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.base import Base


class AgentInteraction(Base):
    """Track all agent interactions for analytics and learning"""
    __tablename__ = "agent_interactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)

    # Agent information
    agent_id = Column(String(100), nullable=False, index=True)
    agent_type = Column(String(50), nullable=False, index=True)

    # Interaction details
    user_message = Column(Text, nullable=False)
    agent_response = Column(Text, nullable=False)

    # Intent and routing
    intent_type = Column(String(100), nullable=True)
    intent_confidence = Column(Float, nullable=True)
    routing_type = Column(String(50), nullable=True)  # single_agent, multi_agent

    # Performance metrics
    response_time_ms = Column(Float, nullable=True)  # How long did it take
    tokens_used = Column(JSON, nullable=True)  # {prompt: X, completion: Y, total: Z}

    # Context
    context_enriched = Column(JSON, nullable=True)  # What memories were used

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    conversation = relationship("Conversation", back_populates="agent_interactions")

    def __repr__(self):
        return f"<AgentInteraction(id={self.id}, agent_id={self.agent_id})>"

    def to_dict(self):
        return {
            "id": str(self.id),
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "intent_type": self.intent_type,
            "intent_confidence": self.intent_confidence,
            "routing_type": self.routing_type,
            "response_time_ms": self.response_time_ms,
            "tokens_used": self.tokens_used,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
