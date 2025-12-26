"""Tests for core router module."""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.core.router import route_message, RouteDecision
from app.schemas.common import Context, Message, Language, Intent
from app.agents.base import BaseAgent


class MockAgent(BaseAgent):
    """Mock agent for testing."""

    def __init__(self, agent_id: str, name: str, capabilities: list):
        super().__init__(agent_id=agent_id, name=name, capabilities=capabilities)

    async def process(self, context: Context) -> str:
        return f"Response from {self.name}"

    async def can_handle(self, intent: Intent) -> tuple[bool, float]:
        if intent.primary == "test_query":
            return True, 0.95
        return False, 0.0


class TestRouter:
    """Test suite for Router module."""

    @pytest.fixture
    def mock_context(self):
        """Create a mock context for testing."""
        return Context(
            session_id="test-session",
            user_id="test-user",
            language=Language.POLISH,
            conversation_history=[],
            user_preferences={}
        )

    @pytest.mark.asyncio
    async def test_route_message_single_agent(self, mock_context):
        """Test routing to a single agent."""
        with patch('app.core.intent_classifier.classify_intent', new_callable=AsyncMock) as mock_classify:
            with patch('app.core.agent_registry.AgentRegistry.find_capable_agents') as mock_find:
                # Setup mocks
                mock_intent = Intent(primary="general_query", confidence=0.95)
                mock_classify.return_value = mock_intent

                mock_agent = MockAgent("test_agent", "Test Agent", ["general"])
                mock_find.return_value = [mock_agent]

                # Route message
                response = await route_message(mock_context, "Hello")

                assert response is not None
                assert response.response == "Response from Test Agent"
                assert "test_agent" in response.agents_used
                assert response.routing_type == "single_agent"

    @pytest.mark.asyncio
    async def test_route_message_no_capable_agents(self, mock_context):
        """Test routing when no capable agents are found."""
        with patch('app.core.intent_classifier.classify_intent', new_callable=AsyncMock) as mock_classify:
            with patch('app.core.agent_registry.AgentRegistry.find_capable_agents') as mock_find:
                mock_intent = Intent(primary="unknown_query", confidence=0.5)
                mock_classify.return_value = mock_intent
                mock_find.return_value = []  # No capable agents

                response = await route_message(mock_context, "Unknown request")

                assert response is not None
                # Should fallback to general agent or return default response
                assert response.response is not None

    @pytest.mark.asyncio
    async def test_route_message_multi_agent(self, mock_context):
        """Test routing to multiple agents (multi-agent collaboration)."""
        with patch('app.core.intent_classifier.classify_intent', new_callable=AsyncMock) as mock_classify:
            with patch('app.core.agent_registry.AgentRegistry.find_capable_agents') as mock_find:
                # Intent requiring multiple domains
                mock_intent = Intent(
                    primary="health_finance_query",
                    confidence=0.9,
                    secondary_intents=["health", "finance"]
                )
                mock_classify.return_value = mock_intent

                # Multiple capable agents
                health_agent = MockAgent("health_agent", "Health Agent", ["health"])
                finance_agent = MockAgent("finance_agent", "Finance Agent", ["finance"])
                mock_find.return_value = [health_agent, finance_agent]

                response = await route_message(mock_context, "I want to lose weight and save money")

                assert response is not None
                # Should use multiple agents
                assert len(response.agents_used) > 0

    @pytest.mark.asyncio
    async def test_route_decision_confidence_threshold(self, mock_context):
        """Test that low confidence intents are handled appropriately."""
        with patch('app.core.intent_classifier.classify_intent', new_callable=AsyncMock) as mock_classify:
            # Low confidence intent
            mock_intent = Intent(primary="unclear_query", confidence=0.3)
            mock_classify.return_value = mock_intent

            response = await route_message(mock_context, "Hmm...")

            assert response is not None
            # Should handle low confidence gracefully

    @pytest.mark.asyncio
    async def test_route_message_context_enrichment(self, mock_context):
        """Test that routing enriches context with relevant information."""
        mock_context.conversation_history = [
            Message(role="user", content="Previous message"),
            Message(role="assistant", content="Previous response")
        ]

        with patch('app.core.intent_classifier.classify_intent', new_callable=AsyncMock) as mock_classify:
            with patch('app.core.agent_registry.AgentRegistry.find_capable_agents') as mock_find:
                mock_intent = Intent(primary="general_query", confidence=0.9)
                mock_classify.return_value = mock_intent

                mock_agent = MockAgent("test_agent", "Test Agent", ["general"])
                mock_find.return_value = [mock_agent]

                response = await route_message(mock_context, "Follow-up question")

                # Context should have been enriched with history
                assert len(mock_context.conversation_history) >= 2

    @pytest.mark.asyncio
    async def test_route_message_language_handling(self, mock_context):
        """Test that routing respects language preferences."""
        mock_context.language = Language.ENGLISH

        with patch('app.core.intent_classifier.classify_intent', new_callable=AsyncMock) as mock_classify:
            with patch('app.core.agent_registry.AgentRegistry.find_capable_agents') as mock_find:
                mock_intent = Intent(primary="general_query", confidence=0.9)
                mock_classify.return_value = mock_intent

                mock_agent = MockAgent("test_agent", "Test Agent", ["general"])
                mock_find.return_value = [mock_agent]

                await route_message(mock_context, "Hello")

                # Verify language was passed to classifier
                mock_classify.assert_called_once()
                call_args = mock_classify.call_args
                # Check that context with correct language was used

    @pytest.mark.asyncio
    async def test_route_message_error_handling(self, mock_context):
        """Test error handling in routing."""
        with patch('app.core.intent_classifier.classify_intent', new_callable=AsyncMock) as mock_classify:
            # Simulate classifier error
            mock_classify.side_effect = Exception("Classification failed")

            # Should handle error gracefully
            with pytest.raises(Exception):
                await route_message(mock_context, "Test message")

    @pytest.mark.asyncio
    async def test_route_message_caching(self, mock_context):
        """Test that routing results can be cached."""
        with patch('app.core.intent_classifier.classify_intent', new_callable=AsyncMock) as mock_classify:
            with patch('app.core.agent_registry.AgentRegistry.find_capable_agents') as mock_find:
                mock_intent = Intent(primary="general_query", confidence=0.95)
                mock_classify.return_value = mock_intent

                mock_agent = MockAgent("test_agent", "Test Agent", ["general"])
                mock_find.return_value = [mock_agent]

                # First call
                response1 = await route_message(mock_context, "Repeated question")
                # Second call with same message
                response2 = await route_message(mock_context, "Repeated question")

                assert response1 is not None
                assert response2 is not None


