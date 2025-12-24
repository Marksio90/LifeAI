from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.base import Base


class Conversation(Base):
    """Conversation model to store user conversations"""
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(String(255), unique=True, nullable=False, index=True)

    # Conversation metadata
    title = Column(String(500), nullable=True)  # Auto-generated or user-provided
    language = Column(String(10), default="pl")

    # Messages stored as JSON array
    messages = Column(JSON, default=list)

    # Analytics
    message_count = Column(Integer, default=0)
    agents_used = Column(JSON, default=list)  # List of agent IDs that participated

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)

    # Summary (auto-generated when conversation ends)
    summary = Column(Text, nullable=True)
    main_topics = Column(JSON, default=list)

    # Relationships
    user = relationship("User", back_populates="conversations")
    feedbacks = relationship("Feedback", back_populates="conversation", cascade="all, delete-orphan")
    agent_interactions = relationship("AgentInteraction", back_populates="conversation", cascade="all, delete-orphan")

    # Composite indexes for common queries
    __table_args__ = (
        # Index for user's conversations sorted by creation date (most common query)
        Index('ix_conversations_user_created', 'user_id', 'created_at'),
        # Index for user's recent conversations
        Index('ix_conversations_user_updated', 'user_id', 'updated_at'),
        # Index for finding conversations by creation date
        Index('ix_conversations_created_at', 'created_at'),
    )

    def __repr__(self):
        return f"<Conversation(id={self.id}, user_id={self.user_id}, messages={self.message_count})>"

    def to_dict(self):
        return {
            "id": str(self.id),
            "session_id": self.session_id,
            "title": self.title,
            "language": self.language,
            "message_count": self.message_count,
            "agents_used": self.agents_used,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "summary": self.summary,
            "main_topics": self.main_topics
        }
