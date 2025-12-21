import json
from typing import Dict, Any
from app.schemas.common import Intent, IntentType, AgentType, Context, Message
from app.services.llm_client import call_llm
import logging

logger = logging.getLogger(__name__)


class IntentClassifier:
    """
    LLM-based intent classifier.

    Uses a language model to analyze user messages and classify
    their intent, determining which agent(s) should handle the request.
    """

    CLASSIFICATION_PROMPT = """You are an intent classification system for a multi-agent AI platform.

Analyze the user's message and classify their intent. The platform has the following specialized agents:

1. HEALTH AGENT - handles: fitness, diet, medical questions, wellness, mental health, exercise
2. FINANCE AGENT - handles: budgeting, expenses, investments, savings, financial planning, banking
3. RELATIONS AGENT - handles: relationships, communication, conflicts, emotions, social interactions
4. PERSONAL_DEVELOPMENT AGENT - handles: career, education, skills, goals, self-improvement, learning
5. TASK_MANAGEMENT AGENT - handles: tasks, to-do lists, reminders, scheduling, time management
6. GENERAL - handles: general conversation, unclear requests, greetings

You must return a JSON object with this exact structure:
{
  "intent_type": "<one of: general_conversation, health_query, finance_query, relationship_advice, career_planning, task_management, multi_domain>",
  "confidence": <float between 0.0 and 1.0>,
  "agent_types": ["<list of relevant agent types: general, health, finance, relations, personal_development, task_management>"],
  "requires_multi_agent": <true if multiple agents needed, false otherwise>,
  "entities": {
    "<key>": "<value>"
  },
  "reasoning": "<brief explanation of classification>"
}

IMPORTANT:
- If the request involves multiple domains (e.g., "I want to lose weight and save money for gym"), set requires_multi_agent to true and list all relevant agent types
- Confidence should reflect how clear the intent is (0.0-1.0)
- Extract relevant entities (dates, amounts, names, etc.)
- Always return valid JSON only

User message: {user_message}

Context (last few messages): {context}

Return only the JSON object, no other text."""

    async def classify(self, user_message: str, context: Context) -> Intent:
        """
        Classify user intent using LLM.

        Args:
            user_message: The user's latest message
            context: Conversation context

        Returns:
            Intent: Classified intent with confidence and metadata
        """
        try:
            # Prepare context summary (last 3 messages)
            recent_context = self._prepare_context_summary(context)

            # Format prompt
            prompt = self.CLASSIFICATION_PROMPT.format(
                user_message=user_message,
                context=recent_context
            )

            # Call LLM
            messages = [{"role": "system", "content": prompt}]
            response = await call_llm(messages)

            # Parse JSON response
            classification = self._parse_classification(response)

            # Create Intent object
            intent = Intent(
                type=IntentType(classification["intent_type"]),
                confidence=classification["confidence"],
                entities=classification.get("entities", {}),
                agent_types=[AgentType(at) for at in classification["agent_types"]],
                requires_multi_agent=classification.get("requires_multi_agent", False)
            )

            logger.info(
                f"Classified intent: {intent.type.value} "
                f"(confidence: {intent.confidence:.2f}, "
                f"agents: {[at.value for at in intent.agent_types]})"
            )

            return intent

        except Exception as e:
            logger.error(f"Error classifying intent: {e}")
            # Fallback to general conversation
            return Intent(
                type=IntentType.GENERAL_CONVERSATION,
                confidence=0.5,
                agent_types=[AgentType.GENERAL],
                requires_multi_agent=False,
                entities={}
            )

    def _prepare_context_summary(self, context: Context) -> str:
        """Prepare a summary of recent context for the classifier."""
        if not context.history:
            return "No previous context."

        # Get last 3 messages
        recent_messages = context.history[-3:]
        summary = []
        for msg in recent_messages:
            summary.append(f"{msg.role}: {msg.content}")

        return "\n".join(summary)

    def _parse_classification(self, response: str) -> Dict[str, Any]:
        """
        Parse LLM response into classification dict.

        Handles potential JSON parsing errors and provides fallback.
        """
        try:
            # Try to extract JSON from response
            # Sometimes LLM adds extra text, so we try to find JSON block
            response = response.strip()

            # If response contains markdown code blocks, extract JSON
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                response = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                response = response[start:end].strip()

            classification = json.loads(response)

            # Validate required fields
            required_fields = ["intent_type", "confidence", "agent_types"]
            for field in required_fields:
                if field not in classification:
                    raise ValueError(f"Missing required field: {field}")

            return classification

        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse classification response: {e}")
            logger.error(f"Raw response: {response}")

            # Return fallback classification
            return {
                "intent_type": "general_conversation",
                "confidence": 0.3,
                "agent_types": ["general"],
                "requires_multi_agent": False,
                "entities": {},
                "reasoning": "Failed to parse classification, using fallback"
            }


# Singleton instance
_intent_classifier = IntentClassifier()


async def classify_intent(user_message: str, context: Context) -> Intent:
    """
    Convenience function to classify intent.

    Args:
        user_message: User's message
        context: Conversation context

    Returns:
        Intent: Classified intent
    """
    return await _intent_classifier.classify(user_message, context)
