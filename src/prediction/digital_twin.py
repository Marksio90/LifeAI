"""
Digital Twin Engine
Creates and maintains a digital replica of the user
Updates dynamically based on decisions and feedback
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger
from dataclasses import dataclass, field
import json


@dataclass
class LifeDomain:
    """Represents a life domain in the digital twin"""
    name: str
    current_state: float  # 0-1 score
    trend: str  # "improving", "stable", "declining"
    factors: Dict[str, float] = field(default_factory=dict)
    history: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class DigitalTwin:
    """Digital representation of user's life"""
    user_id: str
    created_at: datetime
    last_updated: datetime

    # Life domains
    health: LifeDomain
    finance: LifeDomain
    psychology: LifeDomain
    relationships: LifeDomain
    personal_development: LifeDomain

    # Overall metrics
    life_satisfaction: float
    stress_level: float
    goal_progress: Dict[str, float] = field(default_factory=dict)

    # Personality and patterns
    personality_profile: Dict[str, float] = field(default_factory=dict)
    decision_patterns: Dict[str, Any] = field(default_factory=dict)
    behavioral_tendencies: Dict[str, float] = field(default_factory=dict)

    # Predictions
    predicted_trajectories: Dict[str, List[float]] = field(default_factory=dict)


class DigitalTwinEngine:
    """
    Creates and maintains digital twins of users
    Continuously updates based on interactions and feedback
    """

    def __init__(self):
        self.twins: Dict[str, DigitalTwin] = {}
        logger.info("Digital Twin Engine initialized")

    async def create_twin(
        self,
        user_id: str,
        initial_data: Optional[Dict[str, Any]] = None
    ) -> DigitalTwin:
        """
        Create new digital twin for user
        """
        now = datetime.utcnow()

        # Initialize life domains
        health = LifeDomain(
            name="health",
            current_state=initial_data.get("health_score", 0.7) if initial_data else 0.7,
            trend="stable"
        )

        finance = LifeDomain(
            name="finance",
            current_state=initial_data.get("finance_score", 0.6) if initial_data else 0.6,
            trend="stable"
        )

        psychology = LifeDomain(
            name="psychology",
            current_state=initial_data.get("psychology_score", 0.7) if initial_data else 0.7,
            trend="stable"
        )

        relationships = LifeDomain(
            name="relationships",
            current_state=initial_data.get("relationships_score", 0.6) if initial_data else 0.6,
            trend="stable"
        )

        personal_development = LifeDomain(
            name="personal_development",
            current_state=initial_data.get("development_score", 0.5) if initial_data else 0.5,
            trend="stable"
        )

        # Create twin
        twin = DigitalTwin(
            user_id=user_id,
            created_at=now,
            last_updated=now,
            health=health,
            finance=finance,
            psychology=psychology,
            relationships=relationships,
            personal_development=personal_development,
            life_satisfaction=0.65,
            stress_level=0.5
        )

        self.twins[user_id] = twin
        logger.info(f"Created digital twin for user {user_id}")

        return twin

    async def get_twin(self, user_id: str) -> Optional[DigitalTwin]:
        """Get existing digital twin"""
        return self.twins.get(user_id)

    async def update_twin(
        self,
        user_id: str,
        updates: Dict[str, Any]
    ) -> DigitalTwin:
        """
        Update digital twin with new information
        """
        twin = self.twins.get(user_id)

        if twin is None:
            # Create if doesn't exist
            twin = await self.create_twin(user_id)

        # Update domains
        if "health" in updates:
            await self._update_domain(twin.health, updates["health"])

        if "finance" in updates:
            await self._update_domain(twin.finance, updates["finance"])

        if "psychology" in updates:
            await self._update_domain(twin.psychology, updates["psychology"])

        if "relationships" in updates:
            await self._update_domain(twin.relationships, updates["relationships"])

        if "personal_development" in updates:
            await self._update_domain(twin.personal_development, updates["personal_development"])

        # Update overall metrics
        twin.life_satisfaction = self._calculate_life_satisfaction(twin)
        twin.stress_level = updates.get("stress_level", twin.stress_level)

        # Update timestamp
        twin.last_updated = datetime.utcnow()

        logger.info(f"Updated digital twin for user {user_id}")

        return twin

    async def update_from_decision(
        self,
        user_id: str,
        decision: Dict[str, Any],
        outcome: Dict[str, Any]
    ):
        """
        Update twin based on user decision and its outcome
        This is the learning loop
        """
        twin = await self.get_twin(user_id)
        if not twin:
            return

        # Record decision pattern
        decision_type = decision.get("type", "unknown")
        if decision_type not in twin.decision_patterns:
            twin.decision_patterns[decision_type] = []

        twin.decision_patterns[decision_type].append({
            "timestamp": datetime.utcnow().isoformat(),
            "decision": decision,
            "outcome": outcome,
            "satisfaction": outcome.get("satisfaction", 0.5)
        })

        # Update affected domains
        affected_domains = outcome.get("affected_domains", [])
        for domain_name in affected_domains:
            domain = getattr(twin, domain_name, None)
            if domain:
                impact = outcome.get(f"{domain_name}_impact", 0)
                domain.current_state = max(0, min(1, domain.current_state + impact))

                # Add to history
                domain.history.append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "state": domain.current_state,
                    "decision": decision.get("action", "unknown"),
                    "impact": impact
                })

        # Analyze patterns
        await self._analyze_patterns(twin)

    async def _update_domain(
        self,
        domain: LifeDomain,
        data: Dict[str, Any]
    ):
        """Update a life domain"""
        if "state" in data:
            domain.current_state = data["state"]

        if "factors" in data:
            domain.factors.update(data["factors"])

        # Determine trend
        if len(domain.history) >= 3:
            recent = [h["state"] for h in domain.history[-3:]]
            if recent[-1] > recent[0]:
                domain.trend = "improving"
            elif recent[-1] < recent[0]:
                domain.trend = "declining"
            else:
                domain.trend = "stable"

    def _calculate_life_satisfaction(self, twin: DigitalTwin) -> float:
        """
        Calculate overall life satisfaction from domains
        """
        domains = [
            twin.health.current_state,
            twin.finance.current_state,
            twin.psychology.current_state,
            twin.relationships.current_state,
            twin.personal_development.current_state
        ]

        # Weighted average (can be personalized)
        weights = [0.25, 0.20, 0.25, 0.20, 0.10]

        satisfaction = sum(d * w for d, w in zip(domains, weights))
        return satisfaction

    async def _analyze_patterns(self, twin: DigitalTwin):
        """
        Analyze behavioral patterns from decision history
        """
        # TODO: Implement ML-based pattern analysis
        # For now, simple statistics
        pass

    async def predict_trajectory(
        self,
        user_id: str,
        domain: str,
        timeframe_days: int = 30
    ) -> List[float]:
        """
        Predict future trajectory of a life domain
        Uses time series forecasting
        """
        twin = await self.get_twin(user_id)
        if not twin:
            return []

        domain_obj = getattr(twin, domain, None)
        if not domain_obj or len(domain_obj.history) < 5:
            return []

        # Simple linear trend (TODO: Replace with proper time series model)
        history = [h["state"] for h in domain_obj.history[-10:]]

        # Calculate trend
        trend = (history[-1] - history[0]) / len(history)

        # Project forward
        predictions = []
        current = history[-1]
        for _ in range(timeframe_days):
            current += trend
            current = max(0, min(1, current))  # Clip to [0, 1]
            predictions.append(current)

        return predictions

    def export_twin(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Export digital twin as JSON
        User can download their digital twin data (GDPR compliance)
        """
        twin = self.twins.get(user_id)
        if not twin:
            return None

        return {
            "user_id": twin.user_id,
            "created_at": twin.created_at.isoformat(),
            "last_updated": twin.last_updated.isoformat(),
            "domains": {
                "health": {
                    "state": twin.health.current_state,
                    "trend": twin.health.trend,
                    "factors": twin.health.factors
                },
                "finance": {
                    "state": twin.finance.current_state,
                    "trend": twin.finance.trend,
                    "factors": twin.finance.factors
                },
                "psychology": {
                    "state": twin.psychology.current_state,
                    "trend": twin.psychology.trend,
                    "factors": twin.psychology.factors
                },
                "relationships": {
                    "state": twin.relationships.current_state,
                    "trend": twin.relationships.trend,
                    "factors": twin.relationships.factors
                },
                "personal_development": {
                    "state": twin.personal_development.current_state,
                    "trend": twin.personal_development.trend,
                    "factors": twin.personal_development.factors
                }
            },
            "overall": {
                "life_satisfaction": twin.life_satisfaction,
                "stress_level": twin.stress_level
            },
            "personality": twin.personality_profile,
            "patterns": twin.decision_patterns
        }

    async def delete_twin(self, user_id: str):
        """
        Delete digital twin (GDPR right to be forgotten)
        """
        if user_id in self.twins:
            del self.twins[user_id]
            logger.info(f"Deleted digital twin for user {user_id}")
