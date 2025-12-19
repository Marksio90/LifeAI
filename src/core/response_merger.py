"""
Response Merger - Merges multiple agent responses into coherent narrative
Uses LLM to synthesize responses from different specialized agents
"""
from typing import List
from loguru import logger

from openai import AsyncOpenAI
from .models import AgentResponse, Intent, UserInput
from config import settings


class ResponseMerger:
    """
    Merges multiple agent responses into a single, coherent response
    """

    def __init__(self, model: str = None):
        self.model = model or settings.default_llm_model
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def merge(
        self,
        agent_responses: List[AgentResponse],
        intent: Intent,
        user_input: UserInput
    ) -> str:
        """
        Merge multiple agent responses into coherent narrative
        """
        if not agent_responses:
            return "I apologize, but I couldn't generate a response. Please try rephrasing your question."

        if len(agent_responses) == 1:
            # Single response - return as is
            return agent_responses[0].content

        try:
            # Multiple responses - merge them
            prompt = self._build_merge_prompt(
                agent_responses,
                intent,
                user_input
            )

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
                temperature=0.7,
                max_tokens=2000
            )

            merged_content = response.choices[0].message.content
            return merged_content

        except Exception as e:
            logger.error(f"Error merging responses: {str(e)}")
            # Fallback: concatenate responses
            return self._simple_merge(agent_responses)

    def _get_system_prompt(self) -> str:
        """System prompt for response merging"""
        return """You are a response synthesis system for a life guidance AI platform.

Your task is to merge multiple specialized agent responses into a single, coherent, helpful response.

Guidelines:
1. Create a natural, conversational tone
2. Integrate insights from all agents seamlessly
3. Avoid repetition
4. Prioritize the most important information
5. Maintain consistency across different domains
6. If agents disagree, acknowledge different perspectives
7. Be empathetic and supportive
8. Keep the response focused and actionable

The user should receive ONE unified response, not multiple separate answers.
"""

    def _build_merge_prompt(
        self,
        agent_responses: List[AgentResponse],
        intent: Intent,
        user_input: UserInput
    ) -> str:
        """Build prompt for merging responses"""
        prompt = f"User question: {user_input.content}\n\n"
        prompt += f"Intent: {intent.intent_type}\n\n"
        prompt += "Agent responses to merge:\n\n"

        for i, response in enumerate(agent_responses, 1):
            prompt += f"Agent {i} ({response.agent_id}) - Confidence: {response.confidence:.2f}\n"
            prompt += f"{response.content}\n\n"

        prompt += "Create a single, coherent response that integrates all these insights:"
        return prompt

    def _simple_merge(self, agent_responses: List[AgentResponse]) -> str:
        """Simple fallback merge by concatenation"""
        parts = []
        for response in agent_responses:
            if response.content:
                parts.append(f"• {response.content}")

        return "\n\n".join(parts)
