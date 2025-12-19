from typing import Dict, List, Optional
from app.agents.base import BaseAgent
from app.schemas.common import AgentType, Intent, Context
import logging

logger = logging.getLogger(__name__)


class AgentRegistry:
    """
    Registry for managing all available agents in the system.

    This is a singleton that maintains a registry of all agents,
    allows dynamic addition/removal of agents, and provides
    methods to query available agents.
    """

    _instance = None
    _agents: Dict[str, BaseAgent] = {}

    def __new__(cls):
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super(AgentRegistry, cls).__new__(cls)
            cls._instance._agents = {}
        return cls._instance

    def register(self, agent: BaseAgent) -> None:
        """
        Register a new agent.

        Args:
            agent: Agent instance to register

        Raises:
            ValueError: If agent with this ID already exists
        """
        if agent.agent_id in self._agents:
            logger.warning(f"Agent {agent.agent_id} already registered. Overwriting.")

        self._agents[agent.agent_id] = agent
        logger.info(f"Registered agent: {agent.agent_id} ({agent.agent_type.value})")

    def unregister(self, agent_id: str) -> bool:
        """
        Unregister an agent.

        Args:
            agent_id: ID of agent to remove

        Returns:
            bool: True if agent was removed, False if not found
        """
        if agent_id in self._agents:
            agent = self._agents.pop(agent_id)
            logger.info(f"Unregistered agent: {agent_id}")
            return True
        return False

    def get(self, agent_id: str) -> Optional[BaseAgent]:
        """Get agent by ID."""
        return self._agents.get(agent_id)

    def get_by_type(self, agent_type: AgentType) -> List[BaseAgent]:
        """
        Get all agents of a specific type.

        Args:
            agent_type: Type of agents to retrieve

        Returns:
            List of agents matching the type
        """
        return [
            agent for agent in self._agents.values()
            if agent.agent_type == agent_type and agent.is_active
        ]

    def get_all_active(self) -> List[BaseAgent]:
        """Get all active agents."""
        return [agent for agent in self._agents.values() if agent.is_active]

    def get_all(self) -> List[BaseAgent]:
        """Get all registered agents (active and inactive)."""
        return list(self._agents.values())

    async def find_capable_agents(
        self,
        intent: Intent,
        context: Context,
        min_confidence: float = 0.3
    ) -> List[tuple[BaseAgent, float]]:
        """
        Find agents capable of handling the given intent.

        Args:
            intent: User intent
            context: Conversation context
            min_confidence: Minimum confidence threshold

        Returns:
            List of (agent, confidence) tuples, sorted by confidence (descending)
        """
        capable_agents = []

        for agent in self.get_all_active():
            try:
                confidence = await agent.can_handle(intent, context)
                if confidence >= min_confidence:
                    capable_agents.append((agent, confidence))
            except Exception as e:
                logger.error(f"Error checking agent {agent.agent_id}: {e}")
                continue

        # Sort by confidence (descending)
        capable_agents.sort(key=lambda x: x[1], reverse=True)
        return capable_agents

    def get_agent_info(self, agent_id: str) -> Optional[Dict]:
        """Get information about a specific agent."""
        agent = self.get(agent_id)
        return agent.get_info() if agent else None

    def list_all_agents_info(self) -> List[Dict]:
        """Get information about all registered agents."""
        return [agent.get_info() for agent in self._agents.values()]

    def activate_agent(self, agent_id: str) -> bool:
        """Activate an agent."""
        agent = self.get(agent_id)
        if agent:
            agent.activate()
            logger.info(f"Activated agent: {agent_id}")
            return True
        return False

    def deactivate_agent(self, agent_id: str) -> bool:
        """Deactivate an agent."""
        agent = self.get(agent_id)
        if agent:
            agent.deactivate()
            logger.info(f"Deactivated agent: {agent_id}")
            return True
        return False

    def clear(self) -> None:
        """Clear all registered agents (mainly for testing)."""
        self._agents.clear()
        logger.info("Cleared all agents from registry")

    def __len__(self) -> int:
        """Return number of registered agents."""
        return len(self._agents)

    def __contains__(self, agent_id: str) -> bool:
        """Check if agent is registered."""
        return agent_id in self._agents
