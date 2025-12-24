import json
import re
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from app.schemas.common import Intent, IntentType, AgentType, Context, Message
from app.services.llm_client import call_llm
import logging

logger = logging.getLogger(__name__)


class ClassificationCache:
    """Simple in-memory cache for intent classifications."""

    def __init__(self, ttl_seconds: int = 300):
        """
        Initialize classification cache.

        Args:
            ttl_seconds: Time to live for cache entries in seconds
        """
        self._cache: Dict[str, Tuple[Intent, datetime]] = {}
        self._ttl = timedelta(seconds=ttl_seconds)

    def get(self, message: str, context_hash: str) -> Optional[Intent]:
        """Get cached classification if available and not expired."""
        cache_key = self._make_key(message, context_hash)

        if cache_key in self._cache:
            intent, timestamp = self._cache[cache_key]

            # Check if expired
            if datetime.now() - timestamp < self._ttl:
                logger.debug(f"Cache HIT for message: {message[:30]}...")
                return intent
            else:
                # Remove expired entry
                del self._cache[cache_key]

        return None

    def set(self, message: str, context_hash: str, intent: Intent):
        """Cache classification result."""
        cache_key = self._make_key(message, context_hash)
        self._cache[cache_key] = (intent, datetime.now())

        # Simple cleanup: if cache grows too large, remove oldest entries
        if len(self._cache) > 1000:
            oldest_keys = sorted(
                self._cache.keys(),
                key=lambda k: self._cache[k][1]
            )[:100]
            for key in oldest_keys:
                del self._cache[key]

    def _make_key(self, message: str, context_hash: str) -> str:
        """Generate cache key from message and context."""
        content = f"{message}:{context_hash}"
        return hashlib.md5(content.encode()).hexdigest()


