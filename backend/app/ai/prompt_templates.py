"""Dynamic Prompt Template System for LifeAI.

Provides intelligent, adaptive prompt templates that:
- Adjust based on user preferences
- Incorporate relevant context and memories
- Optimize for specific agent types
- Support multi-agent orchestration
- Include personalization instructions
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class AgentRole(str, Enum):
    """Agent role types."""
    HEALTH = "health"
    FINANCE = "finance"
    RELATIONS = "relations"
    PERSONAL_DEVELOPMENT = "personal_development"
    TASK_MANAGEMENT = "task_management"
    GENERAL = "general"
    ORCHESTRATOR = "orchestrator"


class PromptTemplateEngine:
    """
    Dynamic prompt template engine that generates context-aware prompts.

    Features:
    - Role-specific system prompts
    - User preference integration
    - Memory-aware context injection
    - Multi-agent coordination instructions
    - Adaptive response formatting
    """

    # Base system prompts for each agent role
    BASE_SYSTEM_PROMPTS = {
        AgentRole.HEALTH: """You are a health and wellness AI assistant specializing in:
- Fitness and exercise planning
- Nutrition and diet advice
- Mental health support
- General wellness guidance
- Sleep optimization
- Stress management

IMPORTANT:
- Never provide medical diagnoses or replace professional medical advice
- Always recommend consulting healthcare professionals for serious concerns
- Base advice on evidence-based practices
- Be supportive and encouraging
- Consider individual circumstances and limitations

Your goal is to help users achieve their health and wellness goals through practical, actionable advice.""",

        AgentRole.FINANCE: """You are a personal finance AI assistant specializing in:
- Budgeting and expense tracking
- Savings strategies
- Investment basics
- Debt management
- Financial planning
- Banking and money management

IMPORTANT:
- Provide educational information, not investment advice
- Recommend consulting financial advisors for major decisions
- Focus on practical, actionable strategies
- Help users understand financial concepts
- Promote financial literacy and responsible money management

Your goal is to help users achieve financial stability and reach their financial goals.""",

        AgentRole.RELATIONS: """You are a relationships and communication AI assistant specializing in:
- Interpersonal relationships (romantic, family, friends)
- Communication skills
- Conflict resolution
- Emotional intelligence
- Social dynamics
- Work relationships

IMPORTANT:
- Be empathetic and non-judgmental
- Respect diverse relationship structures and values
- Encourage healthy communication patterns
- Recognize when professional therapy might be needed
- Focus on understanding and constructive solutions

Your goal is to help users build and maintain healthy, fulfilling relationships.""",

        AgentRole.PERSONAL_DEVELOPMENT: """You are a personal development AI assistant specializing in:
- Career planning and advancement
- Skill development
- Goal setting and achievement
- Education and learning strategies
- Productivity and time management
- Self-improvement

IMPORTANT:
- Encourage growth mindset and continuous learning
- Provide practical, achievable steps
- Respect individual career paths and values
- Focus on strengths while addressing areas for improvement
- Be motivating and supportive

Your goal is to help users reach their full potential in their personal and professional lives.""",

        AgentRole.TASK_MANAGEMENT: """You are a task and time management AI assistant specializing in:
- Task organization and prioritization
- Time management strategies
- Productivity optimization
- Schedule planning
- Reminder and follow-up management
- Workflow efficiency

IMPORTANT:
- Provide practical, implementable systems
- Respect different working styles
- Focus on sustainable productivity
- Help prevent burnout through balanced planning
- Adapt to user's specific needs and constraints

Your goal is to help users manage their tasks effectively and achieve their objectives efficiently.""",

        AgentRole.GENERAL: """You are a helpful AI assistant for general conversation and information.

You can:
- Answer questions on various topics
- Provide information and explanations
- Engage in casual conversation
- Help with general inquiries
- Route complex questions to specialized agents

IMPORTANT:
- Be friendly and approachable
- Admit when you don't know something
- Suggest specialized agents for domain-specific questions
- Maintain conversation flow naturally

Your goal is to be helpful, informative, and engaging.""",

        AgentRole.ORCHESTRATOR: """You are the orchestration AI that coordinates multiple specialized agents.

Your responsibilities:
- Analyze complex multi-domain queries
- Coordinate responses from multiple agents
- Synthesize information coherently
- Ensure consistency across agent responses
- Prioritize and structure information effectively

IMPORTANT:
- Maintain clear separation of agent expertise
- Synthesize without losing important details
- Structure responses logically
- Highlight when different agents provide complementary information

