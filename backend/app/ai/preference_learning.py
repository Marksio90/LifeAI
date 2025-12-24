"""Preference Learning System for LifeAI.

Automatically learns user preferences from interactions and adapts responses accordingly.

Features:
- Communication style learning (formal/casual, brief/detailed)
- Topic preferences (favorite domains, recurring interests)
- Response format preferences (lists, paragraphs, examples)
- Interaction patterns (best time to interact, session length)
- Adaptive personalization based on feedback
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import Counter
import json

from app.memory.long_term_memory import (
    get_long_term_memory,
    MemoryType,
    MemoryImportance
)
from app.services.llm_client import call_llm

logger = logging.getLogger(__name__)


class PreferenceCategory:
    """Categories of learnable preferences."""
    COMMUNICATION_STYLE = "communication_style"  # formal, casual, professional
    RESPONSE_LENGTH = "response_length"  # brief, moderate, detailed
    RESPONSE_FORMAT = "response_format"  # lists, paragraphs, mixed
    TONE = "tone"  # friendly, professional, empathetic
    LANGUAGE_COMPLEXITY = "language_complexity"  # simple, moderate, advanced
    EXAMPLE_PREFERENCE = "example_preference"  # loves examples, prefers abstract
    TOPIC_INTERESTS = "topic_interests"  # recurring topics of interest
    INTERACTION_TIME = "interaction_time"  # preferred time of day


class PreferenceLearner:
    """
    Learns and adapts to user preferences over time.

    Uses conversation analysis, feedback, and behavioral patterns
    to build a preference profile for each user.
    """

    def __init__(self):
        """Initialize preference learner."""
        self.memory = get_long_term_memory()
        self._user_profiles: Dict[str, Dict[str, Any]] = {}
        logger.info("Preference learning system initialized")

    async def learn_from_conversation(
        self,
        user_id: str,
        conversation_messages: List[Dict[str, str]],
        user_feedback: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze conversation and extract preference signals.

        Args:
            user_id: User identifier
            conversation_messages: List of conversation messages
            user_feedback: Optional explicit feedback from user

        Returns:
            Dictionary of learned preferences
        """
        try:
            logger.info(f"Learning preferences from conversation for user {user_id}")

            # Analyze conversation for implicit preferences
            implicit_prefs = await self._analyze_conversation_style(
                user_id,
                conversation_messages
            )

            # Incorporate explicit feedback if provided
            if user_feedback:
                explicit_prefs = self._process_explicit_feedback(user_feedback)
                implicit_prefs.update(explicit_prefs)

            # Store learned preferences
            for category, value in implicit_prefs.items():
                await self._store_preference(
                    user_id=user_id,
                    category=category,
                    value=value,
                    confidence=implicit_prefs.get(f"{category}_confidence", 0.7)
                )

            # Update user profile cache
            self._update_user_profile(user_id, implicit_prefs)

            logger.info(
                f"Learned {len(implicit_prefs)} preferences for user {user_id}"
            )

            return implicit_prefs

        except Exception as e:
            logger.error(f"Error learning preferences: {e}")
            return {}

    async def _analyze_conversation_style(
        self,
        user_id: str,
        messages: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Use LLM to analyze conversation and extract preference signals.

        Args:
            user_id: User identifier
            messages: Conversation messages

        Returns:
            Dictionary of detected preferences
        """
        try:
            # Prepare conversation for analysis
            conversation_text = "\n".join([
                f"{msg['role']}: {msg['content']}"
                for msg in messages[-10:]  # Last 10 messages
            ])

            analysis_prompt = f"""Analyze this conversation and identify the user's communication preferences.

Conversation:
{conversation_text}

Analyze and extract:

1. COMMUNICATION STYLE:
   - formal (uses proper grammar, polite language)
   - casual (informal, relaxed tone)
   - professional (business-like, to the point)

2. RESPONSE LENGTH PREFERENCE:
   - brief (short, concise answers)
   - moderate (balanced detail)
   - detailed (comprehensive explanations)

3. RESPONSE FORMAT PREFERENCE:
   - lists (bullet points, numbered lists)
   - paragraphs (flowing text)
   - mixed (combination)

4. TONE PREFERENCE:
   - friendly (warm, personable)
   - professional (business-like)
   - empathetic (understanding, supportive)

5. EXAMPLE PREFERENCE:
   - loves_examples (frequently asks for or appreciates examples)
   - prefers_abstract (likes theoretical explanations)
   - neutral (no strong preference)

6. LANGUAGE COMPLEXITY:
   - simple (prefers plain language)
   - moderate (standard vocabulary)
   - advanced (comfortable with technical terms)

Return ONLY a JSON object with detected preferences and confidence scores (0.0-1.0):
{{
  "communication_style": "casual",
  "communication_style_confidence": 0.8,
  "response_length": "detailed",
  "response_length_confidence": 0.7,
  "response_format": "lists",
  "response_format_confidence": 0.9,
  "tone": "friendly",
  "tone_confidence": 0.85,
  "example_preference": "loves_examples",
  "example_preference_confidence": 0.6,
  "language_complexity": "moderate",
  "language_complexity_confidence": 0.75
}}

Base your analysis on:
- User's message length and structure
- Formality of language
- Questions asked
- Engagement with responses
- Explicit requests for specific formats

Return ONLY the JSON object."""

            response = await call_llm([
                {"role": "system", "content": "You are a user preference analysis expert."},
                {"role": "user", "content": analysis_prompt}
            ], temperature=0.3, response_format={"type": "json_object"})

            # Parse response
            preferences = json.loads(response)

            return preferences

        except Exception as e:
            logger.error(f"Error analyzing conversation style: {e}")
            return {}

    def _process_explicit_feedback(
        self,
        feedback: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process explicit user feedback into preferences.

        Args:
            feedback: Feedback dictionary

        Returns:
            Extracted preferences
        """
        preferences = {}

        # Map feedback to preferences
        if "too_long" in feedback:
            preferences["response_length"] = "brief"
            preferences["response_length_confidence"] = 0.9

        if "too_short" in feedback:
            preferences["response_length"] = "detailed"
            preferences["response_length_confidence"] = 0.9

        if "prefer_lists" in feedback:
            preferences["response_format"] = "lists"
            preferences["response_format_confidence"] = 1.0

        if "prefer_paragraphs" in feedback:
            preferences["response_format"] = "paragraphs"
            preferences["response_format_confidence"] = 1.0

        if "too_formal" in feedback:
            preferences["communication_style"] = "casual"
            preferences["communication_style_confidence"] = 0.95

        if "too_casual" in feedback:
            preferences["communication_style"] = "formal"
            preferences["communication_style_confidence"] = 0.95

        return preferences

    async def _store_preference(
        self,
        user_id: str,
        category: str,
        value: Any,
        confidence: float = 0.7
    ):
        """
        Store a learned preference in long-term memory.

        Args:
            user_id: User identifier
            category: Preference category
            value: Preference value
            confidence: Confidence score (0.0-1.0)
        """
        try:
            # Convert to importance score (1-5)
            importance = MemoryImportance.MEDIUM
            if confidence >= 0.9:
                importance = MemoryImportance.HIGH
            elif confidence >= 0.7:
                importance = MemoryImportance.MEDIUM
            else:
                importance = MemoryImportance.LOW

            content = f"User prefers {category}: {value}"

            await self.memory.store_memory(
                user_id=user_id,
                content=content,
                memory_type=MemoryType.PREFERENCE,
                importance=importance,
                metadata={
                    "preference_key": category,
                    "preference_value": value,
                    "confidence": confidence,
                    "learned_at": datetime.utcnow().isoformat()
                }
            )

            logger.debug(
                f"Stored preference for user {user_id}: {category}={value} "
                f"(confidence: {confidence:.2f})"
            )

        except Exception as e:
            logger.error(f"Error storing preference: {e}")

    def _update_user_profile(self, user_id: str, preferences: Dict[str, Any]):
        """
        Update cached user profile with new preferences.

        Args:
            user_id: User identifier
            preferences: Preference updates
        """
        if user_id not in self._user_profiles:
            self._user_profiles[user_id] = {}

        # Update with new preferences (with timestamp)
        for key, value in preferences.items():
            if not key.endswith("_confidence"):
                self._user_profiles[user_id][key] = {
                    "value": value,
                    "confidence": preferences.get(f"{key}_confidence", 0.7),
                    "updated_at": datetime.utcnow().isoformat()
                }

    async def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Get consolidated user preferences.

        Args:
            user_id: User identifier

        Returns:
            Dictionary of user preferences
        """
        try:
            # Check cache first
            if user_id in self._user_profiles:
                logger.debug(f"Using cached preferences for user {user_id}")
                return self._user_profiles[user_id]

            # Retrieve from memory
            prefs_dict = await self.memory.get_user_preferences(user_id)

            # Build profile
            profile = {}
            for pref_key, pref_data in prefs_dict.items():
                profile[pref_key] = pref_data

            # Cache it
            self._user_profiles[user_id] = profile

            return profile

        except Exception as e:
            logger.error(f"Error getting user preferences: {e}")
            return {}

    async def generate_personalization_instructions(
        self,
        user_id: str
    ) -> str:
        """
        Generate instructions for LLM to personalize responses.

        Args:
            user_id: User identifier

        Returns:
            String with personalization instructions
        """
        try:
            preferences = await self.get_user_preferences(user_id)

            if not preferences:
                return "No specific personalization preferences detected yet."

            instructions = ["PERSONALIZATION INSTRUCTIONS:"]

            # Communication style
            if "communication_style" in preferences:
                style = preferences["communication_style"]["value"]
                instructions.append(
                    f"- Use {style} communication style"
                )

            # Response length
            if "response_length" in preferences:
                length = preferences["response_length"]["value"]
                length_map = {
                    "brief": "Keep responses concise and to the point",
                    "moderate": "Provide balanced detail in responses",
                    "detailed": "Provide comprehensive, detailed explanations"
                }
                instructions.append(f"- {length_map.get(length, '')}")

            # Response format
            if "response_format" in preferences:
                format_pref = preferences["response_format"]["value"]
                format_map = {
                    "lists": "Format information as bullet points or lists",
                    "paragraphs": "Use flowing paragraphs",
                    "mixed": "Mix lists and paragraphs as appropriate"
                }
                instructions.append(f"- {format_map.get(format_pref, '')}")

            # Tone
            if "tone" in preferences:
                tone = preferences["tone"]["value"]
                instructions.append(f"- Maintain a {tone} tone")

            # Examples
            if "example_preference" in preferences:
                example_pref = preferences["example_preference"]["value"]
                if example_pref == "loves_examples":
                    instructions.append("- Include practical examples to illustrate points")
                elif example_pref == "prefers_abstract":
                    instructions.append("- Focus on theoretical explanations")

            # Language complexity
            if "language_complexity" in preferences:
                complexity = preferences["language_complexity"]["value"]
                complexity_map = {
                    "simple": "Use plain, simple language",
                    "moderate": "Use standard vocabulary",
                    "advanced": "Technical terms are acceptable"
                }
                instructions.append(f"- {complexity_map.get(complexity, '')}")

            result = "\n".join(instructions)
            logger.debug(f"Generated personalization instructions for user {user_id}")

            return result

        except Exception as e:
            logger.error(f"Error generating personalization instructions: {e}")
            return ""

    async def learn_from_feedback(
        self,
        user_id: str,
        message_id: str,
        rating: int,
        feedback_text: Optional[str] = None
    ):
        """
        Learn from explicit user feedback on responses.

        Args:
            user_id: User identifier
            message_id: Message that was rated
            rating: Rating (1-5)
            feedback_text: Optional feedback text
        """
        try:
            # Analyze feedback for preference signals
            if rating <= 2 and feedback_text:
                # Negative feedback - analyze what went wrong
                await self._analyze_negative_feedback(
                    user_id,
                    feedback_text,
                    message_id
                )

            elif rating >= 4:
                # Positive feedback - reinforce current preferences
                logger.info(
                    f"Positive feedback from user {user_id} - "
                    f"reinforcing current preferences"
                )

        except Exception as e:
            logger.error(f"Error learning from feedback: {e}")

    async def _analyze_negative_feedback(
        self,
        user_id: str,
        feedback_text: str,
        message_id: str
    ):
        """
        Analyze negative feedback to adjust preferences.

        Args:
            user_id: User identifier
            feedback_text: Feedback text
            message_id: Associated message ID
        """
        try:
            # Use LLM to extract actionable insights from feedback
            analysis_prompt = f"""Analyze this user feedback and identify what preferences need adjustment.

Feedback: "{feedback_text}"

Identify if the user is indicating preferences about:
- Response length (too long/too short)
- Response format (prefer lists/paragraphs)
- Communication style (too formal/too casual)
- Tone (too friendly/too professional)
- Level of detail
- Use of examples

Return JSON with detected preference adjustments:
{{
  "adjustments": [
    {{"category": "response_length", "new_value": "brief", "reason": "User said too long"}}
  ]
}}

Return ONLY the JSON object."""

            response = await call_llm([
                {"role": "system", "content": "You are a feedback analysis expert."},
                {"role": "user", "content": analysis_prompt}
            ], temperature=0.3, response_format={"type": "json_object"})

            result = json.loads(response)

            # Apply adjustments
            for adjustment in result.get("adjustments", []):
                category = adjustment["category"]
                new_value = adjustment["new_value"]

                await self._store_preference(
                    user_id=user_id,
                    category=category,
                    value=new_value,
                    confidence=0.8  # High confidence from explicit feedback
                )

                logger.info(
                    f"Adjusted preference for user {user_id}: "
                    f"{category} -> {new_value} (reason: {adjustment['reason']})"
                )

        except Exception as e:
            logger.error(f"Error analyzing negative feedback: {e}")


# Singleton instance
_preference_learner: Optional[PreferenceLearner] = None


def get_preference_learner() -> PreferenceLearner:
    """Get or create preference learner instance."""
    global _preference_learner

    if _preference_learner is None:
        _preference_learner = PreferenceLearner()

    return _preference_learner
