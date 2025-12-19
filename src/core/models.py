"""
Core Data Models for LifeAI Platform
Defines the fundamental data structures used throughout the system
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class IntentType(str, Enum):
    """Types of user intents that the system can recognize"""
    HEALTH = "health"
    FINANCE = "finance"
    PSYCHOLOGY = "psychology"
    RELATIONSHIPS = "relationships"
    PERSONAL_DEVELOPMENT = "personal_development"
    GENERAL = "general"
    MULTI_DOMAIN = "multi_domain"


class ConfidenceLevel(str, Enum):
    """Confidence levels for predictions and responses"""
    HIGH = "high"  # > 0.8
    MEDIUM = "medium"  # 0.5 - 0.8
    LOW = "low"  # < 0.5
    UNCERTAIN = "uncertain"  # Cannot determine


class UserInput(BaseModel):
    """User input data structure"""
    user_id: str
    session_id: str
    content: str
    input_type: str = "text"  # text, voice, image
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None


class Intent(BaseModel):
    """Detected user intent"""
    intent_type: IntentType
    confidence: float = Field(ge=0.0, le=1.0)
    sub_intents: List[IntentType] = Field(default_factory=list)
    extracted_entities: Dict[str, Any] = Field(default_factory=dict)


class AgentRequest(BaseModel):
    """Request sent to an agent"""
    agent_id: str
    user_input: UserInput
    intent: Intent
    context: Dict[str, Any] = Field(default_factory=dict)
    timeout: int = 30


class AgentResponse(BaseModel):
    """Response from an agent"""
    agent_id: str
    content: str
    confidence: float = Field(ge=0.0, le=1.0)
    confidence_level: ConfidenceLevel
    metadata: Dict[str, Any] = Field(default_factory=dict)
    processing_time: float
    tokens_used: Optional[int] = None


class OrchestratorResponse(BaseModel):
    """Final orchestrated response to user"""
    user_id: str
    session_id: str
    content: str
    agent_responses: List[AgentResponse]
    total_confidence: float
    intent: Intent
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class UserProfile(BaseModel):
    """User profile stored in Identity & Context Engine"""
    user_id: str
    values: List[str] = Field(default_factory=list)
    goals: List[str] = Field(default_factory=list)
    preferences: Dict[str, Any] = Field(default_factory=dict)
    personality_traits: Dict[str, float] = Field(default_factory=dict)
    decision_history: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
