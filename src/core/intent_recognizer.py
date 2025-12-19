"""
Intent Recognizer - Analyzes user input to determine intent
Uses LLM to classify user requests into appropriate categories
"""
from typing import Optional, Dict, Any
from loguru import logger
import json

from openai import AsyncOpenAI
from .models import Intent, IntentType
from config import settings


class IntentRecognizer:
    """
    Uses LLM to recognize user intent and extract entities
    """

    def __init__(self, model: str = None):
        self.model = model or settings.default_llm_model
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def recognize(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Intent:
        """
        Recognize intent from user message
        Returns Intent object with classification and entities
        """
        try:
            # Build prompt with context
            prompt = self._build_prompt(user_message, context)

            # Call LLM
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            # Parse response
            result = json.loads(response.choices[0].message.content)

            intent = Intent(
                intent_type=IntentType(result.get("intent_type", "general")),
                confidence=result.get("confidence", 0.5),
                sub_intents=[IntentType(si) for si in result.get("sub_intents", [])],
                extracted_entities=result.get("entities", {})
            )

            return intent

        except Exception as e:
            logger.error(f"Error recognizing intent: {str(e)}")
            # Return default intent on error
            return Intent(
                intent_type=IntentType.GENERAL,
                confidence=0.5,
                sub_intents=[],
                extracted_entities={}
            )

    def _get_system_prompt(self) -> str:
        """System prompt for intent recognition"""
        return """You are an intent classification system for a life guidance AI platform.

Your task is to analyze user messages and classify them into one of these categories:
- health: Questions about physical/mental health, fitness, diet, sleep, wellness
- finance: Questions about money, budgeting, investments, expenses, financial planning
- psychology: Questions about emotions, thoughts, mental patterns, cognitive issues
- relationships: Questions about interpersonal relationships, communication, conflicts
- personal_development: Questions about goals, career, learning, habits, self-improvement
- general: General conversation, greetings, unclear requests
- multi_domain: Questions that span multiple domains

Return a JSON object with:
{
  "intent_type": "one of the categories above",
  "confidence": float between 0 and 1,
  "sub_intents": ["list", "of", "secondary", "intents"],
  "entities": {
    "key": "value pairs of extracted information"
  }
}

Examples:
User: "I'm feeling stressed about work and it's affecting my sleep"
Output: {"intent_type": "multi_domain", "confidence": 0.9, "sub_intents": ["psychology", "health"], "entities": {"stressor": "work", "symptom": "sleep_problems"}}

User: "How should I invest $10,000?"
Output: {"intent_type": "finance", "confidence": 0.95, "sub_intents": [], "entities": {"amount": 10000, "action": "invest"}}

User: "Hello, how are you?"
Output: {"intent_type": "general", "confidence": 1.0, "sub_intents": [], "entities": {}}
"""

    def _build_prompt(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build prompt with context"""
        prompt = f"User message: {user_message}\n"

        if context:
            prompt += f"\nContext: {json.dumps(context, indent=2)}\n"

        prompt += "\nClassify this message and return JSON."
        return prompt
