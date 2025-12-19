from app.agents.base import BaseAgent
from app.schemas.common import (
    Context,
    Intent,
    AgentResponse,
    AgentType,
    IntentType,
    Language
)
from app.agents.health.prompts import get_health_agent_prompt
from app.services.llm_client import call_llm
import logging

logger = logging.getLogger(__name__)


class HealthAgent(BaseAgent):
    """
    Health and wellness agent.

    Specializes in fitness, nutrition, wellness, and healthy lifestyle.
    """

    def __init__(self):
        super().__init__(
            agent_id="health_agent_001",
            agent_type=AgentType.HEALTH,
            name="Health & Wellness Agent",
            description="Specializes in fitness, nutrition, wellness, and healthy lifestyle support",
            capabilities=[
                "fitness_planning",
                "nutrition_advice",
                "wellness_support",
                "habit_building",
                "exercise_recommendations",
                "mindfulness_support"
            ],
            supported_languages=[Language.POLISH, Language.ENGLISH, Language.GERMAN]
        )

    async def process(self, context: Context, intent: Intent) -> AgentResponse:
        """Process a health-related request."""
        try:
            user_context = self._extract_health_context(context, intent)
            system_prompt = get_health_agent_prompt(user_context)

            messages = [{"role": "system", "content": system_prompt}]

            for msg in context.history[-4:]:
                messages.append({"role": msg.role, "content": msg.content})

            response_content = call_llm(messages)

            # Add disclaimer if medical topic detected
            if self._is_medical_topic(response_content):
                response_content += "\n\n⚠️ Uwaga: To nie jest porada medyczna. W razie wątpliwości skonsultuj się z lekarzem."

            return AgentResponse(
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                content=response_content,
                confidence=0.85,
                metadata={
                    "intent_type": intent.type.value,
                    "language": context.language.value,
                    "domain": "health"
                },
                follow_up_actions=self._suggest_follow_up_actions(intent)
            )

        except Exception as e:
            logger.error(f"Error in HealthAgent.process: {e}", exc_info=True)
            return self._error_response(e)

    async def can_handle(self, intent: Intent, context: Context) -> float:
        """Determine if this agent can handle the intent."""
        if not self.supports_language(context.language):
            return 0.0

        if intent.type == IntentType.HEALTH_QUERY:
            return 0.95

        health_keywords = [
            "zdrowie", "health", "fitness", "trening", "workout", "dieta", "diet",
            "ćwiczenia", "exercise", "odchudzanie", "weight loss", "sport",
            "wellness", "mindfulness", "medytacja", "meditation"
        ]

        user_message = context.history[-1].content.lower() if context.history else ""
        if any(keyword in user_message for keyword in health_keywords):
            return 0.75

        return 0.2

    def _extract_health_context(self, context: Context, intent: Intent) -> str:
        """Extract health-related context."""
        context_parts = []

        if intent.entities:
            entities_str = ", ".join([f"{k}: {v}" for k, v in intent.entities.items()])
            context_parts.append(f"Extracted info: {entities_str}")

        return "\n".join(context_parts) if context_parts else ""

    def _is_medical_topic(self, response: str) -> bool:
        """Check if response discusses medical topics."""
        medical_keywords = [
            "lek", "drug", "medication", "choroba", "disease", "symptom",
            "objaw", "ból", "pain", "diagnoz"
        ]
        return any(keyword in response.lower() for keyword in medical_keywords)

    def _suggest_follow_up_actions(self, intent: Intent) -> list[str]:
        """Suggest follow-up actions."""
        actions = []
        if "fitness" in str(intent.entities).lower():
            actions.append("create_workout_plan")
        if "diet" in str(intent.entities).lower():
            actions.append("track_nutrition")
        return actions

    def _error_response(self, error: Exception) -> AgentResponse:
        """Generate error response."""
        return AgentResponse(
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            content="Przepraszam, wystąpił problem. Spróbuj sformułować pytanie ponownie.",
            confidence=0.3,
            metadata={"error": str(error)},
            follow_up_actions=[]
        )