class IntentClassifier:
    """
    Enhanced LLM-based intent classifier with caching and multi-intent detection.

    Uses a language model to analyze user messages and classify
    their intent, determining which agent(s) should handle the request.

    Features:
    - Classification caching (5min TTL)
    - Multi-intent detection
    - Entity extraction
    - Confidence thresholding
    - Intent history tracking
    """

    def __init__(self):
        """Initialize classifier with cache and history tracking."""
        self._cache = ClassificationCache(ttl_seconds=300)  # 5 minute cache
        self._intent_history: Dict[str, List[Intent]] = {}  # user_id -> intent list
        self._confidence_threshold = 0.6  # Minimum confidence for classification

    CLASSIFICATION_PROMPT = """You are an advanced intent classification system for a multi-agent AI platform.

Analyze the user's message and classify their intent. The platform has the following specialized agents:

1. HEALTH AGENT - handles: fitness, diet, medical questions, wellness, mental health, exercise, nutrition, sleep
2. FINANCE AGENT - handles: budgeting, expenses, investments, savings, financial planning, banking, debt management
3. RELATIONS AGENT - handles: relationships, communication, conflicts, emotions, social interactions, family, friends
4. PERSONAL_DEVELOPMENT AGENT - handles: career, education, skills, goals, self-improvement, learning, productivity
5. TASK_MANAGEMENT AGENT - handles: tasks, to-do lists, reminders, scheduling, time management, organization
6. GENERAL - handles: general conversation, unclear requests, greetings, chitchat

User message: {user_message}

Context (last few messages): {context}

Previous intent pattern: {intent_history}

INSTRUCTIONS:
1. Identify PRIMARY intent (main purpose of the message)
2. Detect SECONDARY intents if multiple domains are involved
3. Extract KEY ENTITIES (numbers, dates, amounts, names, specific items)
4. Set requires_multi_agent=true if user explicitly needs multiple agents (e.g., "I want to lose weight AND save money")
5. Consider conversation history for context-aware classification

ENTITY EXTRACTION EXAMPLES:
- "I want to save 1000 PLN" → entities: {{"amount": 1000, "currency": "PLN"}}
- "I need to lose 5 kg by June" → entities: {{"weight": 5, "unit": "kg", "deadline": "June"}}
- "Help me plan a workout 3 times per week" → entities: {{"frequency": 3, "unit": "times per week"}}

MULTI-INTENT DETECTION:
- If message clearly involves 2+ domains, set requires_multi_agent=true and list all relevant agents
- Example: "I want to get fit and need a budget for gym membership" → health + finance

Return ONLY a valid JSON object with this exact structure:
{{"intent_type": "health_query", "confidence": 0.85, "agent_types": ["health"], "requires_multi_agent": false, "entities": {{"weight": 5}}, "reasoning": "User asking about weight loss", "secondary_intents": []}}

Valid intent_type values: general_conversation, health_query, finance_query, relationship_advice, career_planning, task_management, multi_domain
Valid agent_types values: general, health, finance, relations, personal_development, task_management

CRITICAL: Return ONLY the JSON object. No markdown, no code blocks, no explanations. Start with {{ and end with }}."""

    async def classify(
        self,
        user_message: str,
        context: Context,
        user_id: Optional[str] = None
    ) -> Intent:
        """
        Classify user intent using LLM with caching and history awareness.

        Args:
            user_message: The user's latest message
            context: Conversation context
            user_id: Optional user ID for history tracking

        Returns:
            Intent: Classified intent with confidence and metadata
        """
        try:
            # Prepare context summary (last 3 messages)
            recent_context = self._prepare_context_summary(context)
            context_hash = self._hash_context(recent_context)

            # Check cache first
            cached_intent = self._cache.get(user_message, context_hash)
            if cached_intent:
                logger.info(f"Using cached classification for: {user_message[:50]}...")
                return cached_intent

            # Get intent history for this user
            intent_history = self._get_intent_history_summary(user_id)

            # Format prompt
            prompt = self.CLASSIFICATION_PROMPT.format(
                user_message=user_message,
                context=recent_context,
                intent_history=intent_history
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

            # Apply confidence threshold - fallback to general if too low
            if intent.confidence < self._confidence_threshold:
                logger.warning(
                    f"Low confidence ({intent.confidence:.2f}) - falling back to general"
                )
                intent = Intent(
                    type=IntentType.GENERAL_CONVERSATION,
                    confidence=0.5,
                    agent_types=[AgentType.GENERAL],
                    requires_multi_agent=False,
                    entities={}
                )

            # Cache the result
            self._cache.set(user_message, context_hash, intent)

            # Track intent history
            if user_id:
                self._add_to_intent_history(user_id, intent)

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

    def _hash_context(self, context_summary: str) -> str:
        """Generate hash of context for cache key."""
        return hashlib.md5(context_summary.encode()).hexdigest()[:8]

    def _get_intent_history_summary(self, user_id: Optional[str]) -> str:
        """
        Get summary of user's recent intent history.

        Args:
            user_id: User identifier

        Returns:
            String summary of recent intents
        """
        if not user_id or user_id not in self._intent_history:
            return "No previous intent history"

        recent_intents = self._intent_history[user_id][-5:]  # Last 5 intents

        if not recent_intents:
            return "No previous intent history"

        # Count intent types
        intent_counts = {}
        for intent in recent_intents:
            intent_type = intent.type.value
            intent_counts[intent_type] = intent_counts.get(intent_type, 0) + 1

        # Format summary
        summary_parts = []
        for intent_type, count in intent_counts.items():
            summary_parts.append(f"{intent_type} ({count}x)")

        return f"Recent patterns: {', '.join(summary_parts)}"

    def _add_to_intent_history(self, user_id: str, intent: Intent):
        """
        Add intent to user's history.

        Args:
            user_id: User identifier
            intent: Classified intent
        """
        if user_id not in self._intent_history:
            self._intent_history[user_id] = []

        self._intent_history[user_id].append(intent)

        # Keep only last 20 intents per user
        if len(self._intent_history[user_id]) > 20:
            self._intent_history[user_id] = self._intent_history[user_id][-20:]

    def get_intent_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Get intent classification statistics for a user.

        Args:
            user_id: User identifier

        Returns:
            Dictionary with statistics
        """
        if user_id not in self._intent_history:
            return {
                "total_classifications": 0,
                "intent_distribution": {},
                "average_confidence": 0.0,
                "multi_agent_requests": 0
            }

        intents = self._intent_history[user_id]

        # Calculate statistics
        intent_counts = {}
        total_confidence = 0.0
        multi_agent_count = 0

        for intent in intents:
            intent_type = intent.type.value
            intent_counts[intent_type] = intent_counts.get(intent_type, 0) + 1
            total_confidence += intent.confidence

            if intent.requires_multi_agent:
                multi_agent_count += 1

        return {
            "total_classifications": len(intents),
            "intent_distribution": intent_counts,
            "average_confidence": total_confidence / len(intents) if intents else 0.0,
            "multi_agent_requests": multi_agent_count,
            "most_common_intent": max(intent_counts.items(), key=lambda x: x[1])[0] if intent_counts else None
        }

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

            # Remove potential text before/after JSON (e.g., "Here is the classification: {...}")
            # Look for first { and last }
            first_brace = cleaned.find('{')
            last_brace = cleaned.rfind('}')
            if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                cleaned = cleaned[first_brace:last_brace + 1]
                logger.debug(f"Extracted JSON from position {first_brace} to {last_brace}")

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
                # First try: Look for JSON with intent_type (handle nested braces)
                match = re.search(r'\{(?:[^{}]|(?:\{[^{}]*\}))*"intent_type"(?:[^{}]|(?:\{[^{}]*\}))*\}', cleaned, re.DOTALL)
                if match:
                    cleaned = match.group(0)
                else:
                    # Second try: Find any JSON object (greedy match)
                    match = re.search(r'\{.*\}', cleaned, re.DOTALL)
                    if match:
                        cleaned = match.group(0)
                    else:
                        logger.warning(f"No JSON object found in response, trying last resort")
                        # Last resort: just try to parse as-is
                        pass

            # Try to parse
            classification = json.loads(cleaned)
            logger.debug(f"Successfully parsed JSON classification: {classification.get('intent_type')}")

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


async def classify_intent(
    user_message: str,
    context: Context,
    user_id: Optional[str] = None
) -> Intent:
    """
    Convenience function to classify intent with enhanced features.

    Args:
        user_message: User's message
        context: Conversation context
        user_id: Optional user ID for history tracking and caching

    Returns:
        Intent: Classified intent with entities and confidence
    """
    return await _intent_classifier.classify(user_message, context, user_id)


def get_intent_stats(user_id: str) -> Dict[str, Any]:
    """
    Get intent classification statistics for a user.

    Args:
        user_id: User identifier

    Returns:
        Statistics dictionary
    """
    return _intent_classifier.get_intent_statistics(user_id)
