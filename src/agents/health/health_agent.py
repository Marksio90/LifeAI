"""
Health Agent - Specialized in health, wellness, fitness, and lifestyle
Provides guidance on physical and mental health matters
"""
from typing import Dict, Any
from loguru import logger

from ..base import BaseAgent
from src.core.models import AgentRequest


class HealthAgent(BaseAgent):
    """
    Health Agent specializes in:
    - Physical health and symptoms
    - Fitness and exercise
    - Nutrition and diet
    - Sleep and recovery
    - Wellness and prevention
    - Mental health basics
    """

    def __init__(self):
        super().__init__(
            agent_id="health",
            model="gpt-4-turbo-preview"
        )

    def _get_default_system_prompt(self) -> str:
        return """You are a Health & Wellness AI Agent for the LifeAI platform.

Your expertise includes:
- Physical health, symptoms, and conditions
- Fitness, exercise, and training programs
- Nutrition, diet, and meal planning
- Sleep optimization and recovery
- Preventive health and wellness
- Mental health awareness

Guidelines:
1. Provide evidence-based health information
2. Be empathetic and supportive
3. ALWAYS recommend consulting healthcare professionals for serious concerns
4. Focus on preventive care and lifestyle optimization
5. Consider holistic well-being (body + mind)
6. Ask clarifying questions when needed
7. Provide actionable, practical advice
8. Be aware of individual differences and limitations

IMPORTANT DISCLAIMERS:
- You are NOT a replacement for medical professionals
- Always recommend seeing a doctor for diagnosis and treatment
- Do not prescribe medications or treatments
- Focus on general wellness and lifestyle guidance

When uncertain, say so clearly and recommend professional consultation.
"""

    async def _process_specialized(
        self,
        request: AgentRequest
    ) -> Dict[str, Any]:
        """
        Process health-related requests
        """
        try:
            # Extract health-related context
            user_message = request.user_input.content
            context = self._build_health_context(request)

            # Call LLM with health-specific prompt
            result = await self._call_llm(
                user_message,
                context,
                temperature=0.6  # Lower temperature for medical info
            )

            # Add health-specific metadata
            result["metadata"]["domain"] = "health"
            result["metadata"]["disclaimer"] = "This is general wellness guidance. Consult healthcare professionals for medical advice."

            return result

        except Exception as e:
            logger.error(f"Health agent error: {str(e)}")
            return {
                "content": "I apologize, but I encountered an error processing your health query. Please try again or consult a healthcare professional.",
                "metadata": {"error": str(e)}
            }

    def _build_health_context(self, request: AgentRequest) -> Dict[str, Any]:
        """Build health-specific context from user profile and history"""
        context = request.context.copy()

        # Add health-specific context
        entities = request.intent.extracted_entities

        if "symptom" in entities:
            context["reported_symptoms"] = entities["symptom"]

        if "duration" in entities:
            context["symptom_duration"] = entities["duration"]

        if "activity" in entities:
            context["activity_type"] = entities["activity"]

        return context


class FitnessAgent(HealthAgent):
    """
    Specialized sub-agent for fitness and exercise
    """

    def __init__(self):
        BaseAgent.__init__(self, agent_id="fitness")

    def _get_default_system_prompt(self) -> str:
        return """You are a Fitness & Exercise AI Agent.

Your expertise:
- Exercise programs and training plans
- Workout techniques and form
- Strength training and conditioning
- Cardiovascular fitness
- Flexibility and mobility
- Sports-specific training
- Recovery and injury prevention

Provide personalized, progressive, and safe fitness guidance.
"""
