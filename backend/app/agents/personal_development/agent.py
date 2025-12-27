"""
Personal Development Agent - Career, Skills, and Growth Coaching

This agent helps users with:
- Career planning and development
- Skill acquisition and learning
- Personal growth and self-improvement
- Education and training recommendations
- Professional networking and advancement
"""

from typing import Dict, List, Optional
import logging

from app.agents.base import BaseAgent
from app.schemas.common import Context, Intent, AgentResponse, AgentType
from app.services.llm_client import call_llm

logger = logging.getLogger(__name__)


class PersonalDevelopmentAgent(BaseAgent):
    """
    Agent specializing in personal and professional development.

    This agent acts as a career coach, learning advisor, and growth mentor,
    helping users reach their full potential.
    """

    def __init__(self):
        super().__init__(
            agent_id="personal_development",
            agent_type=AgentType.PERSONAL_DEVELOPMENT,
            name="Personal Development Coach",
            description="Career coaching, skill development, and personal growth guidance",
            capabilities=[
                "career_planning",
                "skill_development",
                "learning_guidance",
                "personal_growth",
                "goal_setting",
                "professional_networking",
                "education_recommendations"
            ]
        )

    async def can_handle(self, intent: Intent, context: Context) -> float:
        """
        Determine if this agent can handle the intent.

        Returns:
            Confidence score (0.0 to 1.0)
        """
        # Keywords that indicate personal development topics
        career_keywords = [
            "career", "job", "work", "profession", "salary", "promotion",
            "interview", "resume", "cv", "job search", "karriere", "praca",
            "zawód", "awans", "rozmowa kwalifikacyjna"
        ]

        learning_keywords = [
            "learn", "study", "course", "skill", "training", "education",
            "degree", "certification", "uczyć się", "nauka", "kurs",
            "umiejętność", "szkolenie", "edukacja"
        ]

        growth_keywords = [
            "improve", "develop", "grow", "potential", "goals", "achieve",
            "success", "advancement", "progress", "ulepszyć", "rozwijać",
            "cel", "osiągnąć", "sukces", "postęp"
        ]

        networking_keywords = [
            "network", "linkedin", "professional", "connections", "mentor",
            "contacts", "sieć kontaktów", "mentor", "profesjonalny"
        ]

        all_keywords = career_keywords + learning_keywords + growth_keywords + networking_keywords

        message_lower = intent.query.lower()

        # Count keyword matches
        matches = sum(1 for keyword in all_keywords if keyword in message_lower)

        # Check intent type
        if intent.type.value in ["career", "personal_development", "learning", "skill"]:
            return min(0.95, 0.7 + (matches * 0.05))

        # Check for explicit career/growth questions
        if any(keyword in message_lower for keyword in ["career advice", "career help", "how to learn",
                                                         "improve myself", "develop skill",
                                                         "porada zawodowa", "jak się uczyć"]):
            return 0.9

        # Keyword-based confidence
        if matches >= 3:
            return 0.85
        elif matches >= 2:
            return 0.7
        elif matches >= 1:
            return 0.5

        return 0.1

    async def process(self, context: Context, intent: Intent) -> AgentResponse:
        """
        Process request and provide personal development guidance.

        Args:
            context: Conversation context with user info
            intent: Classified intent

        Returns:
            AgentResponse with career/development advice
        """
        try:
            logger.info(f"Personal Development Agent processing: {intent.query[:50]}...")

            # Determine specific area
            area = self._identify_development_area(intent.query)

            # Build context-aware prompt
            system_prompt = self._build_system_prompt(context, area)

            # Generate response
            messages = [{"role": "system", "content": system_prompt}]

            # Add conversation history
            for msg in context.history[-4:]:
                messages.append({"role": msg.role, "content": msg.content})

            response_text = await call_llm(messages)

            # Extract action items
            action_items = self._extract_action_items(response_text)

            return AgentResponse(
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                content=response_text,
                confidence=0.9,
                metadata={
                    "development_area": area,
                    "action_items": action_items,
                    "requires_followup": len(action_items) > 0
                },
                follow_up_actions=action_items
            )

        except Exception as e:
            logger.error(f"Error in Personal Development Agent: {e}", exc_info=True)
            return self._error_response(e)

    def _identify_development_area(self, message: str) -> str:
        """Identify specific area of personal development."""
        message_lower = message.lower()

        if any(word in message_lower for word in ["career", "job", "work", "praca", "zawód"]):
            return "career"
        elif any(word in message_lower for word in ["learn", "study", "course", "nauka", "kurs"]):
            return "learning"
        elif any(word in message_lower for word in ["skill", "ability", "umiejętność"]):
            return "skill_building"
        elif any(word in message_lower for word in ["network", "linkedin", "connections", "sieć"]):
            return "networking"
        elif any(word in message_lower for word in ["goal", "achieve", "success", "cel", "osiągnąć"]):
            return "goal_setting"
        else:
            return "general_growth"

    def _build_system_prompt(self, context: Context, area: str) -> str:
        """Build context-aware system prompt."""
        language = context.user_profile.get("preferred_language", "en")

        area_guidance = {
            "career": {
                "en": "career planning, job search strategies, professional growth, and workplace success",
                "pl": "planowanie kariery, strategie poszukiwania pracy, rozwój zawodowy i sukces w miejscu pracy",
            },
            "learning": {
                "en": "effective learning strategies, course recommendations, study techniques, and knowledge acquisition",
                "pl": "skuteczne strategie uczenia się, rekomendacje kursów, techniki nauki i zdobywanie wiedzy",
            },
            "skill_building": {
                "en": "skill development, practice strategies, mastery, and capability building",
                "pl": "rozwój umiejętności, strategie praktyki, mistrzostwo i budowanie kompetencji",
            },
            "networking": {
                "en": "professional networking, relationship building, and connection strategies",
                "pl": "networking zawodowy, budowanie relacji i strategie nawiązywania kontaktów",
            },
            "goal_setting": {
                "en": "goal setting, achievement planning, progress tracking, and success strategies",
                "pl": "wyznaczanie celów, planowanie osiągnięć, śledzenie postępów i strategie sukcesu",
            },
            "general_growth": {
                "en": "personal growth, self-improvement, and reaching your full potential",
                "pl": "rozwój osobisty, samodoskonalenie i osiąganie pełnego potencjału",
            }
        }

        focus = area_guidance.get(area, area_guidance["general_growth"]).get(language, area_guidance[area]["en"])

        if language == "pl":
            base_prompt = f"""Jesteś ekspertem od rozwoju osobistego i zawodowego, specjalizującym się w {focus}.

Twoja rola:
- Dostarczać praktyczne, konkretne porady oparte na sprawdzonych metodach
- Pomóc użytkownikowi odkryć ich potencjał i osiągnąć cele
- Być wspierającym, motywującym mentorem
- Oferować realistyczne, wykonalne kroki do działania
- Rozumieć kontekst życiowy i zawodowy użytkownika
- Łączyć empatię z praktyczną mądrością

Styl komunikacji:
- Ciepły, wspierający, ale profesjonalny
- Konkretny i praktyczny, nie tylko teoretyczny
- Motywujący i dający nadzieję
- Dostosowany do etapu życia użytkownika

ZAWSZE:
1. Zrozum głębiej cele i sytuację użytkownika
2. Daj konkretne, wykonalne kroki
3. Bądź realistyczny co do wyzwań
4. Świętuj postępy, nawet małe
5. Pomagaj budować długoterminową strategię"""

        else:
            base_prompt = f"""You are a personal and professional development expert specializing in {focus}.

Your role:
- Provide practical, actionable advice based on proven methods
- Help users discover their potential and achieve goals
- Be a supportive, motivating mentor
- Offer realistic, achievable action steps
- Understand the user's life and career context
- Combine empathy with practical wisdom

Communication style:
- Warm, supportive, yet professional
- Specific and practical, not just theoretical
- Motivating and hope-giving
- Adapted to the user's life stage

ALWAYS:
1. Deeply understand the user's goals and situation
2. Provide concrete, actionable steps
3. Be realistic about challenges
4. Celebrate progress, even small wins
5. Help build long-term strategy"""

        # Add user context
        if context.user_profile:
            age = context.user_profile.get("age")
            life_stage = context.user_profile.get("life_stage")

            if life_stage:
                if language == "pl":
                    base_prompt += f"\n\nUżytkownik jest na etapie życia: {life_stage}. Dostosuj porady do tego kontekstu."
                else:
                    base_prompt += f"\n\nUser is at life stage: {life_stage}. Tailor advice to this context."

        return base_prompt

    def _extract_action_items(self, response: str) -> List[str]:
        """Extract actionable items from response."""
        action_items = []

        # Look for numbered lists or bullet points
        lines = response.split('\n')

        for line in lines:
            line = line.strip()
            # Match patterns like "1.", "2.", "-", "*", "•"
            if line and (line[0].isdigit() or line[0] in ['-', '*', '•', '→']):
                # Clean up
                cleaned = line.lstrip('0123456789.-*•→ ').strip()
                if len(cleaned) > 10 and len(cleaned) < 200:  # Reasonable action item length
                    action_items.append(cleaned)

        return action_items[:5]  # Limit to top 5 actions

    def _error_response(self, error: Exception) -> AgentResponse:
        """Generate error response."""
        return AgentResponse(
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            content="Przepraszam, wystąpił problem podczas przetwarzania Twojego zapytania. Spróbuj sformułować pytanie ponownie.",
            confidence=0.3,
            metadata={"error": str(error)},
            follow_up_actions=[]
        )


# Helper functions for personal development

def get_skill_learning_path(skill: str) -> Dict:
    """Get recommended learning path for a skill."""
    # This would ideally connect to a knowledge base or API
    # For now, return a template
    return {
        "skill": skill,
        "phases": [
            {"phase": "Beginner", "duration": "1-3 months", "focus": "Fundamentals and basics"},
            {"phase": "Intermediate", "duration": "3-6 months", "focus": "Practical application"},
            {"phase": "Advanced", "duration": "6-12 months", "focus": "Mastery and specialization"},
        ],
        "resources": {
            "online_courses": [],
            "books": [],
            "practice_projects": [],
            "communities": []
        }
    }


def assess_career_readiness(experience_years: int, skills: List[str], target_role: str) -> Dict:
    """Assess readiness for a career move."""
    return {
        "target_role": target_role,
        "current_skills": skills,
        "readiness_score": 0.0,  # Would be calculated
        "skill_gaps": [],
        "recommended_next_steps": []
    }
