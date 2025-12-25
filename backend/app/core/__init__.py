from app.core.agent_registry import AgentRegistry
from app.core.orchestrator import get_orchestrator
from app.agents.general import GeneralAgent
from app.agents.finance import FinanceAgent
from app.agents.health import HealthAgent
from app.agents.relations import RelationsAgent
from app.agents.task_management import TaskManagementAgent
from app.agents.personal_development import PersonalDevelopmentAgent
import logging

logger = logging.getLogger(__name__)


def initialize_agents():
    """
    Initialize and register all agents in the system.

    This function should be called at application startup.
    """
    logger.info("Initializing agent system...")

    registry = AgentRegistry()

    # Register all specialized agents
    agents = [
        GeneralAgent(),
        FinanceAgent(),
        HealthAgent(),
        RelationsAgent(),
        TaskManagementAgent(),
        PersonalDevelopmentAgent(),  # NEW: Career, learning, and personal growth
    ]

    for agent in agents:
        registry.register(agent)
        logger.info(f"Registered agent: {agent.name} ({agent.agent_id})")

    logger.info(f"Agent system initialized with {len(registry)} agents")

    return registry


__all__ = [
    "AgentRegistry",
    "get_orchestrator",
    "initialize_agents"
]
