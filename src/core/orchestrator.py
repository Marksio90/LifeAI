"""
Core Orchestrator - The Heart of LifeAI Platform
Responsible for:
- Receiving user input
- Recognizing intent
- Routing to appropriate agents
- Merging agent responses
- Managing costs and confidence
"""
import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime
from loguru import logger

from .models import (
    UserInput, Intent, IntentType, AgentRequest, AgentResponse,
    OrchestratorResponse, ConfidenceLevel
)
from .intent_recognizer import IntentRecognizer
from .response_merger import ResponseMerger
from ..agents.base import BaseAgent


class CoreOrchestrator:
    """
    Core Orchestrator manages the entire flow of user requests
    through the multi-agent system
    """

    def __init__(
        self,
        intent_recognizer: IntentRecognizer,
        response_merger: ResponseMerger,
        max_agents: int = 5,
        confidence_threshold: float = 0.7
    ):
        self.intent_recognizer = intent_recognizer
        self.response_merger = response_merger
        self.max_agents = max_agents
        self.confidence_threshold = confidence_threshold
        self.agents: Dict[str, BaseAgent] = {}
        self.agent_costs: Dict[str, float] = {}

        logger.info("CoreOrchestrator initialized")

    def register_agent(self, agent_id: str, agent: BaseAgent):
        """Register an agent with the orchestrator"""
        self.agents[agent_id] = agent
        self.agent_costs[agent_id] = 0.0
        logger.info(f"Registered agent: {agent_id}")

    def unregister_agent(self, agent_id: str):
        """Unregister an agent"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            del self.agent_costs[agent_id]
            logger.info(f"Unregistered agent: {agent_id}")

    async def process_input(
        self,
        user_input: UserInput,
        user_context: Optional[Dict[str, Any]] = None
    ) -> OrchestratorResponse:
        """
        Main processing pipeline:
        1. Recognize intent
        2. Select appropriate agents
        3. Execute agents in parallel
        4. Merge responses
        5. Return final response
        """
        start_time = datetime.utcnow()
        logger.info(f"Processing input from user {user_input.user_id}")

        try:
            # Step 1: Recognize intent
            intent = await self.intent_recognizer.recognize(
                user_input.content,
                user_context
            )
            logger.info(f"Detected intent: {intent.intent_type} (confidence: {intent.confidence:.2f})")

            # Step 2: Select agents
            selected_agents = self._select_agents(intent)
            logger.info(f"Selected {len(selected_agents)} agents: {[a for a in selected_agents]}")

            # Step 3: Execute agents in parallel
            agent_responses = await self._execute_agents(
                selected_agents,
                user_input,
                intent,
                user_context or {}
            )

            # Step 4: Filter low-confidence responses
            filtered_responses = self._filter_responses(
                agent_responses,
                self.confidence_threshold
            )

            # Step 5: Merge responses
            merged_content = await self.response_merger.merge(
                filtered_responses,
                intent,
                user_input
            )

            # Calculate overall confidence
            total_confidence = self._calculate_total_confidence(filtered_responses)

            # Create final response
            response = OrchestratorResponse(
                user_id=user_input.user_id,
                session_id=user_input.session_id,
                content=merged_content,
                agent_responses=filtered_responses,
                total_confidence=total_confidence,
                intent=intent,
                metadata={
                    "processing_time": (datetime.utcnow() - start_time).total_seconds(),
                    "agents_used": len(filtered_responses),
                    "total_cost": sum(self.agent_costs.values())
                }
            )

            logger.info(f"Successfully processed input (confidence: {total_confidence:.2f})")
            return response

        except Exception as e:
            logger.error(f"Error processing input: {str(e)}")
            raise

    def _select_agents(self, intent: Intent) -> List[str]:
        """
        Select appropriate agents based on intent
        Returns list of agent IDs to activate
        """
        agent_mapping = {
            IntentType.HEALTH: ["health"],
            IntentType.FINANCE: ["finance"],
            IntentType.PSYCHOLOGY: ["psychology"],
            IntentType.RELATIONSHIPS: ["relationships"],
            IntentType.PERSONAL_DEVELOPMENT: ["personal_development"],
            IntentType.GENERAL: ["meta"],
            IntentType.MULTI_DOMAIN: []  # Will be handled specially
        }

        if intent.intent_type == IntentType.MULTI_DOMAIN:
            # For multi-domain, activate agents for all sub-intents
            agents = []
            for sub_intent in intent.sub_intents:
                agents.extend(agent_mapping.get(sub_intent, []))
            # Add meta agent to supervise
            agents.append("meta")
            return list(set(agents))[:self.max_agents]

        agents = agent_mapping.get(intent.intent_type, ["meta"])
        return [a for a in agents if a in self.agents]

    async def _execute_agents(
        self,
        agent_ids: List[str],
        user_input: UserInput,
        intent: Intent,
        context: Dict[str, Any]
    ) -> List[AgentResponse]:
        """Execute selected agents in parallel"""

        tasks = []
        for agent_id in agent_ids:
            if agent_id in self.agents:
                agent = self.agents[agent_id]
                request = AgentRequest(
                    agent_id=agent_id,
                    user_input=user_input,
                    intent=intent,
                    context=context
                )
                tasks.append(self._execute_single_agent(agent, request))

        # Execute all agents in parallel
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions and log errors
        valid_responses = []
        for resp in responses:
            if isinstance(resp, Exception):
                logger.error(f"Agent execution failed: {str(resp)}")
            else:
                valid_responses.append(resp)
                # Track costs
                if resp.tokens_used:
                    self.agent_costs[resp.agent_id] += resp.tokens_used * 0.00001  # Rough estimate

        return valid_responses

    async def _execute_single_agent(
        self,
        agent: BaseAgent,
        request: AgentRequest
    ) -> AgentResponse:
        """Execute a single agent with timeout"""
        try:
            response = await asyncio.wait_for(
                agent.process(request),
                timeout=request.timeout
            )
            return response
        except asyncio.TimeoutError:
            logger.warning(f"Agent {request.agent_id} timed out")
            return AgentResponse(
                agent_id=request.agent_id,
                content="Agent timed out",
                confidence=0.0,
                confidence_level=ConfidenceLevel.UNCERTAIN,
                processing_time=request.timeout,
                metadata={"error": "timeout"}
            )

    def _filter_responses(
        self,
        responses: List[AgentResponse],
        threshold: float
    ) -> List[AgentResponse]:
        """Filter out low-confidence responses"""
        return [r for r in responses if r.confidence >= threshold]

    def _calculate_total_confidence(
        self,
        responses: List[AgentResponse]
    ) -> float:
        """Calculate weighted average confidence"""
        if not responses:
            return 0.0

        total_weight = sum(r.confidence for r in responses)
        if total_weight == 0:
            return 0.0

        weighted_sum = sum(r.confidence * r.confidence for r in responses)
        return weighted_sum / total_weight

    def get_statistics(self) -> Dict[str, Any]:
        """Get orchestrator statistics"""
        return {
            "registered_agents": len(self.agents),
            "total_costs": sum(self.agent_costs.values()),
            "agent_costs": self.agent_costs.copy()
        }
