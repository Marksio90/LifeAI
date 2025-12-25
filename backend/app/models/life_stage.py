"""
Life Stage models for comprehensive life journey tracking.

This module defines the life stage system that enables the platform
to provide age-appropriate, contextually relevant support across
all phases of human life.
"""

from sqlalchemy import Column, String, Integer, Float, JSON, ForeignKey, DateTime, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.db.base import Base


class LifeStageType(str, enum.Enum):
    """
    Comprehensive life stages covering the entire human lifespan.

    Each stage has unique challenges, opportunities, and support needs.
    """
    CHILDHOOD = "childhood"  # 0-12: Foundation, learning, family
    ADOLESCENCE = "adolescence"  # 13-19: Identity formation, education, peer relationships
    YOUNG_ADULT = "young_adult"  # 20-29: Independence, career start, relationships
    EARLY_ADULT = "early_adult"  # 30-39: Career building, family formation, settling
    MIDLIFE = "midlife"  # 40-54: Peak career, parenting, reflection
    LATE_MIDLIFE = "late_midlife"  # 55-64: Pre-retirement, empty nest, purpose
    YOUNG_SENIOR = "young_senior"  # 65-74: Active retirement, wisdom sharing
    SENIOR = "senior"  # 75-84: Legacy, health focus, life review
    ELDERLY = "elderly"  # 85+: Spiritual growth, acceptance, end-of-life


class LifeRole(str, enum.Enum):
    """Current life roles that shape user's context and needs."""
    STUDENT = "student"
    EMPLOYEE = "employee"
    ENTREPRENEUR = "entrepreneur"
    PARENT = "parent"
    CAREGIVER = "caregiver"
    RETIREE = "retiree"
    VOLUNTEER = "volunteer"
    HOMEMAKER = "homemaker"
    JOB_SEEKER = "job_seeker"
    CREATIVE = "creative"


class LifeTransitionType(str, enum.Enum):
    """Major life transitions that require extra support."""
    NEW_JOB = "new_job"
    JOB_LOSS = "job_loss"
    CAREER_CHANGE = "career_change"
    NEW_RELATIONSHIP = "new_relationship"
    MARRIAGE = "marriage"
    BREAKUP = "breakup"
    DIVORCE = "divorce"
    NEW_PARENT = "new_parent"
    CHILD_LEAVING_HOME = "child_leaving_home"
    MOVING = "moving"
    LOSS_LOVED_ONE = "loss_loved_one"
    HEALTH_DIAGNOSIS = "health_diagnosis"
    RETIREMENT = "retirement"
    GOING_TO_COLLEGE = "going_to_college"
    GRADUATION = "graduation"
    FINANCIAL_HARDSHIP = "financial_hardship"
    MAJOR_ACHIEVEMENT = "major_achievement"


class UserLifeProfile(Base):
    """
    Comprehensive life profile tracking user's current stage,
    roles, transitions, and life context.
    """
    __tablename__ = "user_life_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)

    # Current life stage
    current_stage = Column(SQLEnum(LifeStageType), nullable=False)
    age = Column(Integer)
    date_of_birth = Column(DateTime)

    # Life roles (stored as JSON array)
    current_roles = Column(JSON, default=list)  # List of LifeRole values

    # Life context
    relationship_status = Column(String(50))  # single, married, partnered, divorced, widowed
    has_children = Column(Integer, default=0)  # Number of children
    employment_status = Column(String(50))  # employed, unemployed, student, retired
    education_level = Column(String(50))  # high_school, bachelors, masters, phd

    # Life priorities (1-10 ratings)
    priorities = Column(JSON, default=dict)  # {career: 8, family: 10, health: 7, ...}

    # Life satisfaction areas (1-10 ratings)
    satisfaction = Column(JSON, default=dict)  # {career: 6, relationships: 8, ...}

    # Current challenges and goals
    current_challenges = Column(JSON, default=list)  # List of challenge descriptions
    life_goals = Column(JSON, default=list)  # List of goal objects

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="life_profile")
    transitions = relationship("LifeTransition", back_populates="profile", cascade="all, delete-orphan")
    milestones = relationship("LifeMilestone", back_populates="profile", cascade="all, delete-orphan")


class LifeTransition(Base):
    """
    Track major life transitions for providing appropriate support.
    """
    __tablename__ = "life_transitions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("user_life_profiles.id"), nullable=False)

    transition_type = Column(SQLEnum(LifeTransitionType), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)

    # Timeline
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    expected_end_at = Column(DateTime)  # Optional
    completed_at = Column(DateTime)  # When transition is complete

    # Support tracking
    support_level_needed = Column(Integer, default=5)  # 1-10 scale
    coping_score = Column(Float)  # How well user is coping (calculated)

    # Notes and updates
    notes = Column(JSON, default=list)  # Timeline of notes/updates
    emotions = Column(JSON, default=list)  # Emotional states during transition

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    profile = relationship("UserLifeProfile", back_populates="transitions")


