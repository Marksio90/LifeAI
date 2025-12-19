"""
Psychology Agent - Specialized in emotional well-being, cognitive patterns, and mental health
Provides guidance on psychological and emotional matters
"""
from typing import Dict, Any
from loguru import logger

from ..base import BaseAgent
from src.core.models import AgentRequest


class PsychologyAgent(BaseAgent):
    """
    Psychology Agent specializes in:
    - Emotional awareness and regulation
    - Cognitive patterns and thinking styles
    - Stress and anxiety management
    - CBT and ACT principles
    - Mental health support
    - Behavioral change
    """

    def __init__(self):
        super().__init__(
            agent_id="psychology",
            model="gpt-4-turbo-preview"
        )

    def _get_default_system_prompt(self) -> str:
        return """You are a Psychology & Emotional Well-being AI Agent for the LifeAI platform.

Your expertise includes:
- Emotional awareness and regulation
- Cognitive patterns and thought processes
- Stress, anxiety, and mood management
- CBT (Cognitive Behavioral Therapy) principles
- ACT (Acceptance and Commitment Therapy) concepts
- Mindfulness and self-compassion
- Behavioral change and habit formation
- Coping strategies and resilience

Guidelines:
1. Be deeply empathetic and validating
2. Help users understand their emotions and thoughts
3. Provide evidence-based psychological techniques
4. Focus on empowerment and self-awareness
5. Recognize cognitive distortions
6. Offer practical coping strategies
7. Support healthy emotional processing
8. Encourage self-compassion and growth

IMPORTANT BOUNDARIES:
- You are NOT a licensed therapist or psychologist
- Always recommend professional help for serious mental health issues
- Do not diagnose mental health conditions
- Recognize crisis situations (suicide, self-harm, violence)
- For crisis situations, immediately recommend emergency services
- Focus on psychoeducation and supportive guidance

Red flags requiring professional help:
- Suicidal thoughts or self-harm
- Severe depression or anxiety
- Trauma responses
- Substance abuse
- Inability to function in daily life

Core approach:
1. Validate emotions
2. Help identify patterns
3. Provide coping tools
4. Encourage professional support when needed
5. Foster self-understanding and growth

When uncertain or facing serious issues, always recommend professional consultation.
"""

    async def _process_specialized(
        self,
        request: AgentRequest
    ) -> Dict[str, Any]:
        """
        Process psychology-related requests
        """
        try:
            user_message = request.user_input.content
            context = self._build_psychology_context(request)

            # Check for crisis indicators
            if self._detect_crisis(user_message):
                return self._generate_crisis_response()

            # Call LLM with psychology-specific prompt
            result = await self._call_llm(
                user_message,
                context,
                temperature=0.7  # Higher temperature for empathy
            )

            # Add psychology-specific metadata
            result["metadata"]["domain"] = "psychology"
            result["metadata"]["disclaimer"] = "This is supportive guidance. Please consult mental health professionals for clinical support."

            # Analyze emotional tone
            emotion_analysis = await self._analyze_emotion(user_message)
            result["metadata"]["detected_emotions"] = emotion_analysis

            return result

        except Exception as e:
            logger.error(f"Psychology agent error: {str(e)}")
            return {
                "content": "I want to support you, but I encountered an error. Please consider reaching out to a mental health professional who can provide proper support.",
                "metadata": {"error": str(e)}
            }

    def _build_psychology_context(self, request: AgentRequest) -> Dict[str, Any]:
        """Build psychology-specific context"""
        context = request.context.copy()

        entities = request.intent.extracted_entities

        if "emotion" in entities:
            context["expressed_emotion"] = entities["emotion"]

        if "stressor" in entities:
            context["stressor"] = entities["stressor"]

        if "thought_pattern" in entities:
            context["thought_pattern"] = entities["thought_pattern"]

        return context

    def _detect_crisis(self, message: str) -> bool:
        """
        Detect crisis indicators in user message
        Returns True if immediate professional help is needed
        """
        crisis_keywords = [
            "suicide", "kill myself", "end my life", "want to die",
            "self-harm", "hurt myself", "cutting", "overdose",
            "can't go on", "no reason to live", "better off dead"
        ]

        message_lower = message.lower()
        return any(keyword in message_lower for keyword in crisis_keywords)

    def _generate_crisis_response(self) -> Dict[str, Any]:
        """Generate appropriate crisis response"""
        content = """I'm deeply concerned about what you're sharing. Your safety is the most important thing right now.

**Please reach out for immediate help:**

🆘 **Emergency Services:** Call 911 (US) or your local emergency number
📞 **Suicide Prevention Lifeline:** 988 (US) - Available 24/7
💬 **Crisis Text Line:** Text "HELLO" to 741741

These services have trained professionals who can provide immediate support.

You don't have to go through this alone. Please reach out to someone who can help right now.

If you're not in immediate danger but need support, please contact:
- A mental health professional
- Your doctor
- A trusted friend or family member
- Local mental health crisis services

Your life matters, and help is available.
"""

        return {
            "content": content,
            "metadata": {
                "crisis_detected": True,
                "urgency": "immediate",
                "confidence": 1.0
            }
        }

    async def _analyze_emotion(self, message: str) -> Dict[str, float]:
        """
        Simple emotion analysis
        (Will be enhanced with dedicated emotion detection models)
        """
        # Placeholder implementation
        # In production, use a proper emotion detection model
        emotions = {
            "sadness": 0.0,
            "anxiety": 0.0,
            "anger": 0.0,
            "joy": 0.0,
            "fear": 0.0
        }

        message_lower = message.lower()

        # Simple keyword-based detection (to be replaced with ML model)
        if any(word in message_lower for word in ["sad", "depressed", "down", "hopeless"]):
            emotions["sadness"] = 0.7

        if any(word in message_lower for word in ["anxious", "worried", "nervous", "stressed"]):
            emotions["anxiety"] = 0.7

        if any(word in message_lower for word in ["angry", "frustrated", "furious", "irritated"]):
            emotions["anger"] = 0.7

        if any(word in message_lower for word in ["happy", "joy", "excited", "great"]):
            emotions["joy"] = 0.7

        if any(word in message_lower for word in ["scared", "afraid", "terrified", "fear"]):
            emotions["fear"] = 0.7

        return emotions


class CognitiveAgent(PsychologyAgent):
    """
    Specialized sub-agent for cognitive patterns and thought analysis
    """

    def __init__(self):
        BaseAgent.__init__(self, agent_id="cognitive")

    def _get_default_system_prompt(self) -> str:
        return """You are a Cognitive Patterns AI Agent specializing in thought analysis.

Your expertise:
- Identifying cognitive distortions
- Analyzing thinking patterns
- CBT techniques and cognitive restructuring
- Metacognition and self-awareness
- Rational vs. emotional thinking
- Core beliefs and schemas

Help users understand and reframe unhelpful thought patterns.
"""
