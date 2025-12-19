"""
Identity & Context Engine (Layer 0.2)
Builds and maintains user identity in the system:
- Values and beliefs
- Goals and aspirations
- Decision history
- Thinking style
- Emotional preferences
- Life context
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger
import json

from .models import UserProfile
from config import settings


class IdentityEngine:
    """
    Manages user identity and context
    Uses graph database (Neo4j) for relationships and vector DB for semantic search
    """

    def __init__(self, neo4j_driver=None, vector_db=None):
        self.neo4j_driver = neo4j_driver
        self.vector_db = vector_db
        self.user_profiles: Dict[str, UserProfile] = {}  # In-memory cache

        logger.info("Identity Engine initialized")

    async def get_or_create_profile(self, user_id: str) -> UserProfile:
        """
        Get existing user profile or create new one
        """
        # Check cache
        if user_id in self.user_profiles:
            return self.user_profiles[user_id]

        # Try to load from database
        profile = await self._load_profile(user_id)

        if profile is None:
            # Create new profile
            profile = UserProfile(
                user_id=user_id,
                values=[],
                goals=[],
                preferences={},
                personality_traits={},
                decision_history=[]
            )
            await self._save_profile(profile)

        # Cache it
        self.user_profiles[user_id] = profile
        return profile

    async def update_profile(
        self,
        user_id: str,
        updates: Dict[str, Any]
    ) -> UserProfile:
        """
        Update user profile with new information
        """
        profile = await self.get_or_create_profile(user_id)

        # Update fields
        for key, value in updates.items():
            if hasattr(profile, key):
                setattr(profile, key, value)

        profile.updated_at = datetime.utcnow()

        # Save to database
        await self._save_profile(profile)

        # Update cache
        self.user_profiles[user_id] = profile

        logger.info(f"Updated profile for user {user_id}")
        return profile

    async def add_decision(
        self,
        user_id: str,
        decision: Dict[str, Any]
    ):
        """
        Record a user decision for learning
        """
        profile = await self.get_or_create_profile(user_id)

        decision_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "decision": decision.get("action"),
            "context": decision.get("context", {}),
            "outcome": decision.get("outcome"),
            "satisfaction": decision.get("satisfaction")
        }

        profile.decision_history.append(decision_record)

        # Keep only last 100 decisions
        if len(profile.decision_history) > 100:
            profile.decision_history = profile.decision_history[-100:]

        await self._save_profile(profile)
        logger.info(f"Recorded decision for user {user_id}")

    async def extract_values(
        self,
        user_id: str,
        conversation_text: str
    ) -> List[str]:
        """
        Extract values from user conversation
        Uses LLM to identify what matters to the user
        """
        # TODO: Implement LLM-based value extraction
        # For now, return empty list
        return []

    async def extract_goals(
        self,
        user_id: str,
        conversation_text: str
    ) -> List[str]:
        """
        Extract goals from user conversation
        """
        # TODO: Implement LLM-based goal extraction
        return []

    async def get_context(
        self,
        user_id: str,
        include_history: bool = True
    ) -> Dict[str, Any]:
        """
        Build comprehensive context for user
        """
        profile = await self.get_or_create_profile(user_id)

        context = {
            "user_id": user_id,
            "values": profile.values,
            "goals": profile.goals,
            "preferences": profile.preferences,
            "personality_traits": profile.personality_traits
        }

        if include_history:
            # Include recent decisions
            recent_decisions = profile.decision_history[-10:]
            context["recent_decisions"] = recent_decisions

        return context

    async def analyze_personality(
        self,
        user_id: str,
        interactions: List[str]
    ) -> Dict[str, float]:
        """
        Analyze personality traits from interactions
        Uses Big Five personality model: OCEAN
        - Openness
        - Conscientiousness
        - Extraversion
        - Agreeableness
        - Neuroticism
        """
        # TODO: Implement personality analysis
        # This will use NLP models to analyze language patterns
        return {
            "openness": 0.5,
            "conscientiousness": 0.5,
            "extraversion": 0.5,
            "agreeableness": 0.5,
            "neuroticism": 0.5
        }

    async def _load_profile(self, user_id: str) -> Optional[UserProfile]:
        """
        Load profile from database
        """
        # TODO: Implement database loading (Neo4j/PostgreSQL)
        # For now, return None (will create new profile)
        return None

    async def _save_profile(self, profile: UserProfile):
        """
        Save profile to database
        """
        # TODO: Implement database saving
        # For now, just log
        logger.debug(f"Saving profile for user {profile.user_id}")

    def get_life_ontology(self, user_id: str) -> Dict[str, Any]:
        """
        Build life ontology - structured representation of user's life
        """
        # This will be connected to Neo4j graph
        return {
            "domains": {
                "health": {},
                "finance": {},
                "relationships": {},
                "career": {},
                "personal_growth": {}
            },
            "connections": [],
            "priorities": []
        }


class LifeOntology:
    """
    Structured representation of user's life domains and their relationships
    Stored in graph database (Neo4j)
    """

    def __init__(self):
        self.domains = [
            "health",
            "finance",
            "relationships",
            "career",
            "personal_development",
            "leisure",
            "spirituality"
        ]

    def build_ontology(self, user_profile: UserProfile) -> Dict[str, Any]:
        """
        Build ontology from user profile
        """
        ontology = {
            "user_id": user_profile.user_id,
            "domains": {},
            "relationships": [],
            "priorities": []
        }

        # Map goals to domains
        for goal in user_profile.goals:
            domain = self._classify_goal_domain(goal)
            if domain not in ontology["domains"]:
                ontology["domains"][domain] = {"goals": []}
            ontology["domains"][domain]["goals"].append(goal)

        # Map values to domains
        for value in user_profile.values:
            domain = self._classify_value_domain(value)
            if domain not in ontology["domains"]:
                ontology["domains"][domain] = {"values": []}
            if "values" not in ontology["domains"][domain]:
                ontology["domains"][domain]["values"] = []
            ontology["domains"][domain]["values"].append(value)

        return ontology

    def _classify_goal_domain(self, goal: str) -> str:
        """Classify goal into domain"""
        # Simple keyword matching - will be replaced with ML
        goal_lower = goal.lower()

        if any(kw in goal_lower for kw in ["health", "fitness", "weight", "exercise"]):
            return "health"
        elif any(kw in goal_lower for kw in ["money", "save", "invest", "financial"]):
            return "finance"
        elif any(kw in goal_lower for kw in ["relationship", "family", "friend", "partner"]):
            return "relationships"
        elif any(kw in goal_lower for kw in ["career", "job", "work", "profession"]):
            return "career"
        else:
            return "personal_development"

    def _classify_value_domain(self, value: str) -> str:
        """Classify value into domain"""
        # Similar to goal classification
        return "personal_development"  # Default