class LifeMilestone(Base):
    """
    Track significant life milestones and achievements.
    """
    __tablename__ = "life_milestones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("user_life_profiles.id"), nullable=False)

    title = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(50))  # career, relationship, health, personal, achievement

    achieved_at = Column(DateTime, nullable=False)
    importance = Column(Integer, default=5)  # 1-10 scale

    # Emotional impact
    emotions_felt = Column(JSON, default=list)  # List of emotions
    reflection = Column(Text)  # User's reflection on the milestone

    # Media
    images = Column(JSON, default=list)  # Image URLs/paths

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    profile = relationship("UserLifeProfile", back_populates="milestones")


def get_life_stage_for_age(age: int) -> LifeStageType:
    """Determine life stage based on age."""
    if age < 13:
        return LifeStageType.CHILDHOOD
    elif age < 20:
        return LifeStageType.ADOLESCENCE
    elif age < 30:
        return LifeStageType.YOUNG_ADULT
    elif age < 40:
        return LifeStageType.EARLY_ADULT
    elif age < 55:
        return LifeStageType.MIDLIFE
    elif age < 65:
        return LifeStageType.LATE_MIDLIFE
    elif age < 75:
        return LifeStageType.YOUNG_SENIOR
    elif age < 85:
        return LifeStageType.SENIOR
    else:
        return LifeStageType.ELDERLY


def get_stage_characteristics(stage: LifeStageType) -> dict:
    """Get characteristics and focus areas for each life stage."""
    characteristics = {
        LifeStageType.CHILDHOOD: {
            "focus_areas": ["learning", "play", "family", "school", "social_skills"],
            "common_challenges": ["bullying", "academic_pressure", "family_issues", "self_esteem"],
            "support_approach": "nurturing, educational, playful, protective",
            "key_relationships": ["parents", "siblings", "teachers", "friends"],
        },
        LifeStageType.ADOLESCENCE: {
            "focus_areas": ["identity", "education", "peer_relationships", "independence", "future_planning"],
            "common_challenges": ["peer_pressure", "academic_stress", "body_image", "family_conflict", "career_confusion"],
            "support_approach": "understanding, non-judgmental, empowering, future-oriented",
            "key_relationships": ["peers", "parents", "romantic_interests", "mentors"],
        },
        LifeStageType.YOUNG_ADULT: {
            "focus_areas": ["career_start", "independence", "relationships", "identity_solidification", "exploration"],
            "common_challenges": ["financial_stress", "career_uncertainty", "relationship_issues", "life_direction"],
            "support_approach": "encouraging, practical, exploratory, balanced",
            "key_relationships": ["romantic_partners", "friends", "colleagues", "mentors"],
        },
        LifeStageType.EARLY_ADULT: {
            "focus_areas": ["career_building", "family_formation", "home_ownership", "financial_stability", "settling"],
            "common_challenges": ["work_life_balance", "parenting", "mortgage_stress", "career_plateau"],
            "support_approach": "pragmatic, supportive, goal-oriented, stress-management",
            "key_relationships": ["spouse_partner", "children", "parents", "colleagues"],
        },
        LifeStageType.MIDLIFE: {
            "focus_areas": ["peak_career", "parenting_teens", "aging_parents", "health", "meaning"],
            "common_challenges": ["midlife_crisis", "teen_parenting", "elderly_care", "health_concerns", "purpose"],
            "support_approach": "reflective, wisdom-seeking, health-conscious, balanced",
            "key_relationships": ["family", "aging_parents", "teenage_children", "long_term_friends"],
        },
        LifeStageType.LATE_MIDLIFE: {
            "focus_areas": ["pre_retirement", "empty_nest", "grandparenting", "health_focus", "legacy"],
            "common_challenges": ["retirement_planning", "empty_nest_syndrome", "health_decline", "purpose_shift"],
            "support_approach": "transitional, purposeful, health-supportive, legacy-building",
            "key_relationships": ["spouse", "adult_children", "grandchildren", "close_friends"],
        },
        LifeStageType.YOUNG_SENIOR: {
            "focus_areas": ["active_retirement", "hobbies", "travel", "volunteering", "wisdom_sharing"],
            "common_challenges": ["purpose_finding", "health_maintenance", "social_connection", "financial_security"],
            "support_approach": "empowering, active, social, purposeful",
            "key_relationships": ["spouse", "friends", "grandchildren", "community"],
        },
        LifeStageType.SENIOR: {
            "focus_areas": ["health_management", "legacy", "life_review", "spiritual_growth", "family_connection"],
            "common_challenges": ["mobility_issues", "loss_of_loved_ones", "cognitive_decline", "independence"],
            "support_approach": "gentle, respectful, health-focused, legacy-honoring",
            "key_relationships": ["family", "caregivers", "lifelong_friends", "healthcare_providers"],
        },
        LifeStageType.ELDERLY: {
            "focus_areas": ["comfort", "spiritual_peace", "life_acceptance", "family_legacy", "dignity"],
            "common_challenges": ["health_decline", "loss", "end_of_life_fears", "dependence"],
            "support_approach": "compassionate, gentle, spiritual, dignity-preserving",
            "key_relationships": ["close_family", "caregivers", "spiritual_advisors"],
        },
    }

    return characteristics.get(stage, {})
