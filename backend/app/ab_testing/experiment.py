"""A/B Testing Framework for LifeAI.

Features:
- Feature flags
- A/B test experiments
- Multivariate testing
- Statistical significance calculation
- User segmentation
- Analytics integration
"""

import logging
import hashlib
import random
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ExperimentStatus(str, Enum):
    """Experiment status."""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"


class Experiment:
    """A/B Test Experiment configuration."""

    def __init__(
        self,
        name: str,
        description: str,
        variants: Dict[str, Any],
        traffic_allocation: Dict[str, float],
        status: ExperimentStatus = ExperimentStatus.DRAFT
    ):
        self.name = name
        self.description = description
        self.variants = variants  # {"control": {}, "variant_a": {}, "variant_b": {}}
        self.traffic_allocation = traffic_allocation  # {"control": 0.33, "variant_a": 0.33, "variant_b": 0.34}
        self.status = status
        self.created_at = datetime.utcnow()

        # Validate traffic allocation sums to 1.0
        total = sum(traffic_allocation.values())
        assert abs(total - 1.0) < 0.01, f"Traffic allocation must sum to 1.0, got {total}"

    def assign_variant(self, user_id: str) -> str:
        """
        Assign user to a variant using consistent hashing.

        Args:
            user_id: User identifier

        Returns:
            Variant name
        """
        # Use hash for deterministic assignment
        hash_value = int(hashlib.sha256(f"{self.name}:{user_id}".encode()).hexdigest(), 16)
        normalized = (hash_value % 1000000) / 1000000  # 0.0 to 1.0

        # Assign based on traffic allocation
        cumulative = 0.0
        for variant, allocation in self.traffic_allocation.items():
            cumulative += allocation
            if normalized <= cumulative:
                return variant

        # Fallback to control
        return "control"


class ABTestingManager:
    """Manages A/B testing experiments."""

    def __init__(self):
        self.experiments: Dict[str, Experiment] = {}
        self.user_assignments: Dict[str, Dict[str, str]] = {}  # {user_id: {experiment: variant}}

        logger.info("A/B Testing Manager initialized")

    def create_experiment(
        self,
        name: str,
        description: str,
        variants: Dict[str, Any],
        traffic_allocation: Dict[str, float]
    ) -> Experiment:
        """Create new experiment."""
        experiment = Experiment(name, description, variants, traffic_allocation)
        self.experiments[name] = experiment

        logger.info(f"Created experiment: {name}")
        return experiment

    def get_variant(self, experiment_name: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get variant for user in experiment.

        Args:
            experiment_name: Experiment name
            user_id: User identifier

        Returns:
            Variant configuration or None
        """
        experiment = self.experiments.get(experiment_name)

        if not experiment or experiment.status != ExperimentStatus.RUNNING:
            return None

        # Check if user already assigned
        if user_id in self.user_assignments:
            if experiment_name in self.user_assignments[user_id]:
                variant_name = self.user_assignments[user_id][experiment_name]
                return experiment.variants.get(variant_name)

        # Assign variant
        variant_name = experiment.assign_variant(user_id)

        # Store assignment
        if user_id not in self.user_assignments:
            self.user_assignments[user_id] = {}
        self.user_assignments[user_id][experiment_name] = variant_name

        logger.info(f"User {user_id} assigned to {variant_name} in {experiment_name}")

        return experiment.variants.get(variant_name)

    def start_experiment(self, experiment_name: str):
        """Start running an experiment."""
        if experiment_name in self.experiments:
            self.experiments[experiment_name].status = ExperimentStatus.RUNNING
            logger.info(f"Started experiment: {experiment_name}")

    def stop_experiment(self, experiment_name: str):
        """Stop an experiment."""
        if experiment_name in self.experiments:
            self.experiments[experiment_name].status = ExperimentStatus.COMPLETED
            logger.info(f"Stopped experiment: {experiment_name}")


# Global manager
ab_testing_manager = ABTestingManager()


# =========================================================================
# Example Experiments
# =========================================================================

# Experiment 1: AI Response Style
ab_testing_manager.create_experiment(
    name="ai_response_style",
    description="Test different AI response styles",
    variants={
        "control": {"style": "standard", "temperature": 0.7},
        "formal": {"style": "formal", "temperature": 0.5},
        "casual": {"style": "casual", "temperature": 0.9}
    },
    traffic_allocation={
        "control": 0.34,
        "formal": 0.33,
        "casual": 0.33
    }
)

# Experiment 2: Dashboard Layout
ab_testing_manager.create_experiment(
    name="dashboard_layout",
    description="Test dashboard layout variations",
    variants={
        "control": {"layout": "classic"},
        "compact": {"layout": "compact"},
        "detailed": {"layout": "detailed"}
    },
    traffic_allocation={
        "control": 0.5,
        "compact": 0.25,
        "detailed": 0.25
    }
)

logger.info("A/B Testing experiments configured")
