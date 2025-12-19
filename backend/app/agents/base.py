from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.schemas.common import (
    Context,
    Intent,
    AgentResponse,
    AgentType,
    Language
)


class BaseAgent(ABC):
    """
    Abstract base class for all specialized agents.

    All agents must inherit from this class and implement the required methods.
    This ensures a consistent interface across all agents in the system.
    """

    def __init__(
        self,
        agent_id: str,
        agent_type: AgentType,
        name: str,
        description: str,
        capabilities: List[str],
        supported_languages: List[Language] = None
    ):
        """
        Initialize the base agent.

        Args:
            agent_id: Unique identifier for the agent
            agent_type: Type of the agent (from AgentType enum)
            name: Human-readable name
            description: Description of agent's purpose
            capabilities: List of specific capabilities
            supported_languages: Languages this agent supports
        """
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.name = name
        self.description = description
        self.capabilities = capabilities
        self.supported_languages = supported_languages or [
            Language.POLISH,
            Language.ENGLISH,
            Language.GERMAN
        ]
        self.is_active = True
        self.metadata: Dict[str, Any] = {}

    @abstractmethod
    async def process(self, context: Context, intent: Intent) -> AgentResponse:
        """
        Process a user request and generate a response.

        This is the main method that each agent must implement.
        It receives the conversation context and classified intent,
        and returns a structured response.

        Args:
            context: Conversation context including history, user profile, etc.
            intent: Classified user intent with confidence and entities

        Returns:
            AgentResponse: Structured response from the agent
        """
        pass

    @abstractmethod
    async def can_handle(self, intent: Intent, context: Context) -> float:
        """
        Determine if this agent can handle the given intent.

        Returns a confidence score (0.0 to 1.0) indicating how well
        this agent can handle the request.

        Args:
            intent: Classified user intent
            context: Conversation context

        Returns:
            float: Confidence score (0.0 = cannot handle, 1.0 = perfect match)
        """
        pass

    def supports_language(self, language: Language) -> bool:
        """Check if this agent supports the given language."""
        return language in self.supported_languages

    def get_info(self) -> Dict[str, Any]:
        """Get agent information for registry."""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "supported_languages": [lang.value for lang in self.supported_languages],
            "is_active": self.is_active,
            "metadata": self.metadata
        }

    def activate(self):
        """Activate this agent."""
        self.is_active = True

    def deactivate(self):
        """Deactivate this agent."""
        self.is_active = False

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.agent_id}, type={self.agent_type.value})>"
