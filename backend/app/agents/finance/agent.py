from app.agents.base import BaseAgent
from app.schemas.common import (
    Context,
    Intent,
    AgentResponse,
    AgentType,
    IntentType,
    Language
)
from app.agents.finance.prompts import get_finance_agent_prompt
from app.services.llm_client import call_llm
import logging

logger = logging.getLogger(__name__)


class FinanceAgent(BaseAgent):
    """
    Finance and budgeting agent.

    Specializes in personal finance, budgeting, savings,
    and financial planning.
    """

    def __init__(self):
        super().__init__(
            agent_id="finance_agent_001",
            agent_type=AgentType.FINANCE,
            name="Finance & Budgeting Agent",
            description="Specializes in personal finance, budgeting, savings, and financial planning",
            capabilities=[
                "budget_management",
                "expense_tracking",
                "savings_planning",
                "financial_education",
                "debt_management",
                "financial_goal_setting"
            ],
            supported_languages=[Language.POLISH, Language.ENGLISH, Language.GERMAN]
        )

    async def process(self, context: Context, intent: Intent) -> AgentResponse:
        """
        Process a finance-related request.

        Args:
            context: Conversation context
            intent: Classified intent

        Returns:
            AgentResponse: Agent's response
        """
        try:
            # Extract financial context
            user_context = self._extract_financial_context(context, intent)

            # Get system prompt
            system_prompt = get_finance_agent_prompt(user_context)

            # Prepare messages
            messages = [
                {"role": "system", "content": system_prompt}
            ]

            # Add relevant conversation history
            for msg in context.history[-4:]:
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

            # Call LLM
            response_content = await call_llm(messages)

            # Determine follow-up actions
            follow_up_actions = self._suggest_follow_up_actions(intent, response_content)

            return AgentResponse(
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                content=response_content,
                confidence=0.85,
                metadata={
                    "intent_type": intent.type.value,
                    "language": context.language.value,
                    "domain": "finance",
                    "entities": intent.entities
                },
                follow_up_actions=follow_up_actions
            )

        except Exception as e:
            logger.error(f"Error in FinanceAgent.process: {e}", exc_info=True)
            return self._error_response(e)

    async def can_handle(self, intent: Intent, context: Context) -> float:
        """
        Determine if this agent can handle the intent.

        Args:
            intent: User intent
            context: Conversation context

        Returns:
            float: Confidence score
        """
        # Check language support
        if not self.supports_language(context.language):
            return 0.0

        # High confidence for finance queries
        if intent.type == IntentType.FINANCE_QUERY:
            return 0.95

        # Check for finance-related keywords in entities
        finance_keywords = [
            "budżet", "budget", "pieniądze", "money", "wydatki", "expenses",
            "oszczędności", "savings", "kredyt", "loan", "inwestycja", "investment",
            "rachunek", "bill", "płatność", "payment", "bank", "konto", "account"
        ]

        user_message = context.history[-1].content.lower() if context.history else ""
        if any(keyword in user_message for keyword in finance_keywords):
            return 0.75

        # Low confidence for other intents
        return 0.2

    def _extract_financial_context(self, context: Context, intent: Intent) -> str:
        """Extract relevant financial context from conversation."""
        context_parts = []

        # Add extracted entities
        if intent.entities:
            entities_str = ", ".join([f"{k}: {v}" for k, v in intent.entities.items()])
            context_parts.append(f"Extracted info: {entities_str}")

        # Add user profile financial data (if available)
        if context.user_profile:
            # TODO: Extract financial preferences, budget limits, etc.
            pass

        return "\n".join(context_parts) if context_parts else ""

    def _suggest_follow_up_actions(self, intent: Intent, response: str) -> list[str]:
        """Suggest follow-up actions based on the interaction."""
        actions = []

        # Example follow-up actions
        if "budżet" in response.lower() or "budget" in response.lower():
            actions.append("setup_budget_tracking")

        if "oszczędności" in response.lower() or "savings" in response.lower():
            actions.append("set_savings_goal")

        return actions

    def _error_response(self, error: Exception) -> AgentResponse:
        """Generate error response."""
        return AgentResponse(
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            content="Przepraszam, wystąpił problem podczas analizy Twojego zapytania finansowego. Spróbuj sformułować pytanie inaczej.",
            confidence=0.3,
            metadata={"error": str(error)},
            follow_up_actions=[]
        )
