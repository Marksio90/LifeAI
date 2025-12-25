"""
Decision Support Engine - AI-powered decision making assistance.

Helps users make better decisions through:
- Structured analysis (pros/cons)
- Outcome prediction
- Value alignment checking
- Risk assessment
- Alternative exploration
"""

from typing import Dict, List, Optional
from datetime import datetime
import logging

from app.services.llm_client import call_llm

logger = logging.getLogger(__name__)


class DecisionSupportEngine:
    """
    Helps users make thoughtful, well-informed decisions.
    """

    @staticmethod
    async def analyze_decision(
        decision: str,
        options: List[str],
        context: Optional[Dict] = None,
        values: Optional[List[str]] = None
    ) -> Dict:
        """
        Comprehensive decision analysis.

        Args:
            decision: The decision to be made
            options: List of possible options/choices
            context: Additional context about the decision
            values: User's core values to align with

        Returns:
            Complete decision analysis
        """
        try:
            # Build analysis prompt
            values_str = f"\nUser's core values: {', '.join(values)}" if values else ""
            context_str = f"\nContext: {context}" if context else ""

            options_list = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(options)])

            prompt = f"""You are a decision analysis expert helping someone make an important decision.

Decision to make: {decision}

Available options:
{options_list}{context_str}{values_str}

Provide a comprehensive decision analysis in JSON format:
{{
  "summary": "<brief overview of the decision>",
  "option_analysis": [
    {{
      "option": "<option name>",
      "pros": ["<pro 1>", "<pro 2>", ...],
      "cons": ["<con 1>", "<con 2>", ...],
      "short_term_impact": "<impact description>",
      "long_term_impact": "<impact description>",
      "risk_level": "<low/medium/high>",
      "alignment_with_values": "<how well it aligns>",
      "score": <0-100>
    }},
    ...
  ],
  "recommended_option": "<option name>",
  "recommendation_reasoning": "<why this option>",
  "important_considerations": ["<consideration 1>", ...],
  "questions_to_ask": ["<question 1>", ...],
  "red_flags": ["<warning 1>", ...]
}}

Be thoughtful, balanced, and considerate of the human impact of this decision."""

            response = await call_llm([{"role": "user", "content": prompt}])

            # Parse JSON response
            import json
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()

            analysis = json.loads(json_str)

            logger.info(f"Decision analyzed: {decision[:50]}...")

            return {
                "decision": decision,
                "analysis": analysis,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error analyzing decision: {e}")
            return {
                "decision": decision,
                "error": str(e),
                "analysis": None
            }

    @staticmethod
    async def explore_alternatives(
        decision: str,
        current_options: List[str],
        constraints: Optional[List[str]] = None
    ) -> Dict:
        """
        Help user discover alternative options they might not have considered.

        Args:
            decision: The decision being made
            current_options: Options already considered
            constraints: Any constraints or limitations

        Returns:
            Alternative options and creative solutions
        """
        try:
            constraints_str = f"\nConstraints: {', '.join(constraints)}" if constraints else ""
            current_str = "\n".join([f"- {opt}" for opt in current_options])

            prompt = f"""Help someone find creative alternatives for a decision they're making.

Decision: {decision}

Options they've already considered:
{current_str}{constraints_str}

Generate 3-5 alternative options they might not have thought of. Think creatively!

Return JSON format:
{{
  "alternatives": [
    {{
      "option": "<alternative option>",
      "description": "<what this involves>",
      "why_consider": "<why this is worth considering>",
      "feasibility": "<low/medium/high>",
      "creativity_score": <1-10>
    }},
    ...
  ],
  "outside_the_box_thinking": "<any completely different approach to the problem>"
}}"""

            response = await call_llm([{"role": "user", "content": prompt}])

            # Parse response
            import json
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            else:
                json_str = response.strip()

            alternatives = json.loads(json_str)

            return {
                "decision": decision,
                "alternatives": alternatives,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error exploring alternatives: {e}")
            return {"error": str(e)}

    @staticmethod
    async def predict_outcomes(
        decision: str,
        chosen_option: str,
        timeframes: List[str] = ["1 week", "1 month", "6 months", "1 year"]
    ) -> Dict:
        """
        Predict likely outcomes at different timeframes.

        Args:
            decision: The decision
            chosen_option: The option being considered
            timeframes: Time periods to predict for

        Returns:
            Outcome predictions over time
        """
        try:
            timeframes_str = ", ".join(timeframes)

            prompt = f"""Predict the likely outcomes of a decision at different points in time.

Decision: {decision}
Chosen option: {chosen_option}

Predict outcomes for these timeframes: {timeframes_str}

Return JSON:
{{
  "predictions": [
    {{
      "timeframe": "<timeframe>",
      "likely_outcomes": ["<outcome 1>", "<outcome 2>", ...],
      "challenges_faced": ["<challenge 1>", ...],
      "opportunities_created": ["<opportunity 1>", ...],
      "confidence": "<low/medium/high>"
    }},
    ...
  ],
  "overall_trajectory": "<description of overall path>",
  "key_milestones": ["<milestone 1>", ...]
}}

Be realistic but also consider positive possibilities."""

            response = await call_llm([{"role": "user", "content": prompt}])

            # Parse response
            import json
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            else:
                json_str = response.strip()

            predictions = json.loads(json_str)

            return {
                "decision": decision,
                "chosen_option": chosen_option,
                "predictions": predictions,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error predicting outcomes: {e}")
            return {"error": str(e)}

    @staticmethod
    async def check_value_alignment(
        decision: str,
        option: str,
        user_values: List[str]
    ) -> Dict:
        """
        Check how well a decision aligns with user's core values.

        Args:
            decision: The decision
            option: The option being considered
            user_values: User's core values

        Returns:
            Value alignment analysis
        """
        try:
            values_str = ", ".join(user_values)

            prompt = f"""Analyze how well a decision option aligns with someone's core values.

Decision: {decision}
Option: {option}
User's core values: {values_str}

Analyze the alignment. Return JSON:
{{
  "overall_alignment": "<strong/moderate/weak/conflicted>",
  "alignment_score": <0-100>,
  "value_analysis": [
    {{
      "value": "<value name>",
      "alignment": "<aligned/neutral/conflicts>",
      "explanation": "<how this option relates to this value>"
    }},
    ...
  ],
  "conflicts": ["<any value conflicts>"],
  "strengths": ["<where it aligns well>"],
  "recommendation": "<should they proceed based on values?>"
}}"""

            response = await call_llm([{"role": "user", "content": prompt}])

            # Parse response
            import json
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            else:
                json_str = response.strip()

            alignment = json.loads(json_str)

            return {
                "decision": decision,
                "option": option,
                "alignment_analysis": alignment,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error checking value alignment: {e}")
            return {"error": str(e)}


# Convenience functions

async def analyze_quick_decision(decision: str, option_a: str, option_b: str) -> Dict:
    """Quick A vs B decision analysis."""
    engine = DecisionSupportEngine()
    return await engine.analyze_decision(decision, [option_a, option_b])


async def should_i_do_this(action: str, user_values: Optional[List[str]] = None) -> Dict:
    """Simple should I / shouldn't I analysis."""
    engine = DecisionSupportEngine()
    return await engine.analyze_decision(
        f"Should I {action}?",
        ["Yes, do it", "No, don't do it"],
        values=user_values
    )