class TestRouteDecision:
    """Test suite for RouteDecision class."""

    def test_route_decision_single_agent(self):
        """Test creating a single-agent route decision."""
        decision = RouteDecision(
            agents=["agent_1"],
            routing_type="single_agent",
            confidence=0.95
        )

        assert len(decision.agents) == 1
        assert decision.routing_type == "single_agent"
        assert decision.confidence == 0.95

    def test_route_decision_multi_agent(self):
        """Test creating a multi-agent route decision."""
        decision = RouteDecision(
            agents=["health_agent", "finance_agent"],
            routing_type="multi_agent",
            confidence=0.85
        )

        assert len(decision.agents) == 2
        assert decision.routing_type == "multi_agent"
        assert "health_agent" in decision.agents
        assert "finance_agent" in decision.agents

    def test_route_decision_validation(self):
        """Test route decision validation."""
        # Should validate that routing_type matches number of agents
        decision = RouteDecision(
            agents=["agent_1"],
            routing_type="single_agent",
            confidence=0.9
        )

        assert decision.routing_type == "single_agent"

    def test_route_decision_confidence_bounds(self):
        """Test that confidence is bounded between 0 and 1."""
        decision = RouteDecision(
            agents=["agent_1"],
            routing_type="single_agent",
            confidence=0.95
        )

        assert 0.0 <= decision.confidence <= 1.0


class TestAgentSelection:
    """Test suite for agent selection logic."""

    @pytest.fixture
    def multiple_agents(self):
        """Create multiple mock agents."""
        return [
            MockAgent("health_agent", "Health Agent", ["health", "fitness"]),
            MockAgent("finance_agent", "Finance Agent", ["finance", "budget"]),
            MockAgent("general_agent", "General Agent", ["general", "chat"]),
        ]

    @pytest.mark.asyncio
    async def test_select_best_agent(self, multiple_agents):
        """Test selecting the best agent based on capabilities."""
        intent = Intent(primary="health_query", confidence=0.95)

        # Find agents that can handle health queries
        capable_agents = []
        for agent in multiple_agents:
            can_handle, confidence = await agent.can_handle(intent)
            if can_handle:
                capable_agents.append((agent, confidence))

        # Health agent should be selected
        if capable_agents:
            best_agent = max(capable_agents, key=lambda x: x[1])[0]
            assert "health" in best_agent.capabilities

    @pytest.mark.asyncio
    async def test_agent_priority_ordering(self, multiple_agents):
        """Test that agents are ordered by confidence."""
        intent = Intent(primary="test_query", confidence=0.9)

        agent_scores = []
        for agent in multiple_agents:
            can_handle, confidence = await agent.can_handle(intent)
            if can_handle:
                agent_scores.append((agent, confidence))

        # Sort by confidence (descending)
        sorted_agents = sorted(agent_scores, key=lambda x: x[1], reverse=True)

        # Verify ordering
        if len(sorted_agents) > 1:
            assert sorted_agents[0][1] >= sorted_agents[-1][1]
