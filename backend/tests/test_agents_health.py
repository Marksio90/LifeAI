"""Tests for Health Agent."""
import pytest
from unittest.mock import patch, AsyncMock
from app.agents.health.agent import HealthAgent
from app.schemas.common import Context, Language, Intent


class TestHealthAgent:
    """Test suite for Health Agent."""

    @pytest.fixture
    def health_agent(self):
        """Create health agent instance."""
        return HealthAgent()

    @pytest.fixture
    def mock_context(self):
        """Create mock context."""
        return Context(
            session_id="test-session",
            user_id="test-user",
            language=Language.POLISH,
            conversation_history=[],
            user_preferences={}
        )

    def test_health_agent_initialization(self, health_agent):
        """Test health agent initializes correctly."""
        assert health_agent is not None
        assert health_agent.name == "Health Agent"
        assert "health" in health_agent.capabilities

    @pytest.mark.asyncio
    async def test_can_handle_health_intent(self, health_agent):
        """Test agent can handle health-related intents."""
        health_intent = Intent(primary="health_query", confidence=0.9)

        can_handle, confidence = await health_agent.can_handle(health_intent)

        assert can_handle is True
        assert confidence > 0.5

    @pytest.mark.asyncio
    async def test_cannot_handle_finance_intent(self, health_agent):
        """Test agent rejects non-health intents."""
        finance_intent = Intent(primary="finance_query", confidence=0.9)

        can_handle, confidence = await health_agent.can_handle(finance_intent)

        assert can_handle is False or confidence < 0.5

    @pytest.mark.asyncio
    async def test_process_fitness_query(self, health_agent, mock_context):
        """Test processing fitness-related query."""
        mock_context.conversation_history.append({
            "role": "user",
            "content": "Jak zacząć biegać?"
        })

        with patch('app.services.llm_client.call_llm', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = "Zacznij od 15-20 minut joggingu 3x w tygodniu..."

            response = await health_agent.process(mock_context)

            assert response is not None
            assert len(response) > 0
            mock_llm.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_diet_query(self, health_agent, mock_context):
        """Test processing diet-related query."""
        mock_context.conversation_history.append({
            "role": "user",
            "content": "Jaka dieta na odchudzanie?"
        })

        with patch('app.services.llm_client.call_llm', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = "Zbilansowana dieta z deficytem kalorycznym..."

            response = await health_agent.process(mock_context)

            assert response is not None

    @pytest.mark.asyncio
    async def test_process_with_context_history(self, health_agent, mock_context):
        """Test processing with conversation history."""
        from app.schemas.common import Message

        mock_context.conversation_history = [
            Message(role="user", content="Chcę schudnąć"),
            Message(role="assistant", content="Mogę pomóc z planem odchudzania"),
            Message(role="user", content="A ile kalorii powinienem jeść?")
        ]

        with patch('app.services.llm_client.call_llm', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = "Zależy od Twojego BMR..."

            response = await health_agent.process(mock_context)

            # Should use conversation history for context
            assert response is not None

    @pytest.mark.asyncio
    async def test_multilingual_support(self, health_agent):
        """Test agent supports multiple languages."""
        languages = [Language.POLISH, Language.ENGLISH, Language.GERMAN]

        for lang in languages:
            context = Context(
                session_id="test",
                user_id="test",
                language=lang,
                conversation_history=[],
                user_preferences={}
            )

            with patch('app.services.llm_client.call_llm', new_callable=AsyncMock) as mock_llm:
                mock_llm.return_value = "Health advice"

                response = await health_agent.process(context)
                assert response is not None

    def test_agent_capabilities(self, health_agent):
        """Test agent has correct capabilities."""
        assert "health" in health_agent.capabilities
        # Might also have fitness, diet, wellness
        assert len(health_agent.capabilities) > 0

    def test_agent_id_unique(self, health_agent):
        """Test agent has unique ID."""
        assert health_agent.agent_id is not None
        assert len(health_agent.agent_id) > 0

    @pytest.mark.asyncio
    async def test_process_empty_context(self, health_agent):
        """Test processing with minimal context."""
        minimal_context = Context(
            session_id="test",
            user_id="test",
            language=Language.POLISH,
            conversation_history=[],
            user_preferences={}
        )

        minimal_context.conversation_history.append({
            "role": "user",
            "content": "Pomóż mi"
        })

        with patch('app.services.llm_client.call_llm', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = "Jak mogę pomóc z Twoim zdrowiem?"

            response = await health_agent.process(minimal_context)
            assert response is not None
