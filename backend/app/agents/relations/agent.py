from app.agents.base import BaseAgent
from app.schemas.common import (
    Context,
    Intent,
    AgentResponse,
    AgentType,
    IntentType,
    Language
)
from app.agents.relations.prompts import get_relations_agent_prompt
from app.services.llm_client import call_llm
import logging

logger = logging.getLogger(__name__)


class RelationsAgent(BaseAgent):
    """
    Relationships and emotional support agent.

    Specializes in interpersonal relationships, communication,
    conflict resolution, and emotional wellbeing.
    """

    def __init__(self):
        super().__init__(
            agent_id="relations_agent_001",
            agent_type=AgentType.RELATIONS,
            name="Relations & Emotional Support Agent",
            description="Specializes in relationships, communication, and emotional support",
            capabilities=[
                "relationship_advice",
                "conflict_resolution",
                "emotional_support",
                "communication_coaching",
                "stress_management",
                "empathy_building"
            ],
            supported_languages=[Language.POLISH, Language.ENGLISH, Language.GERMAN]
        )

    async def process(self, context: Context, intent: Intent) -> AgentResponse:
        """Process a relationship/emotional support request."""
        try:
            user_context = self._extract_relations_context(context, intent)
            system_prompt = get_relations_agent_prompt(user_context)

            messages = [{"role": "system", "content": system_prompt}]

            for msg in context.history[-5:]:
                messages.append({"role": msg.role, "content": msg.content})

            response_content = await call_llm(messages)

            # Check for crisis indicators
            if self._detect_crisis(context.history[-1].content if context.history else ""):
                response_content += "\n\n⚠️ WAŻNE: Jeśli czujesz się w kryzysie, skontaktuj się z profesjonalistą. Telefon zaufania: 116 123 (24/7)"

            return AgentResponse(
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                content=response_content,
                confidence=0.85,
                metadata={
                    "intent_type": intent.type.value,
                    "language": context.language.value,
                    "domain": "relations"
                },
                follow_up_actions=[]
            )

        except Exception as e:
            logger.error(f"Error in RelationsAgent.process: {e}", exc_info=True)
            return self._error_response(e)

    async def can_handle(self, intent: Intent, context: Context) -> float:
        """Determine if this agent can handle the intent."""
        if not self.supports_language(context.language):
            return 0.0

        if intent.type == IntentType.RELATIONSHIP_ADVICE:
            return 0.95

        relations_keywords = [
            "związek", "relationship", "konflikt", "conflict", "emocje", "emotions",
            "stres", "stress", "komunikacja", "communication", "rodzina", "family",
            "przyjaciele", "friends", "partnerstwo", "partnership", "kłótnia", "argument"
        ]

        user_message = context.history[-1].content.lower() if context.history else ""
        if any(keyword in user_message for keyword in relations_keywords):
            return 0.75

        return 0.2

    def _extract_relations_context(self, context: Context, intent: Intent) -> str:
        """Extract relationship context."""
        context_parts = []

        if intent.entities:
            entities_str = ", ".join([f"{k}: {v}" for k, v in intent.entities.items()])
            context_parts.append(f"Extracted info: {entities_str}")

        return "\n".join(context_parts) if context_parts else ""

    def _detect_crisis(self, message: str) -> bool:
        """Detect potential mental health crisis indicators."""
        crisis_keywords = [
            "samobójstwo", "suicide", "chcę umrzeć", "want to die",
            "nie chcę żyć", "don't want to live", "skończyć z sobą"
        ]
        return any(keyword in message.lower() for keyword in crisis_keywords)

    def _error_response(self, error: Exception) -> AgentResponse:
        """Generate error response."""
        return AgentResponse(
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            content="Przepraszam, wystąpił problem. Pamiętaj, że zawsze możesz porozmawiać ze mną lub skontaktować się z profesjonalną pomocą.",
            confidence=0.3,
            metadata={"error": str(error)},
            follow_up_actions=[]
        )
