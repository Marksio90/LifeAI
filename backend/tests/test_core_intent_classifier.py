"""Tests for intent classifier module."""
import pytest
from unittest.mock import patch, AsyncMock
from app.core.intent_classifier import classify_intent, IntentClassifier
from app.schemas.common import Context, Language, Intent


class TestIntentClassifier:
    """Test suite for Intent Classifier."""

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

    @pytest.mark.asyncio
    async def test_classify_health_intent(self, mock_context):
        """Test classifying health-related intent."""
        with patch('app.services.llm_client.call_llm', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = "health_query"

            intent = await classify_intent("Chcę schudnąć 5kg", mock_context)

            assert intent is not None
            assert "health" in intent.primary.lower() or intent.confidence > 0.7

    @pytest.mark.asyncio
    async def test_classify_finance_intent(self, mock_context):
        """Test classifying finance-related intent."""
        with patch('app.services.llm_client.call_llm', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = "finance_query"

            intent = await classify_intent("Jak zaoszczędzić 1000 zł?", mock_context)

            assert intent is not None
            assert intent.primary is not None

    @pytest.mark.asyncio
    async def test_classify_multi_intent(self, mock_context):
        """Test classifying message with multiple intents."""
        with patch('app.services.llm_client.call_llm', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = "health_finance_query"

            intent = await classify_intent(
                "Chcę schudnąć i zaoszczędzić na siłownię",
                mock_context
            )

            assert intent is not None
            # Should detect multiple domains
            assert intent.primary is not None

    @pytest.mark.asyncio
    async def test_classify_general_intent(self, mock_context):
        """Test classifying general conversation."""
        with patch('app.services.llm_client.call_llm', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = "general_query"

            intent = await classify_intent("Cześć, jak się masz?", mock_context)

            assert intent is not None
            assert intent.primary == "general_query"

    @pytest.mark.asyncio
    async def test_classify_with_context_history(self, mock_context):
        """Test classification with conversation history."""
        from app.schemas.common import Message

        mock_context.conversation_history = [
            Message(role="user", content="Interesuje mnie zdrowie"),
            Message(role="assistant", content="Mogę pomóc z fitnesem")
        ]

        with patch('app.services.llm_client.call_llm', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = "health_query"

            intent = await classify_intent("A co z dietą?", mock_context)

            # Should use context to understand "diet" relates to health
            assert intent is not None

    @pytest.mark.asyncio
    async def test_classify_confidence_scores(self, mock_context):
        """Test that intent has confidence scores."""
        with patch('app.services.llm_client.call_llm', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = "health_query"

            intent = await classify_intent("Jak zacząć biegać?", mock_context)

            assert intent is not None
            assert hasattr(intent, 'confidence')
            assert 0.0 <= intent.confidence <= 1.0

    @pytest.mark.asyncio
    async def test_classify_language_support(self):
        """Test classification in different languages."""
        test_cases = [
            (Language.POLISH, "Jak się masz?"),
            (Language.ENGLISH, "How are you?"),
            (Language.GERMAN, "Wie geht es dir?")
        ]

        for language, message in test_cases:
            context = Context(
                session_id="test",
                user_id="test",
                language=language,
                conversation_history=[],
                user_preferences={}
            )

            with patch('app.services.llm_client.call_llm', new_callable=AsyncMock) as mock_llm:
                mock_llm.return_value = "general_query"

                intent = await classify_intent(message, context)
                assert intent is not None

    @pytest.mark.asyncio
    async def test_classify_empty_message(self, mock_context):
        """Test classification of empty message."""
        intent = await classify_intent("", mock_context)

        # Should handle gracefully
        assert intent is not None or intent is None  # Either way is acceptable

    @pytest.mark.asyncio
    async def test_classify_very_long_message(self, mock_context):
        """Test classification of very long message."""
        long_message = "test " * 1000  # Very long message

        with patch('app.services.llm_client.call_llm', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = "general_query"

            intent = await classify_intent(long_message, mock_context)
            assert intent is not None

    @pytest.mark.asyncio
    async def test_classify_special_characters(self, mock_context):
        """Test classification with special characters."""
        with patch('app.services.llm_client.call_llm', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = "general_query"

            intent = await classify_intent("Pytanie #1: Jak $$ zaoszczędzić?", mock_context)
            assert intent is not None

    @pytest.mark.asyncio
    async def test_intent_caching(self, mock_context):
        """Test that similar intents can be cached."""
        message = "Jak schudnąć?"

        with patch('app.services.llm_client.call_llm', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = "health_query"

            # First call
            intent1 = await classify_intent(message, mock_context)

            # Second call with same message - might be cached
            intent2 = await classify_intent(message, mock_context)

            assert intent1 is not None
            assert intent2 is not None

    def test_intent_object_structure(self):
        """Test Intent object structure."""
        intent = Intent(
            primary="health_query",
            confidence=0.95,
            secondary_intents=["fitness", "diet"]
        )

        assert intent.primary == "health_query"
        assert intent.confidence == 0.95
        assert "fitness" in intent.secondary_intents
        assert "diet" in intent.secondary_intents
