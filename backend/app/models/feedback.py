from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, Float, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.db.base import Base


class Feedback(Base):
    """User feedback on AI responses for continuous learning"""
    __tablename__ = "feedbacks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)

    # What message/interaction is being rated
    message_index = Column(Integer, nullable=False)  # Index in conversation messages
    agent_id = Column(String(100), nullable=False, index=True)  # Which agent gave this response

    # Feedback data
    rating = Column(Integer, nullable=True)  # 1-5 stars, or thumbs up/down (-1, 1)
    helpful = Column(Boolean, nullable=True)  # Simple helpful/not helpful
    comment = Column(Text, nullable=True)  # Optional user comment

    # Detailed feedback categories
    accuracy = Column(Float, nullable=True)  # How accurate was the response
    relevance = Column(Float, nullable=True)  # How relevant
    clarity = Column(Float, nullable=True)  # How clear

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", back_populates="feedbacks")
    conversation = relationship("Conversation", back_populates="feedbacks")

    def __repr__(self):
        return f"<Feedback(id={self.id}, rating={self.rating}, helpful={self.helpful})>"

    def to_dict(self):
        return {
            "id": str(self.id),
            "rating": self.rating,
            "helpful": self.helpful,
            "comment": self.comment,
            "accuracy": self.accuracy,
            "relevance": self.relevance,
            "clarity": self.clarity,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