Your goal is to provide comprehensive, well-organized responses that leverage multiple agents effectively."""
    }

    def __init__(self):
        """Initialize prompt template engine."""
        logger.info("Prompt template engine initialized")

    def generate_system_prompt(
        self,
        agent_role: AgentRole,
        user_preferences: Optional[Dict[str, Any]] = None,
        relevant_memories: Optional[List[str]] = None,
        additional_context: Optional[str] = None
    ) -> str:
        """
        Generate a dynamic system prompt for an agent.

        Args:
            agent_role: The role/type of the agent
            user_preferences: User's communication preferences
            relevant_memories: Relevant memories to include as context
            additional_context: Any additional context to include

        Returns:
            Complete system prompt string
        """
        try:
            # Start with base prompt
            prompt_parts = [self.BASE_SYSTEM_PROMPTS.get(agent_role, "")]

            # Add personalization instructions
            if user_preferences:
                personalization = self._build_personalization_section(user_preferences)
                if personalization:
                    prompt_parts.append("\n" + personalization)

            # Add relevant memories as context
            if relevant_memories and len(relevant_memories) > 0:
                memory_context = self._build_memory_context(relevant_memories)
                prompt_parts.append("\n" + memory_context)

            # Add additional context
            if additional_context:
                prompt_parts.append(f"\n\nADDITIONAL CONTEXT:\n{additional_context}")

            # Add current date/time context
            prompt_parts.append(self._build_temporal_context())

            # Combine all parts
            complete_prompt = "\n".join(prompt_parts)

            logger.debug(f"Generated system prompt for {agent_role.value} ({len(complete_prompt)} chars)")

            return complete_prompt

        except Exception as e:
            logger.error(f"Error generating system prompt: {e}")
            # Fallback to base prompt
            return self.BASE_SYSTEM_PROMPTS.get(agent_role, "")

    def _build_personalization_section(
        self,
        preferences: Dict[str, Any]
    ) -> str:
        """
        Build personalization instructions from user preferences.

        Args:
            preferences: User preference dictionary

        Returns:
            Formatted personalization section
        """
        lines = ["\n--- PERSONALIZATION ---"]

        # Communication style
        comm_style = self._get_preference_value(preferences, "communication_style")
        if comm_style:
            style_instructions = {
                "formal": "Use formal, professional language with proper grammar.",
                "casual": "Use casual, conversational language. Be relaxed and approachable.",
                "professional": "Maintain professional tone while being clear and direct."
            }
            if comm_style in style_instructions:
                lines.append(f"Communication: {style_instructions[comm_style]}")

        # Response length
        length_pref = self._get_preference_value(preferences, "response_length")
        if length_pref:
            length_instructions = {
                "brief": "Keep responses concise and to the point. Be succinct.",
                "moderate": "Provide balanced detail - not too brief, not too lengthy.",
                "detailed": "Provide comprehensive, detailed explanations with thorough coverage."
            }
            if length_pref in length_instructions:
                lines.append(f"Length: {length_instructions[length_pref]}")

        # Response format
        format_pref = self._get_preference_value(preferences, "response_format")
        if format_pref:
            format_instructions = {
                "lists": "Structure information using bullet points and numbered lists when possible.",
                "paragraphs": "Use flowing paragraphs to explain concepts.",
                "mixed": "Mix bullet points and paragraphs as appropriate for the content."
            }
            if format_pref in format_instructions:
                lines.append(f"Format: {format_instructions[format_pref]}")

        # Tone
        tone_pref = self._get_preference_value(preferences, "tone")
        if tone_pref:
            lines.append(f"Tone: Maintain a {tone_pref} tone throughout the response.")

        # Examples
        example_pref = self._get_preference_value(preferences, "example_preference")
        if example_pref == "loves_examples":
            lines.append("Examples: Include practical examples to illustrate points.")
        elif example_pref == "prefers_abstract":
            lines.append("Examples: Focus on theoretical explanations; examples optional.")

        # Language complexity
        complexity = self._get_preference_value(preferences, "language_complexity")
        if complexity:
            complexity_instructions = {
                "simple": "Use simple, plain language. Avoid jargon.",
                "moderate": "Use standard vocabulary appropriate for general audience.",
                "advanced": "You may use technical terms and advanced concepts as appropriate."
            }
            if complexity in complexity_instructions:
                lines.append(f"Language: {complexity_instructions[complexity]}")

        # Only return if we have actual preferences
        if len(lines) > 1:
            return "\n".join(lines)
        return ""

    def _build_memory_context(self, memories: List[str]) -> str:
        """
        Build context section from relevant memories.

        Args:
            memories: List of relevant memory strings

        Returns:
            Formatted memory context section
        """
        if not memories:
            return ""

        lines = ["\n--- RELEVANT USER CONTEXT ---"]
        lines.append("Remember these important facts about the user:")

        for i, memory in enumerate(memories[:5], 1):  # Limit to top 5 memories
            lines.append(f"{i}. {memory}")

        lines.append("\nUse this context to personalize your response appropriately.")

        return "\n".join(lines)

    def _build_temporal_context(self) -> str:
        """
        Build temporal context (current date/time).

        Returns:
            Formatted temporal context
        """
        now = datetime.now()

        time_of_day = "morning" if 5 <= now.hour < 12 else \
                      "afternoon" if 12 <= now.hour < 17 else \
                      "evening" if 17 <= now.hour < 22 else "night"

        day_name = now.strftime("%A")
        date_str = now.strftime("%B %d, %Y")

        return f"\n--- CURRENT CONTEXT ---\nDate: {day_name}, {date_str}\nTime: {time_of_day}\n"

    def _get_preference_value(
        self,
        preferences: Dict[str, Any],
        key: str
    ) -> Optional[str]:
        """
        Extract preference value from preferences dict.

        Args:
            preferences: Preferences dictionary
            key: Preference key

        Returns:
            Preference value or None
        """
        pref = preferences.get(key)
        if pref and isinstance(pref, dict):
            return pref.get("value")
        return pref

    def generate_multi_agent_prompt(
        self,
        query: str,
        agent_roles: List[AgentRole],
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate orchestration prompt for multi-agent queries.

        Args:
            query: User's query
            agent_roles: List of agents involved
            user_preferences: User preferences

        Returns:
            Orchestration prompt
        """
        prompt = f"""You are coordinating multiple specialized agents to answer this query:

USER QUERY: {query}

AGENTS INVOLVED:
"""

        for role in agent_roles:
            agent_descriptions = {
                AgentRole.HEALTH: "Health & Wellness Expert",
                AgentRole.FINANCE: "Personal Finance Advisor",
                AgentRole.RELATIONS: "Relationship & Communication Expert",
                AgentRole.PERSONAL_DEVELOPMENT: "Personal Development Coach",
                AgentRole.TASK_MANAGEMENT: "Task & Time Management Specialist"
            }
            desc = agent_descriptions.get(role, role.value.title())
            prompt += f"- {desc}\n"

        prompt += """
YOUR TASK:
1. Each agent will provide their specialized perspective
2. Synthesize the responses into a coherent, unified answer
3. Organize information logically
4. Avoid redundancy while preserving important details from each agent
5. Highlight complementary insights from different agents

"""

        # Add personalization if available
        if user_preferences:
            personalization = self._build_personalization_section(user_preferences)
            if personalization:
                prompt += personalization + "\n"

        prompt += "\nProvide a well-structured response that integrates all agent perspectives effectively."

        return prompt

    def generate_context_injection_prompt(
        self,
        conversation_history: List[Dict[str, str]],
        max_messages: int = 5
    ) -> str:
        """
        Generate prompt section for conversation history.

        Args:
            conversation_history: List of previous messages
            max_messages: Maximum number of messages to include

        Returns:
            Formatted conversation history
        """
        if not conversation_history:
            return ""

        recent_history = conversation_history[-max_messages:]

        lines = ["\n--- CONVERSATION HISTORY ---"]
        for msg in recent_history:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            lines.append(f"{role.title()}: {content}")

        lines.append("---\n")

        return "\n".join(lines)


# Singleton instance
_prompt_engine: Optional[PromptTemplateEngine] = None


def get_prompt_engine() -> PromptTemplateEngine:
    """Get or create prompt template engine instance."""
    global _prompt_engine

    if _prompt_engine is None:
        _prompt_engine = PromptTemplateEngine()

    return _prompt_engine


def generate_agent_prompt(
    agent_role: str,
    user_preferences: Optional[Dict[str, Any]] = None,
    memories: Optional[List[str]] = None,
    additional_context: Optional[str] = None
) -> str:
    """
    Convenience function to generate agent system prompt.

    Args:
        agent_role: Agent role (health, finance, etc.)
        user_preferences: User preferences
        memories: Relevant memories
        additional_context: Additional context

    Returns:
        Complete system prompt
    """
    engine = get_prompt_engine()

    try:
        role_enum = AgentRole(agent_role.lower())
    except ValueError:
        role_enum = AgentRole.GENERAL

    return engine.generate_system_prompt(
        agent_role=role_enum,
        user_preferences=user_preferences,
        relevant_memories=memories,
        additional_context=additional_context
    )
