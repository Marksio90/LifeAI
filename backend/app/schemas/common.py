from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class Language(str, Enum):
    """Supported languages"""
    POLISH = "pl"
    ENGLISH = "en"
    GERMAN = "de"


class ModalityType(str, Enum):
    """Input/Output modality types"""
    TEXT = "text"
    VOICE = "voice"
    IMAGE = "image"
    VIDEO = "video"


class AgentType(str, Enum):
    """Types of specialized agents"""
    GENERAL = "general"
    HEALTH = "health"
    FINANCE = "finance"
    RELATIONS = "relations"
    PERSONAL_DEVELOPMENT = "personal_development"
    TASK_MANAGEMENT = "task_management"


class IntentType(str, Enum):
    """User intent types"""
    GENERAL_CONVERSATION = "general_conversation"
    HEALTH_QUERY = "health_query"
    FINANCE_QUERY = "finance_query"
    RELATIONSHIP_ADVICE = "relationship_advice"
    CAREER_PLANNING = "career_planning"
    TASK_MANAGEMENT = "task_management"
    MULTI_DOMAIN = "multi_domain"


class Message(BaseModel):
    """Chat message schema"""
    role: str = Field(..., description="Message role: user, assistant, system")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class Context(BaseModel):
    """Conversation context"""
    session_id: str
    user_id: Optional[str] = None
    language: Language = Language.POLISH
    history: List[Message] = Field(default_factory=list)
    user_profile: Optional[Dict[str, Any]] = None
    relevant_memories: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Intent(BaseModel):
    """Classified user intent"""
    type: IntentType
    confidence: float = Field(..., ge=0.0, le=1.0)
    entities: Dict[str, Any] = Field(default_factory=dict)
    agent_types: List[AgentType] = Field(default_factory=list)
    requires_multi_agent: bool = False


class AgentResponse(BaseModel):
    """Response from an agent"""
    agent_id: str
    agent_type: AgentType
    content: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    follow_up_actions: List[str] = Field(default_factory=list)


class OrchestratorResponse(BaseModel):
    """Final response from the orchestrator"""
    content: str
    modality: ModalityType = ModalityType.TEXT
    agent_responses: List[AgentResponse] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
