from app.agents.base import BaseAgent
from app.schemas.common import (
    Context,
    Intent,
    AgentResponse,
    AgentType,
    IntentType,
    Language
)
from app.agents.general.prompts import get_general_agent_prompt
from app.services.llm_client import call_llm
import logging

logger = logging.getLogger(__name__)


class GeneralAgent(BaseAgent):
    """
    General conversation agent.

    Handles general conversations, greetings, and requests
    that don't require specialized knowledge.
    """

    def __init__(self):
        super().__init__(
            agent_id="general_agent_001",
            agent_type=AgentType.GENERAL,
            name="General Conversation Agent",
            description="Handles general conversations and acts as fallback for unclear requests",
            capabilities=[
                "general_conversation",
                "greetings",
                "thought_organization",
                "emotional_support",
                "small_talk"
            ],
            supported_languages=[Language.POLISH, Language.ENGLISH, Language.GERMAN]
        )

    async def process(self, context: Context, intent: Intent) -> AgentResponse:
        """
        Process a general conversation request.

        Args:
            context: Conversation context
            intent: Classified intent

        Returns:
            AgentResponse: Agent's response
        """
        try:
            # Prepare context summary
            context_summary = self._prepare_context_summary(context)

            # Get system prompt
            system_prompt = get_general_agent_prompt(context_summary)

            # Prepare messages for LLM
            messages = [
                {"role": "system", "content": system_prompt}
            ]

            # Add recent conversation history (last 5 messages)
            for msg in context.history[-5:]:
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

            # Call LLM
            response_content = call_llm(messages)

            # Create response
            return AgentResponse(
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                content=response_content,
                confidence=0.8,  # General agent has moderate confidence
                metadata={
                    "intent_type": intent.type.value,
                    "language": context.language.value
                },
                follow_up_actions=[]
            )

        except Exception as e:
            logger.error(f"Error in GeneralAgent.process: {e}", exc_info=True)
            # Return fallback response
            return AgentResponse(
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                content="Przepraszam, wystąpił problem z przetworzeniem Twojej wiadomości. Czy możesz spróbować ponownie?",
                confidence=0.3,
                metadata={"error": str(e)},
                follow_up_actions=[]
            )

    async def can_handle(self, intent: Intent, context: Context) -> float:
        """
        Determine if this agent can handle the intent.

        General agent can always handle requests as a fallback,
        but with varying confidence.

        Args:
            intent: User intent
            context: Conversation context

        Returns:
            float: Confidence score
        """
        # Check language support
        if not self.supports_language(context.language):
            return 0.2  # Low confidence for unsupported languages

        # High confidence for general conversation
        if intent.type == IntentType.GENERAL_CONVERSATION:
            return 0.9

        # Medium-low confidence for specialized requests (can act as fallback)
        if intent.type in [
            IntentType.HEALTH_QUERY,
            IntentType.FINANCE_QUERY,
            IntentType.RELATIONSHIP_ADVICE,
            IntentType.CAREER_PLANNING,
            IntentType.TASK_MANAGEMENT
        ]:
            return 0.4  # Can handle but specialized agents are better

        # Default fallback confidence
        return 0.5

    def _prepare_context_summary(self, context: Context) -> str:
        """Prepare a brief summary of conversation context."""
        if not context.history:
            return ""

        # Get last 3 messages
        recent = context.history[-3:]
        summary_parts = []

        for msg in recent:
            summary_parts.append(f"{msg.role}: {msg.content[:100]}")

        return "\n".join(summary_parts)
