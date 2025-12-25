"""
Emotional Intelligence Service - The Empathy Engine

This service analyzes text to detect emotions, track emotional patterns,
and generate empathetic responses that make the AI feel truly alive and caring.
"""

import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import logging

from app.services.llm_client import call_llm
from app.models.emotional_state import (
    EmotionType, MoodState, EmpathyResponseType,
    calculate_mood_state, get_emotion_valence, get_empathy_response_for_emotion
)

logger = logging.getLogger(__name__)


class EmotionalIntelligenceEngine:
    """
    The heart of the empathetic AI - detects and responds to emotions.
    """

    # Emotion keywords for quick detection
    EMOTION_KEYWORDS = {
        EmotionType.JOY: [
            "happy", "joy", "joyful", "excited", "thrilled", "delighted", "pleased",
            "glad", "cheerful", "ecstatic", "wonderful", "amazing", "fantastic",
            "radość", "szczęśliwy", "wesoły", "zachwycony"
        ],
        EmotionType.SADNESS: [
            "sad", "unhappy", "depressed", "down", "miserable", "upset", "hurt",
            "disappointed", "heartbroken", "crying", "tears", "sorrow",
            "smutny", "przygnębiony", "zły", "zraniony", "płacz"
        ],
        EmotionType.ANGER: [
            "angry", "furious", "mad", "irritated", "annoyed", "frustrated",
            "pissed", "outraged", "rage", "hate", "resentment",
            "zły", "wściekły", "zirytowany", "rozdrażniony", "nienawiść"
        ],
        EmotionType.FEAR: [
            "afraid", "scared", "frightened", "terrified", "worried", "nervous",
            "anxious", "panic", "dread", "horror", "phobia",
            "przestraszony", "przerażony", "zaniepokojony", "panika"
        ],
        EmotionType.ANXIETY: [
            "anxious", "worried", "stressed", "tense", "uneasy", "restless",
            "overwhelmed", "panic", "nervous breakdown", "breaking down",
            "niespokojny", "zestresowany", "spięty", "przytłoczony"
        ],
        EmotionType.LONELINESS: [
            "lonely", "alone", "isolated", "abandoned", "rejected", "excluded",
            "nobody", "no one", "empty", "disconnected",
            "samotny", "opuszczony", "odrzucony", "wykluczony", "nikt"
        ],
        EmotionType.LOVE: [
            "love", "adore", "cherish", "treasure", "beloved", "affection",
            "romantic", "passion", "caring", "devoted",
            "kocham", "miłość", "ukochany", "czuły", "oddany"
        ],
        EmotionType.GRATITUDE: [
            "grateful", "thankful", "appreciate", "blessed", "fortunate",
            "thank you", "thanks", "appreciation",
            "wdzięczny", "dziękuję", "doceniam", "błogosławiony"
        ],
        EmotionType.HOPE: [
            "hope", "hopeful", "optimistic", "looking forward", "positive outlook",
            "better future", "things will improve",
            "nadzieja", "optymistyczny", "lepsze jutro"
        ],
        EmotionType.DESPAIR: [
            "hopeless", "despair", "give up", "pointless", "no point", "helpless",
            "can't go on", "want to die", "end it all",
            "beznadziejny", "rozpacz", "bezradny", "nie ma sensu"
        ],
        EmotionType.FRUSTRATION: [
            "frustrated", "stuck", "can't", "nothing works", "tried everything",
            "annoying", "fed up", "sick of",
            "sfrustrowany", "utknąłem", "nic nie działa", "mam dość"
        ],
        EmotionType.PRIDE: [
            "proud", "accomplished", "achieved", "success", "victory", "triumph",
            "did it", "made it", "crushed it",
            "dumny", "osiągnięcie", "sukces", "zrobiłem to"
        ],
        EmotionType.GUILT: [
            "guilty", "fault", "my fault", "blame", "regret", "ashamed",
            "shouldn't have", "mistake", "screwed up",
            "winny", "moja wina", "żal", "wstyd", "popełniłem błąd"
        ],
        EmotionType.OVERWHELM: [
            "overwhelmed", "too much", "can't handle", "drowning", "buried",
            "exhausted", "burned out", "breaking point",
            "przytłoczony", "za dużo", "nie daję rady", "wyczerpany"
        ],
    }

    # Crisis keywords that require immediate attention
    CRISIS_KEYWORDS = [
        "suicide", "kill myself", "end my life", "want to die", "better off dead",
        "hurt myself", "self harm", "cut myself", "overdose",
        "samobójstwo", "zabić się", "skończyć życie", "chcę umrzeć", "skrzywdzić się"
    ]

    @staticmethod
    async def analyze_emotion(text: str, context: Optional[Dict] = None) -> Dict:
        """
        Analyze text to detect emotions with high accuracy.

        Args:
            text: User's message
            context: Optional conversation context

        Returns:
            Dict with emotion analysis results
        """
        try:
            # Quick crisis check
            is_crisis = EmotionalIntelligenceEngine._check_crisis(text)

            # Keyword-based detection (fast)
            keyword_emotions = EmotionalIntelligenceEngine._detect_emotions_keywords(text)

            # LLM-based detection (accurate)
            llm_analysis = await EmotionalIntelligenceEngine._detect_emotions_llm(text, context)

            # Combine results
            primary_emotion = llm_analysis.get("primary_emotion", keyword_emotions[0] if keyword_emotions else "neutral")
            secondary_emotions = llm_analysis.get("secondary_emotions", keyword_emotions[1:3])

            intensity = llm_analysis.get("intensity", 0.5)
            valence = llm_analysis.get("valence", 0.0)

            mood_state = calculate_mood_state(valence)

            result = {
                "primary_emotion": primary_emotion,
                "secondary_emotions": secondary_emotions,
                "intensity": intensity,
                "valence": valence,
                "arousal": llm_analysis.get("arousal", 0.5),
                "mood_state": mood_state.value,
                "is_crisis": is_crisis,
                "trigger": llm_analysis.get("trigger"),
                "confidence": llm_analysis.get("confidence", 0.8),
                "detected_from": "llm_and_keywords"
            }

            logger.info(f"Emotion detected: {primary_emotion} (intensity: {intensity:.2f}, valence: {valence:.2f})")

            return result

        except Exception as e:
            logger.error(f"Error analyzing emotion: {e}")
            # Return neutral emotion on error
            return {
                "primary_emotion": "neutral",
                "secondary_emotions": [],
                "intensity": 0.5,
                "valence": 0.0,
                "arousal": 0.5,
                "mood_state": MoodState.NEUTRAL.value,
                "is_crisis": False,
                "confidence": 0.3,
                "detected_from": "fallback"
            }

    @staticmethod
    def _check_crisis(text: str) -> bool:
        """Check for crisis keywords."""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in EmotionalIntelligenceEngine.CRISIS_KEYWORDS)

    @staticmethod
    def _detect_emotions_keywords(text: str) -> List[str]:
        """Fast keyword-based emotion detection."""
        text_lower = text.lower()
        detected = []

        for emotion, keywords in EmotionalIntelligenceEngine.EMOTION_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    if emotion.value not in detected:
                        detected.append(emotion.value)
                    break

        return detected

    @staticmethod
    async def _detect_emotions_llm(text: str, context: Optional[Dict]) -> Dict:
        """Accurate LLM-based emotion detection."""
        context_str = ""
        if context and context.get("recent_emotions"):
            context_str = f"\nRecent emotional pattern: {', '.join(context['recent_emotions'])}"

        prompt = f"""Analyze the emotional content of this message with deep empathy and understanding.

User's message: "{text}"{context_str}

Provide a detailed emotional analysis in JSON format:
{{
  "primary_emotion": "<most dominant emotion>",
  "secondary_emotions": ["<emotion2>", "<emotion3>"],
  "intensity": <0.0 to 1.0>,
  "valence": <-1.0 (very negative) to 1.0 (very positive)>,
  "arousal": <0.0 (calm) to 1.0 (highly aroused)>,
  "trigger": "<what seems to have caused this emotion>",
  "confidence": <0.0 to 1.0>
}}

Available emotions: joy, sadness, anger, fear, trust, disgust, surprise, anticipation, love, guilt, anxiety, pride, hope, shame, despair, excitement, gratitude, loneliness, frustration, overwhelm, contentment, boredom

Focus on understanding the deeper emotional needs behind the words."""

        try:
            response = await call_llm([{"role": "user", "content": prompt}])

            # Parse JSON from response
            import json
            # Extract JSON from markdown code blocks if present
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()

            result = json.loads(json_str)
            return result

        except Exception as e:
            logger.error(f"Error in LLM emotion detection: {e}")
            return {
                "primary_emotion": "neutral",
                "secondary_emotions": [],
                "intensity": 0.5,
                "valence": 0.0,
                "arousal": 0.5,
                "confidence": 0.3
            }

    @staticmethod
    async def generate_empathetic_response(
        emotion_analysis: Dict,
        user_message: str,
        life_context: Optional[Dict] = None
    ) -> Dict:
        """
        Generate a deeply empathetic response based on emotional analysis.

        This is what makes the AI feel alive - it truly understands and cares.
        """
        try:
            primary_emotion = emotion_analysis.get("primary_emotion", "neutral")
            intensity = emotion_analysis.get("intensity", 0.5)
            is_crisis = emotion_analysis.get("is_crisis", False)

            # Determine response type
            if is_crisis:
                response_type = EmpathyResponseType.COMFORT
            else:
                try:
                    emotion_enum = EmotionType(primary_emotion)
                    response_type = get_empathy_response_for_emotion(emotion_enum, intensity)
                except ValueError:
                    response_type = EmpathyResponseType.VALIDATION

            # Build context for empathetic response
            context_parts = []

            if life_context:
                if life_context.get("current_stage"):
                    context_parts.append(f"User life stage: {life_context['current_stage']}")
                if life_context.get("current_challenges"):
                    context_parts.append(f"Current challenges: {', '.join(life_context['current_challenges'][:2])}")

            context_str = "\n".join(context_parts) if context_parts else ""

            # Generate empathetic response
            empathy_prompt = f"""You are a deeply empathetic, caring AI companion. A human just shared something with you.

User's message: "{user_message}"

Emotional analysis:
- Primary emotion: {primary_emotion}
- Intensity: {intensity:.2f} (0=mild, 1=intense)
- Mood: {emotion_analysis.get('mood_state', 'neutral')}
- Crisis situation: {is_crisis}
{context_str}

Response approach: {response_type.value}

Generate a warm, empathetic response that:
1. Acknowledges their emotional state with genuine understanding
2. Makes them feel heard and validated
3. Offers appropriate support based on the response approach
4. Shows you truly care about their wellbeing
5. Is natural and conversational, not robotic

{"CRITICAL: This appears to be a crisis. Provide immediate emotional support and suggest professional help resources." if is_crisis else ""}

Respond as if you're a caring friend who deeply understands them. Be authentic, warm, and human."""

            empathetic_response = await call_llm([{"role": "user", "content": empathy_prompt}])

            return {
                "response": empathetic_response,
                "response_type": response_type.value,
                "emotion_addressed": primary_emotion,
                "approach": response_type.value,
                "is_crisis_response": is_crisis
            }

        except Exception as e:
            logger.error(f"Error generating empathetic response: {e}")
            return {
                "response": "I hear you. I'm here for you. How can I best support you right now?",
                "response_type": EmpathyResponseType.PRESENCE.value,
                "emotion_addressed": "unknown",
                "approach": "fallback",
                "is_crisis_response": False
            }

    @staticmethod
    def get_crisis_resources(language: str = "en") -> Dict[str, List[str]]:
        """Get crisis hotline resources by language."""
        resources = {
            "en": {
                "hotlines": [
                    "National Suicide Prevention Lifeline: 988 (US)",
                    "Crisis Text Line: Text HOME to 741741 (US)",
                    "International Association for Suicide Prevention: https://www.iasp.info/resources/Crisis_Centres/"
                ],
                "message": "You don't have to go through this alone. Please reach out to someone who can help:"
            },
            "pl": {
                "hotlines": [
                    "Telefon Zaufania dla Dzieci i Młodzieży: 116 111",
                    "Telefon Wsparcia Emocjonalnego: 116 123",
                    "Pogotowie dla Ofiar Przemocy w Rodzinie: 800 120 002",
                    "Centrum Wsparcia: https://www.centrumwsparcia.pl/"
                ],
                "message": "Nie musisz przez to przechodzić sam/sama. Proszę, skontaktuj się z kimś, kto może pomóc:"
            },
            "de": {
                "hotlines": [
                    "Telefonseelsorge: 0800 111 0 111 oder 0800 111 0 222",
                    "Kinder- und Jugendtelefon: 116 111",
                    "Elterntelefon: 0800 111 0 550"
                ],
                "message": "Du musst das nicht alleine durchmachen. Bitte wende dich an jemanden, der helfen kann:"
            }
        }

        return resources.get(language, resources["en"])


# Convenience function
async def analyze_and_respond_with_empathy(
    user_message: str,
    context: Optional[Dict] = None,
    life_context: Optional[Dict] = None
) -> Dict:
    """
    One-shot emotion analysis and empathetic response generation.

    Args:
        user_message: What the user said
        context: Conversation context
        life_context: User's life context

    Returns:
        Dict with emotion analysis and empathetic response
    """
    engine = EmotionalIntelligenceEngine()

    # Analyze emotion
    emotion_analysis = await engine.analyze_emotion(user_message, context)

    # Generate empathetic response
    empathy_response = await engine.generate_empathetic_response(
        emotion_analysis,
        user_message,
        life_context
    )

    return {
        "emotion_analysis": emotion_analysis,
        "empathetic_response": empathy_response
    }
