"""
Emotional Intelligence models for empathetic AI interaction.

This module provides the foundation for emotional awareness,
sentiment tracking, and empathetic responses.
"""

from sqlalchemy import Column, String, Integer, Float, JSON, ForeignKey, DateTime, Text, Boolean, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.db.base import Base


class EmotionType(str, enum.Enum):
    """Primary emotions based on Plutchik's wheel of emotions."""
    # Primary emotions
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    TRUST = "trust"
    DISGUST = "disgust"
    SURPRISE = "surprise"
    ANTICIPATION = "anticipation"

    # Secondary emotions (combinations)
    LOVE = "love"  # joy + trust
    GUILT = "guilt"  # sadness + fear
    ANXIETY = "anxiety"  # fear + anticipation
    PRIDE = "pride"  # joy + anger
    HOPE = "hope"  # anticipation + trust
    SHAME = "shame"  # fear + disgust
    DESPAIR = "despair"  # sadness + fear
    EXCITEMENT = "excitement"  # joy + anticipation
    GRATITUDE = "gratitude"  # joy + trust
    LONELINESS = "loneliness"  # sadness + fear
    FRUSTRATION = "frustration"  # anger + anticipation
    OVERWHELM = "overwhelm"  # fear + surprise
    CONTENTMENT = "contentment"  # joy + trust (mild)
    BOREDOM = "boredom"  # disgust + anticipation (negative)


class MoodState(str, enum.Enum):
    """Overall mood states."""
    VERY_NEGATIVE = "very_negative"  # -2
    NEGATIVE = "negative"  # -1
    NEUTRAL = "neutral"  # 0
    POSITIVE = "positive"  # 1
    VERY_POSITIVE = "very_positive"  # 2


class EmpathyResponseType(str, enum.Enum):
    """Types of empathetic responses."""
    VALIDATION = "validation"  # Acknowledge feelings
    COMFORT = "comfort"  # Provide emotional support
    ENCOURAGEMENT = "encouragement"  # Boost confidence
    REFLECTION = "reflection"  # Help process emotions
    GUIDANCE = "guidance"  # Offer actionable advice
    CELEBRATION = "celebration"  # Share in positive emotions
    PRESENCE = "presence"  # Just be there


class EmotionalState(Base):
    """
    Track user's emotional state over time.

    This enables the AI to understand emotional patterns,
    provide appropriate support, and adapt communication style.
    """
    __tablename__ = "emotional_states"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=True)

    # Detected emotions (can be multiple)
    primary_emotion = Column(SQLEnum(EmotionType), nullable=False)
    secondary_emotions = Column(JSON, default=list)  # List of EmotionType values

    # Intensity and valence
    intensity = Column(Float, nullable=False)  # 0-1 scale
    valence = Column(Float, nullable=False)  # -1 (negative) to 1 (positive)
    arousal = Column(Float)  # 0-1 (calm to excited)

    # Overall mood
    mood_state = Column(SQLEnum(MoodState), nullable=False)

    # Detection source
    detected_from = Column(String(50))  # text, voice_tone, image, user_input
    confidence = Column(Float, default=0.8)  # Detection confidence

    # Context
    trigger = Column(Text)  # What caused this emotion
    user_message = Column(Text)  # Original message if from text

    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User")
    conversation = relationship("Conversation")


class EmotionalPattern(Base):
    """
    Long-term emotional patterns and trends for each user.

    This enables predictive insights and personalized support.
    """
    __tablename__ = "emotional_patterns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)

    # Emotional baseline
    baseline_mood = Column(Float, default=0.0)  # -2 to 2 scale
    typical_intensity = Column(Float, default=0.5)  # 0-1

    # Common emotions
    dominant_emotions = Column(JSON, default=list)  # Most frequent emotions

    # Patterns
    morning_mood_avg = Column(Float)  # Average mood in morning
    evening_mood_avg = Column(Float)  # Average mood in evening
    weekly_pattern = Column(JSON, default=dict)  # Mood by day of week

    # Triggers
    positive_triggers = Column(JSON, default=list)  # What makes them happy
    negative_triggers = Column(JSON, default=list)  # What upsets them
    stress_triggers = Column(JSON, default=list)  # What stresses them

    # Coping mechanisms
    effective_coping_strategies = Column(JSON, default=list)
    preferred_support_types = Column(JSON, default=list)  # What helps them most

    # Risk assessment
    emotional_volatility = Column(Float, default=0.0)  # How much mood varies
    crisis_risk_score = Column(Float, default=0.0)  # 0-1, higher = more risk
    last_crisis_check = Column(DateTime)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_analyzed = Column(DateTime)

    # Relationships
    user = relationship("User")


