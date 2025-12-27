"""
Daily Life Companion models for rituals, check-ins, and daily support.

This makes the AI a true daily companion that's part of user's routine.
"""

from typing import Dict
from sqlalchemy import Column, String, Integer, Float, JSON, ForeignKey, DateTime, Text, Boolean, Enum as SQLEnum, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, time
import uuid
import enum

from app.db.base import Base


class RitualType(str, enum.Enum):
    """Types of daily rituals."""
    MORNING = "morning"
    EVENING = "evening"
    MIDDAY = "midday"
    BEDTIME = "bedtime"
    CUSTOM = "custom"


class CheckInType(str, enum.Enum):
    """Types of daily check-ins."""
    MORNING_CHECKIN = "morning_checkin"  # How are you feeling? What's ahead?
    MIDDAY_PULSE = "midday_pulse"  # How's your day going?
    EVENING_REFLECTION = "evening_reflection"  # Reflect on the day
    MOOD_CHECKIN = "mood_checkin"  # Quick mood check
    ENERGY_CHECKIN = "energy_checkin"  # Energy level check
    GRATITUDE = "gratitude"  # What are you grateful for?
    WINS = "wins"  # Celebrate today's wins


class DailyRitual(Base):
    """
    User's daily rituals and routines.

    These create structure and consistency in interactions.
    """
    __tablename__ = "daily_rituals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    ritual_type = Column(SQLEnum(RitualType), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)

    # Timing
    scheduled_time = Column(Time)  # Preferred time
    duration_minutes = Column(Integer, default=5)

    # Ritual components (customizable)
    components = Column(JSON, default=list)  # List of ritual steps

    # Activation
    is_active = Column(Boolean, default=True)
    days_of_week = Column(JSON, default=list)  # [0-6] for Mon-Sun

    # Tracking
    total_completions = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_completed = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User")
    completions = relationship("RitualCompletion", back_populates="ritual", cascade="all, delete-orphan")


class RitualCompletion(Base):
    """Track ritual completions."""
    __tablename__ = "ritual_completions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ritual_id = Column(UUID(as_uuid=True), ForeignKey("daily_rituals.id"), nullable=False)

    completed_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    mood_before = Column(Float)  # Mood before ritual (0-10)
    mood_after = Column(Float)  # Mood after ritual (0-10)

    notes = Column(Text)  # User's notes about the ritual

    # Relationships
    ritual = relationship("DailyRitual", back_populates="completions")


class DailyCheckIn(Base):
    """
    Daily check-ins for maintaining connection and awareness.
    """
    __tablename__ = "daily_checkins"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    checkin_type = Column(SQLEnum(CheckInType), nullable=False)
    checkin_date = Column(DateTime, nullable=False, default=datetime.utcnow)

    # User responses
    mood_rating = Column(Float)  # 0-10
    energy_level = Column(Float)  # 0-10
    stress_level = Column(Float)  # 0-10

    # Qualitative responses
    feelings = Column(JSON, default=list)  # List of emotion words
    whats_on_mind = Column(Text)  # What's on your mind?
    priorities_today = Column(JSON, default=list)  # Today's priorities

    # Gratitude
    grateful_for = Column(JSON, default=list)  # What are you grateful for?

    # Wins and challenges
    wins_today = Column(JSON, default=list)  # Today's wins
    challenges_today = Column(JSON, default=list)  # Today's challenges

    # Sleep (for morning check-ins)
    sleep_hours = Column(Float)
    sleep_quality = Column(Float)  # 0-10

    # AI response
    ai_response = Column(Text)  # AI's response to the check-in
    ai_insights = Column(JSON, default=dict)  # Insights generated

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User")


class DailyIntention(Base):
    """
    Daily intentions set by user.

    Intentions create purpose and direction for each day.
    """
    __tablename__ = "daily_intentions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    date = Column(DateTime, nullable=False)
    intention = Column(Text, nullable=False)  # Main intention for the day

    # Supporting details
    why_important = Column(Text)  # Why this matters
    how_to_achieve = Column(Text)  # How will you do it

    # Tracking
    was_achieved = Column(Boolean, default=False)
    achievement_score = Column(Float)  # 0-10, how well achieved
    reflection = Column(Text)  # End of day reflection

    created_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime)  # When user reviewed it

    # Relationships
    user = relationship("User")


class WellnessSnapshot(Base):
    """
    Daily wellness snapshots tracking overall wellbeing.
    """
    __tablename__ = "wellness_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    snapshot_date = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Wellness dimensions (0-10 each)
    physical_wellness = Column(Float)
    mental_wellness = Column(Float)
    emotional_wellness = Column(Float)
    social_wellness = Column(Float)
    spiritual_wellness = Column(Float)

    # Overall score
    overall_wellness = Column(Float)  # Average or weighted

    # Contributing factors
    sleep_score = Column(Float)
    nutrition_score = Column(Float)
    activity_score = Column(Float)
    stress_score = Column(Float)
    connection_score = Column(Float)  # Social connections

    # Notes
    notes = Column(Text)
    highlights = Column(JSON, default=list)  # Positive highlights
    concerns = Column(JSON, default=list)  # Areas of concern

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User")


# Helper functions

def create_default_morning_ritual() -> Dict:
    """Create a default morning ritual template."""
    return {
        "name": "Morning Energizer",
        "components": [
            {"step": 1, "action": "Check in with your mood", "duration": 1},
            {"step": 2, "action": "Review your intentions for the day", "duration": 2},
            {"step": 3, "action": "Set your top 3 priorities", "duration": 2},
        ],
        "duration_minutes": 5,
        "scheduled_time": time(7, 0)  # 7:00 AM
    }


def create_default_evening_ritual() -> Dict:
    """Create a default evening ritual template."""
    return {
        "name": "Evening Reflection",
        "components": [
            {"step": 1, "action": "Celebrate 3 wins from today", "duration": 2},
            {"step": 2, "action": "Reflect on challenges", "duration": 2},
            {"step": 3, "action": "Express gratitude", "duration": 1},
        ],
        "duration_minutes": 5,
        "scheduled_time": time(21, 0)  # 9:00 PM
    }


def calculate_wellness_score(dimensions: Dict[str, float]) -> float:
    """Calculate overall wellness score from dimensions."""
    if not dimensions:
        return 0.0

    # Weighted average
    weights = {
        "physical_wellness": 0.2,
        "mental_wellness": 0.25,
        "emotional_wellness": 0.25,
        "social_wellness": 0.15,
        "spiritual_wellness": 0.15
    }

    weighted_sum = sum(dimensions.get(dim, 0) * weight for dim, weight in weights.items())
    return round(weighted_sum, 2)
