from app.agents.base import BaseAgent
from app.schemas.common import (
    Context,
    Intent,
    AgentResponse,
    AgentType,
    IntentType,
    Language
)
from app.agents.task_management.prompts import get_task_management_agent_prompt
from app.services.llm_client import call_llm
import logging

logger = logging.getLogger(__name__)


class TaskManagementAgent(BaseAgent):
    """
    Task and time management agent.

    Specializes in task organization, productivity,
    time management, and goal tracking.
    """

    def __init__(self):
        super().__init__(
            agent_id="task_management_agent_001",
            agent_type=AgentType.TASK_MANAGEMENT,
            name="Task & Time Management Agent",
            description="Specializes in task organization, productivity, and time management",
            capabilities=[
                "task_organization",
                "time_management",
                "productivity_coaching",
                "goal_tracking",
                "prioritization",
                "reminder_management"
            ],
            supported_languages=[Language.POLISH, Language.ENGLISH, Language.GERMAN]
        )

    async def process(self, context: Context, intent: Intent) -> AgentResponse:
        """Process a task management request."""
        try:
            user_context = self._extract_task_context(context, intent)
            system_prompt = get_task_management_agent_prompt(user_context)

            messages = [{"role": "system", "content": system_prompt}]

            for msg in context.history[-4:]:
                messages.append({"role": msg.role, "content": msg.content})

            response_content = call_llm(messages)

            follow_up_actions = self._suggest_follow_up_actions(response_content)

            return AgentResponse(
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                content=response_content,
                confidence=0.85,
                metadata={
                    "intent_type": intent.type.value,
                    "language": context.language.value,
                    "domain": "task_management"
                },
                follow_up_actions=follow_up_actions
            )

        except Exception as e:
            logger.error(f"Error in TaskManagementAgent.process: {e}", exc_info=True)
            return self._error_response(e)

    async def can_handle(self, intent: Intent, context: Context) -> float:
        """Determine if this agent can handle the intent."""
        if not self.supports_language(context.language):
            return 0.0

        if intent.type == IntentType.TASK_MANAGEMENT:
            return 0.95

        task_keywords = [
            "zadanie", "task", "todo", "przypomnienie", "reminder",
            "plan", "planowanie", "planning", "produktywność", "productivity",
            "organizacja", "organization", "cel", "goal", "deadline",
            "kalendarz", "calendar", "harmonogram", "schedule"
        ]

        user_message = context.history[-1].content.lower() if context.history else ""
        if any(keyword in user_message for keyword in task_keywords):
            return 0.75

        return 0.2

    def _extract_task_context(self, context: Context, intent: Intent) -> str:
        """Extract task-related context."""
        context_parts = []

        if intent.entities:
            entities_str = ", ".join([f"{k}: {v}" for k, v in intent.entities.items()])
            context_parts.append(f"Extracted info: {entities_str}")

        # TODO: Load user's existing tasks from database
        # if context.user_profile:
        #     existing_tasks = load_user_tasks(context.user_id)
        #     context_parts.append(f"Existing tasks: {existing_tasks}")

        return "\n".join(context_parts) if context_parts else ""

    def _suggest_follow_up_actions(self, response: str) -> list[str]:
        """Suggest follow-up actions based on response."""
        actions = []

        if "zadanie" in response.lower() or "task" in response.lower():
            actions.append("create_task")

        if "przypomnienie" in response.lower() or "reminder" in response.lower():
            actions.append("set_reminder")

        if "plan" in response.lower() or "schedule" in response.lower():
            actions.append("schedule_event")

        return actions

    def _error_response(self, error: Exception) -> AgentResponse:
        """Generate error response."""
        return AgentResponse(
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            content="Przepraszam, wystąpił problem z przetworzeniem Twojego zapytania o zadania. Spróbuj ponownie.",
            confidence=0.3,
            metadata={"error": str(error)},
            follow_up_actions=[]
        )
