from typing import List, Optional
from app.schemas.common import (
    Context,
    Intent,
    AgentResponse,
    OrchestratorResponse,
    Message,
    ModalityType
)
from app.core.agent_registry import AgentRegistry
from app.core.intent_classifier import classify_intent
from app.agents.base import BaseAgent
import logging

logger = logging.getLogger(__name__)


class AgentRouter:
    """
    Main agent routing and orchestration system.

    This is the core component that:
    1. Receives user messages
    2. Classifies intent using LLM
    3. Selects appropriate agent(s)
    4. Coordinates multi-agent collaboration
    5. Aggregates and returns responses
    """

    def __init__(self):
        """Initialize the router with agent registry."""
        self.registry = AgentRegistry()

    async def route(
        self,
        user_message: str,
        context: Context
    ) -> OrchestratorResponse:
        """
        Route a user message to appropriate agent(s) and return response.

        Args:
            user_message: User's message
            context: Conversation context

        Returns:
            OrchestratorResponse: Aggregated response from agent(s)
        """
        try:
            # Step 1: Classify intent
            logger.info(f"Routing message: {user_message[:50]}...")
            intent = await classify_intent(user_message, context)

            # Step 2: Find capable agents
            capable_agents = await self.registry.find_capable_agents(
                intent, context, min_confidence=0.3
            )

            if not capable_agents:
                logger.warning("No capable agents found, using fallback")
                return self._fallback_response()

            # Step 3: Decide on single vs multi-agent
            if intent.requires_multi_agent and len(capable_agents) > 1:
                # Multi-agent collaboration
                response = await self._multi_agent_process(
                    capable_agents, context, intent, user_message
                )
            else:
                # Single agent (use the most confident one)
                agent, confidence = capable_agents[0]
                response = await self._single_agent_process(
                    agent, context, intent
                )

            return response

        except Exception as e:
            logger.error(f"Error in routing: {e}", exc_info=True)
            return self._error_response(str(e))

    async def _single_agent_process(
        self,
        agent: BaseAgent,
        context: Context,
        intent: Intent
    ) -> OrchestratorResponse:
        """Process request with a single agent."""
        logger.info(f"Using single agent: {agent.agent_id}")

        try:
            agent_response = await agent.process(context, intent)

            return OrchestratorResponse(
                content=agent_response.content,
                modality=ModalityType.TEXT,
                agent_responses=[agent_response],
                metadata={
                    "routing_type": "single_agent",
                    "primary_agent": agent.agent_id,
                    "intent_type": intent.type.value,
                    "confidence": intent.confidence
                }
            )

        except Exception as e:
            logger.error(f"Error processing with agent {agent.agent_id}: {e}")
            return self._error_response(f"Agent error: {str(e)}")

    async def _multi_agent_process(
        self,
        capable_agents: List[tuple[BaseAgent, float]],
        context: Context,
        intent: Intent,
        user_message: str
    ) -> OrchestratorResponse:
        """
        Process request with multiple agents and aggregate responses.

        This method coordinates multiple agents working together
        to provide a comprehensive response.
        """
        logger.info(f"Using multi-agent processing with {len(capable_agents)} agents")

        agent_responses = []
        errors = []

        # Process with each capable agent (limit to top 3)
        for agent, confidence in capable_agents[:3]:
            try:
                logger.info(f"Processing with {agent.agent_id} (confidence: {confidence:.2f})")
                response = await agent.process(context, intent)
                agent_responses.append(response)
            except Exception as e:
                logger.error(f"Error with agent {agent.agent_id}: {e}")
                errors.append(f"{agent.agent_id}: {str(e)}")

        if not agent_responses:
            return self._error_response(
                "All agents failed. Errors: " + "; ".join(errors)
            )

        # Aggregate responses
        aggregated_content = await self._aggregate_responses(
            agent_responses, user_message, context
        )

        return OrchestratorResponse(
            content=aggregated_content,
            modality=ModalityType.TEXT,
            agent_responses=agent_responses,
            metadata={
                "routing_type": "multi_agent",
                "agents_used": [r.agent_id for r in agent_responses],
                "intent_type": intent.type.value,
                "confidence": intent.confidence,
                "errors": errors if errors else None
            }
        )

    async def _aggregate_responses(
        self,
        agent_responses: List[AgentResponse],
        user_message: str,
        context: Context
    ) -> str:
        """
        Aggregate multiple agent responses into a coherent answer.

        Uses LLM to combine responses from different agents
        into a single, coherent response.
        """
        if len(agent_responses) == 1:
            return agent_responses[0].content

        # Prepare aggregation prompt
        from app.services.llm_client import call_llm

        responses_text = "\n\n".join([
            f"**{resp.agent_type.value.upper()} AGENT** (confidence: {resp.confidence:.2f}):\n{resp.content}"
            for resp in agent_responses
        ])

        aggregation_prompt = f"""You are a response aggregator for a multi-agent AI system.

Multiple specialized agents have responded to the user's question. Your job is to combine their responses into a single, coherent, and helpful answer.

User's question: {user_message}

Agent responses:
{responses_text}

Instructions:
1. Combine the information from all agents into a coherent response
2. Maintain the language of the user's question (Polish/English/German)
3. Structure the response logically (if multiple topics, use sections)
4. Don't mention "Agent X said..." - present it as a unified answer
5. Keep it concise and actionable
6. If agents provide complementary information, integrate it smoothly

Return ONLY the aggregated response, no meta-commentary."""

        try:
            messages = [{"role": "system", "content": aggregation_prompt}]
            aggregated = await call_llm(messages)
            return aggregated
        except Exception as e:
            logger.error(f"Error aggregating responses: {e}")
            # Fallback: just concatenate
            return "\n\n".join([resp.content for resp in agent_responses])

    def _fallback_response(self) -> OrchestratorResponse:
        """Fallback response when no agents are available."""
        return OrchestratorResponse(
            content="Przepraszam, nie mogę obecnie przetworzyć Twojego zapytania. Spróbuj ponownie.",
            modality=ModalityType.TEXT,
            agent_responses=[],
            metadata={"routing_type": "fallback", "reason": "no_capable_agents"}
        )

    def _error_response(self, error_msg: str) -> OrchestratorResponse:
        """Error response."""
        return OrchestratorResponse(
            content="Wystąpił błąd podczas przetwarzania Twojego zapytania. Spróbuj ponownie za chwilę.",
            modality=ModalityType.TEXT,
            agent_responses=[],
            metadata={"routing_type": "error", "error": error_msg}
        )


# Singleton instance
_router = AgentRouter()


async def route_message(user_message: str, context: Context) -> OrchestratorResponse:
    """
    Convenience function to route a message.

    Args:
        user_message: User's message
        context: Conversation context

    Returns:
        OrchestratorResponse: Response from agent(s)
    """
    return await _router.route(user_message, context)