class EmpathyResponse(Base):
    """
    Track empathetic responses provided by the AI.

    This helps the system learn what works best for each user.
    """
    __tablename__ = "empathy_responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    emotional_state_id = Column(UUID(as_uuid=True), ForeignKey("emotional_states.id"))

    response_type = Column(SQLEnum(EmpathyResponseType), nullable=False)
    response_text = Column(Text, nullable=False)

    # User detected emotion
    user_emotion = Column(String(50))

    # Effectiveness
    was_helpful = Column(Boolean)  # User feedback
    helpfulness_score = Column(Float)  # 0-1 if rated
    user_mood_change = Column(Float)  # Change in mood after response

    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User")
    emotional_state = relationship("EmotionalState")


class MoodJournalEntry(Base):
    """
    User-created mood journal entries for self-reflection.
    """
    __tablename__ = "mood_journal_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Mood rating
    mood_rating = Column(Float, nullable=False)  # -2 to 2
    energy_level = Column(Float)  # 0-10
    stress_level = Column(Float)  # 0-10

    # Emotions
    emotions = Column(JSON, default=list)  # List of EmotionType values

    # Journal content
    title = Column(String(200))
    entry_text = Column(Text)

    # Context
    activities_today = Column(JSON, default=list)
    gratitude_list = Column(JSON, default=list)  # Things user is grateful for
    challenges_faced = Column(JSON, default=list)

    # Metadata
    entry_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User")


# Helper functions for emotional intelligence

def calculate_mood_state(valence: float) -> MoodState:
    """Convert valence to mood state."""
    if valence < -0.6:
        return MoodState.VERY_NEGATIVE
    elif valence < -0.2:
        return MoodState.NEGATIVE
    elif valence < 0.2:
        return MoodState.NEUTRAL
    elif valence < 0.6:
        return MoodState.POSITIVE
    else:
        return MoodState.VERY_POSITIVE


def get_emotion_valence(emotion: EmotionType) -> float:
    """Get valence (positive/negative) for each emotion."""
    valence_map = {
        EmotionType.JOY: 0.9,
        EmotionType.SADNESS: -0.7,
        EmotionType.ANGER: -0.8,
        EmotionType.FEAR: -0.9,
        EmotionType.TRUST: 0.7,
        EmotionType.DISGUST: -0.8,
        EmotionType.SURPRISE: 0.0,  # Can be positive or negative
        EmotionType.ANTICIPATION: 0.3,
        EmotionType.LOVE: 1.0,
        EmotionType.GUILT: -0.7,
        EmotionType.ANXIETY: -0.8,
        EmotionType.PRIDE: 0.7,
        EmotionType.HOPE: 0.8,
        EmotionType.SHAME: -0.9,
        EmotionType.DESPAIR: -1.0,
        EmotionType.EXCITEMENT: 0.8,
        EmotionType.GRATITUDE: 0.9,
        EmotionType.LONELINESS: -0.8,
        EmotionType.FRUSTRATION: -0.6,
        EmotionType.OVERWHELM: -0.7,
        EmotionType.CONTENTMENT: 0.6,
        EmotionType.BOREDOM: -0.3,
    }
    return valence_map.get(emotion, 0.0)


def get_empathy_response_for_emotion(emotion: EmotionType, intensity: float) -> EmpathyResponseType:
    """Determine appropriate empathy response type based on emotion."""
    if emotion in [EmotionType.SADNESS, EmotionType.DESPAIR, EmotionType.LONELINESS]:
        return EmpathyResponseType.COMFORT
    elif emotion in [EmotionType.ANGER, EmotionType.FRUSTRATION]:
        return EmpathyResponseType.VALIDATION
    elif emotion in [EmotionType.FEAR, EmotionType.ANXIETY, EmotionType.OVERWHELM]:
        return EmpathyResponseType.COMFORT if intensity > 0.7 else EmpathyResponseType.GUIDANCE
    elif emotion in [EmotionType.JOY, EmotionType.EXCITEMENT, EmotionType.PRIDE]:
        return EmpathyResponseType.CELEBRATION
    elif emotion in [EmotionType.GUILT, EmotionType.SHAME]:
        return EmpathyResponseType.VALIDATION
    elif emotion in [EmotionType.HOPE, EmotionType.ANTICIPATION]:
        return EmpathyResponseType.ENCOURAGEMENT
    else:
        return EmpathyResponseType.REFLECTION
