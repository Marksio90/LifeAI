"""
Base Agent - Abstract class for all specialized agents
Defines the interface and common functionality for agents
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from datetime import datetime
from loguru import logger

from openai import AsyncOpenAI
from src.core.models import AgentRequest, AgentResponse, ConfidenceLevel
from config import settings


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the system
    Each specialized agent must inherit from this class
    """

    def __init__(
        self,
        agent_id: str,
        model: str = None,
        system_prompt: Optional[str] = None
    ):
        self.agent_id = agent_id
        self.model = model or settings.default_llm_model
        self.system_prompt = system_prompt or self._get_default_system_prompt()
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

        logger.info(f"Initialized agent: {agent_id}")

    @abstractmethod
    def _get_default_system_prompt(self) -> str:
        """
        Each agent must define its own system prompt
        This defines the agent's personality and expertise
        """
        pass

    @abstractmethod
    async def _process_specialized(
        self,
        request: AgentRequest
    ) -> Dict[str, Any]:
        """
        Agent-specific processing logic
        Returns dict with 'content' and optional 'metadata'
        """
        pass

    async def process(self, request: AgentRequest) -> AgentResponse:
        """
        Main processing method - calls specialized processing
        and wraps it in standard response format
        """
        start_time = datetime.utcnow()

        try:
            # Call agent-specific processing
            result = await self._process_specialized(request)

            # Calculate confidence
            confidence = self._calculate_confidence(result, request)

            # Build response
            response = AgentResponse(
                agent_id=self.agent_id,
                content=result.get("content", ""),
                confidence=confidence,
                confidence_level=self._get_confidence_level(confidence),
                metadata=result.get("metadata", {}),
                processing_time=(datetime.utcnow() - start_time).total_seconds(),
                tokens_used=result.get("tokens_used")
            )

            return response

        except Exception as e:
            logger.error(f"Error in agent {self.agent_id}: {str(e)}")
            # Return error response
            return AgentResponse(
                agent_id=self.agent_id,
                content=f"Agent encountered an error: {str(e)}",
                confidence=0.0,
                confidence_level=ConfidenceLevel.UNCERTAIN,
                metadata={"error": str(e)},
                processing_time=(datetime.utcnow() - start_time).total_seconds()
            )

    async def _call_llm(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Helper method to call LLM with agent's system prompt
        """
        messages = [
            {
                "role": "system",
                "content": self.system_prompt
            }
        ]

        # Add context if provided
        if context:
            context_str = self._format_context(context)
            messages.append({
                "role": "system",
                "content": f"Context:\n{context_str}"
            })

        # Add user message
        messages.append({
            "role": "user",
            "content": user_message
        })

        # Call LLM
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=1500
        )

        return {
            "content": response.choices[0].message.content,
            "tokens_used": response.usage.total_tokens,
            "metadata": {
                "model": self.model,
                "finish_reason": response.choices[0].finish_reason
            }
        }

    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context dictionary into readable string"""
        lines = []
        for key, value in context.items():
            lines.append(f"{key}: {value}")
        return "\n".join(lines)

    def _calculate_confidence(
        self,
        result: Dict[str, Any],
        request: AgentRequest
    ) -> float:
        """
        Calculate confidence score for the response
        Can be overridden by specialized agents
        """
        # Base confidence from intent match
        base_confidence = request.intent.confidence

        # Adjust based on result metadata
        if "confidence" in result.get("metadata", {}):
            return result["metadata"]["confidence"]

        # Default confidence based on content length and quality
        content = result.get("content", "")
        if not content or len(content) < 10:
            return 0.3

        if "I don't know" in content or "uncertain" in content.lower():
            return 0.4

        return min(base_confidence * 1.1, 1.0)

    def _get_confidence_level(self, confidence: float) -> ConfidenceLevel:
        """Convert confidence score to level"""
        if confidence >= 0.8:
            return ConfidenceLevel.HIGH
        elif confidence >= 0.5:
            return ConfidenceLevel.MEDIUM
        elif confidence >= 0.3:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.UNCERTAIN

    def get_info(self) -> Dict[str, Any]:
        """Get agent information"""
        return {
            "agent_id": self.agent_id,
            "model": self.model,
            "system_prompt_length": len(self.system_prompt)
        }
