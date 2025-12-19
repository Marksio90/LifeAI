"""
Finance Agent - Specialized in financial planning, budgeting, and money management
Provides guidance on personal finance matters
"""
from typing import Dict, Any
from loguru import logger
import json

from ..base import BaseAgent
from src.core.models import AgentRequest


class FinanceAgent(BaseAgent):
    """
    Finance Agent specializes in:
    - Budgeting and expense tracking
    - Investment strategies
    - Savings and financial goals
    - Debt management
    - Financial planning
    - Risk assessment
    """

    def __init__(self):
        super().__init__(
            agent_id="finance",
            model="gpt-4-turbo-preview"
        )

    def _get_default_system_prompt(self) -> str:
        return """You are a Financial Planning AI Agent for the LifeAI platform.

Your expertise includes:
- Personal budgeting and expense management
- Investment strategies and portfolio planning
- Savings goals and wealth building
- Debt management and credit
- Financial risk assessment
- Retirement planning
- Tax-efficient strategies (general guidance)

Guidelines:
1. Provide practical, actionable financial advice
2. Consider user's risk tolerance and life stage
3. Focus on long-term financial health
4. Explain complex concepts simply
5. Use concrete numbers and examples
6. Be realistic about market risks
7. Encourage sustainable financial habits

IMPORTANT DISCLAIMERS:
- You are NOT a licensed financial advisor
- Always recommend consulting financial professionals for major decisions
- Do not guarantee investment returns
- Consider tax implications but recommend professional tax advice
- Focus on education and general guidance

Priorities:
1. Emergency fund and financial security
2. Debt reduction
3. Long-term investing
4. Lifestyle optimization
5. Wealth building

When uncertain, say so clearly and recommend professional consultation.
"""

    async def _process_specialized(
        self,
        request: AgentRequest
    ) -> Dict[str, Any]:
        """
        Process finance-related requests
        """
        try:
            user_message = request.user_input.content
            context = self._build_finance_context(request)

            # Call LLM with finance-specific prompt
            result = await self._call_llm(
                user_message,
                context,
                temperature=0.5  # Lower temperature for financial advice
            )

            # Add finance-specific metadata
            result["metadata"]["domain"] = "finance"
            result["metadata"]["disclaimer"] = "This is general financial education. Consult licensed financial advisors for personalized advice."

            # Check if we can provide scenario analysis
            if self._should_provide_scenarios(request):
                scenarios = await self._generate_scenarios(request, context)
                result["metadata"]["scenarios"] = scenarios

            return result

        except Exception as e:
            logger.error(f"Finance agent error: {str(e)}")
            return {
                "content": "I apologize, but I encountered an error processing your financial query. Please try again or consult a financial advisor.",
                "metadata": {"error": str(e)}
            }

    def _build_finance_context(self, request: AgentRequest) -> Dict[str, Any]:
        """Build finance-specific context"""
        context = request.context.copy()

        entities = request.intent.extracted_entities

        # Extract financial entities
        if "amount" in entities:
            context["amount"] = entities["amount"]

        if "timeframe" in entities:
            context["timeframe"] = entities["timeframe"]

        if "action" in entities:
            context["financial_action"] = entities["action"]

        return context

    def _should_provide_scenarios(self, request: AgentRequest) -> bool:
        """Determine if scenario analysis would be helpful"""
        keywords = ["invest", "save", "plan", "retire", "goal"]
        return any(kw in request.user_input.content.lower() for kw in keywords)

    async def _generate_scenarios(
        self,
        request: AgentRequest,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate simple financial scenarios
        (This will be enhanced with the Prediction Engine in Layer 3)
        """
        # Placeholder for now - will be connected to Prediction Engine
        return {
            "conservative": "Low-risk, steady growth approach",
            "moderate": "Balanced risk and return",
            "aggressive": "Higher risk for potentially higher returns"
        }


class BudgetAgent(FinanceAgent):
    """
    Specialized sub-agent for budgeting and expense tracking
    """

    def __init__(self):
        BaseAgent.__init__(self, agent_id="budget")

    def _get_default_system_prompt(self) -> str:
        return """You are a Budgeting & Expense Management AI Agent.

Your expertise:
- Creating and maintaining budgets
- Tracking expenses and spending patterns
- Identifying cost-saving opportunities
- Cash flow management
- Financial goal setting
- Spending behavior analysis

Provide practical budgeting strategies that users can actually implement.
Focus on sustainability and realistic goals.
"""
