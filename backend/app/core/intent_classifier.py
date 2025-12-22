import json
import re
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

User message: {user_message}

Context (last few messages): {context}

Return ONLY a valid JSON object with this exact structure (no explanations, no markdown, just pure JSON):
{{"intent_type": "general_conversation", "confidence": 0.8, "agent_types": ["general"], "requires_multi_agent": false, "entities": {{}}, "reasoning": "brief explanation"}}

Valid intent_type values: general_conversation, health_query, finance_query, relationship_advice, career_planning, task_management, multi_domain
Valid agent_types values: general, health, finance, relations, personal_development, task_management

CRITICAL: Return ONLY the JSON object. No additional text before or after. Start with {{ and end with }}."""

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

            # Call LLM with JSON mode to ensure valid JSON response
            messages = [{"role": "system", "content": prompt}]
            response = await call_llm(
                messages,
                temperature=0.3,  # Lower temperature for more deterministic classification
                response_format={"type": "json_object"}  # Force JSON output
            )

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
        Uses multiple strategies to extract valid JSON.
        """
        try:
            # Strategy 1: Clean and direct parse
            cleaned = response.strip()

            # Remove BOM and other invisible characters
            cleaned = cleaned.encode('utf-8').decode('utf-8-sig').strip()

            # Strategy 2: Extract from markdown code blocks
            if "```json" in cleaned.lower():
                match = re.search(r'```json\s*\n?(.*?)\n?```', cleaned, re.DOTALL | re.IGNORECASE)
                if match:
                    cleaned = match.group(1).strip()
            elif "```" in cleaned:
                match = re.search(r'```\s*\n?(.*?)\n?```', cleaned, re.DOTALL)
                if match:
                    cleaned = match.group(1).strip()

            # Strategy 3: Find JSON object using regex (look for {..."intent_type"...})
            if not cleaned.startswith('{'):
                match = re.search(r'\{[^{}]*"intent_type"[^{}]*\}', cleaned, re.DOTALL)
                if match:
                    cleaned = match.group(0)
                else:
                    # Try to find any JSON object
                    match = re.search(r'\{.*?\}', cleaned, re.DOTALL)
                    if match:
                        cleaned = match.group(0)

            # Try to parse
            classification = json.loads(cleaned)

            # Validate required fields
            required_fields = ["intent_type", "confidence", "agent_types"]
            for field in required_fields:
                if field not in classification:
                    raise ValueError(f"Missing required field: {field}")

            return classification

        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse classification response: {e}")
            logger.error(f"Raw response (first 200 chars): {response[:200]}")
            logger.debug(f"Full raw response: {response}")

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
