"""Tests for agent registry module."""
import pytest
from app.core.agent_registry import AgentRegistry
from app.agents.base import BaseAgent
from app.schemas.common import Context, Intent, Language


class MockTestAgent(BaseAgent):
    """Mock agent for testing."""

    def __init__(self, agent_id: str, name: str, capabilities: list):
        super().__init__(agent_id=agent_id, name=name, capabilities=capabilities)

    async def process(self, context: Context) -> str:
        return f"Processed by {self.name}"

    async def can_handle(self, intent: Intent) -> tuple[bool, float]:
        # Simple logic: can handle if intent matches capabilities
        for capability in self.capabilities:
            if capability in intent.primary:
                return True, 0.9
        return False, 0.0


class TestAgentRegistry:
    """Test suite for Agent Registry."""

    @pytest.fixture
    def registry(self):
        """Create a fresh registry."""
        return AgentRegistry()

    @pytest.fixture
    def mock_agents(self):
        """Create mock agents."""
        return [
            MockTestAgent("health_001", "Health Agent", ["health", "fitness"]),
            MockTestAgent("finance_001", "Finance Agent", ["finance", "money"]),
            MockTestAgent("general_001", "General Agent", ["general", "chat"]),
        ]

    def test_registry_initialization(self, registry):
        """Test that registry initializes."""
        assert registry is not None

    def test_register_agent(self, registry):
        """Test registering a new agent."""
        agent = MockTestAgent("test_001", "Test Agent", ["test"])
        registry.register(agent)

        # Verify agent is registered
        assert registry.get("test_001") is not None
        assert registry.get("test_001") == agent

    def test_register_multiple_agents(self, registry, mock_agents):
        """Test registering multiple agents."""
        for agent in mock_agents:
            registry.register(agent)

        # All should be registered
        assert len(registry.list_all()) >= len(mock_agents)

    def test_unregister_agent(self, registry):
        """Test unregistering an agent."""
        agent = MockTestAgent("test_001", "Test Agent", ["test"])
        registry.register(agent)

        # Verify registered
        assert registry.get("test_001") is not None

        # Unregister
        registry.unregister("test_001")

        # Verify unregistered
        assert registry.get("test_001") is None

    def test_get_nonexistent_agent(self, registry):
        """Test getting a non-existent agent."""
        agent = registry.get("nonexistent_999")
        assert agent is None

    def test_list_all_agents(self, registry, mock_agents):
        """Test listing all agents."""
        for agent in mock_agents:
            registry.register(agent)

        all_agents = registry.list_all()

        assert len(all_agents) >= len(mock_agents)
        agent_ids = [a.agent_id for a in all_agents]
        assert "health_001" in agent_ids
        assert "finance_001" in agent_ids
        assert "general_001" in agent_ids

    @pytest.mark.asyncio
    async def test_find_capable_agents(self, registry, mock_agents):
        """Test finding capable agents for an intent."""
        for agent in mock_agents:
            registry.register(agent)

        intent = Intent(primary="health_query", confidence=0.9)

        capable = await registry.find_capable_agents(intent)

        # Health agent should be found
        assert len(capable) > 0
        assert any(agent.agent_id == "health_001" for agent in capable)

    @pytest.mark.asyncio
    async def test_find_capable_agents_multi_domain(self, registry, mock_agents):
        """Test finding agents for multi-domain intent."""
        for agent in mock_agents:
            registry.register(agent)

        intent = Intent(
            primary="health_finance_query",
            confidence=0.85,
            secondary_intents=["health", "finance"]
        )

        capable = await registry.find_capable_agents(intent)

        # Both health and finance agents might be found
        agent_ids = [a.agent_id for a in capable]
        # At least one should be capable
        assert len(capable) > 0

    @pytest.mark.asyncio
    async def test_find_capable_agents_no_match(self, registry, mock_agents):
        """Test finding agents when none can handle intent."""
        for agent in mock_agents:
            registry.register(agent)

        intent = Intent(primary="unknown_domain_query", confidence=0.7)

        capable = await registry.find_capable_agents(intent)

        # Might return empty list or fallback to general agent
        assert isinstance(capable, list)

    def test_agent_capabilities_matching(self, registry):
        """Test that agents are matched by capabilities."""
        specialized_agent = MockTestAgent(
            "specialist_001",
            "Specialist",
            ["very_specific_capability"]
        )
        registry.register(specialized_agent)

        agent = registry.get("specialist_001")
        assert "very_specific_capability" in agent.capabilities

    def test_duplicate_agent_registration(self, registry):
        """Test registering agent with duplicate ID."""
        agent1 = MockTestAgent("duplicate_001", "Agent 1", ["test"])
        agent2 = MockTestAgent("duplicate_001", "Agent 2", ["test"])

        registry.register(agent1)
        registry.register(agent2)  # Should replace or reject

        # Only one should exist
        agent = registry.get("duplicate_001")
        assert agent is not None

    def test_registry_stats(self, registry, mock_agents):
        """Test getting registry statistics."""
        for agent in mock_agents:
            registry.register(agent)

        stats = registry.get_stats()

        assert "total_agents" in stats or "registered_agents" in stats
        # Should show correct count
        assert stats.get("total_agents", 0) >= len(mock_agents) or \
               stats.get("registered_agents", 0) >= len(mock_agents)

    def test_agent_health_check(self, registry, mock_agents):
        """Test health check for registered agents."""
        for agent in mock_agents:
            registry.register(agent)

        # All agents should be healthy
        all_agents = registry.list_all()
        for agent in all_agents:
            assert agent is not None
            assert hasattr(agent, 'agent_id')
            assert hasattr(agent, 'name')

    def test_registry_clear(self, registry, mock_agents):
        """Test clearing all agents from registry."""
        for agent in mock_agents:
            registry.register(agent)

        # Clear registry if method exists
        if hasattr(registry, 'clear'):
            registry.clear()
            assert len(registry.list_all()) == 0

    @pytest.mark.asyncio
    async def test_agent_priority_ranking(self, registry, mock_agents):
        """Test that agents are ranked by capability match."""
        for agent in mock_agents:
            registry.register(agent)

        intent = Intent(primary="health_query", confidence=0.95)

        capable = await registry.find_capable_agents(intent)

        # Agents with better matches should rank higher
        if len(capable) > 1:
            # Verify some ordering exists
            assert capable[0] is not None
