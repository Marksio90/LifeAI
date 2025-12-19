from sqlalchemy import Column, String, Text, TIMESTAMP, Float
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base

class Timeline(Base):
    __tablename__ = "timeline"

    id = Column(UUID(as_uuid=True), primary_key=True)
    created_at = Column(TIMESTAMP, nullable=False)
    summary = Column(Text)
    themes = Column(Text)
    core_question = Column(Text)
    emotional_tone = Column(Text)
    confidence = Column(Float)
