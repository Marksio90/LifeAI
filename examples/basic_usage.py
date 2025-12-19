"""
Basic Usage Example for LifeAI Platform
Demonstrates how to interact with the API
"""
import requests
import json
from typing import Dict, Any


class LifeAIClient:
    """Simple client for LifeAI API"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session_id = None

    def health_check(self) -> Dict[str, Any]:
        """Check if API is running"""
        response = requests.get(f"{self.base_url}/health")
        return response.json()

    def create_session(self, user_id: str) -> str:
        """Create a new conversation session"""
        response = requests.post(
            f"{self.base_url}/session/create",
            json={"user_id": user_id}
        )
        data = response.json()
        self.session_id = data["session_id"]
        return self.session_id

    def chat(self, user_id: str, message: str) -> Dict[str, Any]:
        """Send a message and get response"""
        response = requests.post(
            f"{self.base_url}/chat",
            json={
                "user_id": user_id,
                "session_id": self.session_id,
                "message": message
            }
        )
        return response.json()

    def submit_feedback(self, message_index: int, helpful: bool, rating: int = None):
        """Submit feedback on a response"""
        response = requests.post(
            f"{self.base_url}/feedback",
            json={
                "session_id": self.session_id,
                "message_index": message_index,
                "helpful": helpful,
                "rating": rating
            }
        )
        return response.json()

    def get_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile"""
        response = requests.get(f"{self.base_url}/profile/{user_id}")
        return response.json()


def main():
    """Example usage"""
    # Initialize client
    client = LifeAIClient()

    # Check health
    print("🔍 Checking API health...")
    health = client.health_check()
    print(f"✅ Status: {health['status']}")
    print()

    # Create session
    user_id = "demo_user_123"
    print(f"👤 Creating session for user: {user_id}")
    session_id = client.create_session(user_id)
    print(f"✅ Session created: {session_id}")
    print()

    # Example conversations
    conversations = [
        "I'm feeling stressed about work and it's affecting my sleep. What should I do?",
        "How should I budget $5000 per month with rent being $2000?",
        "I want to start exercising but I'm not motivated. Any advice?",
        "I'm thinking about changing careers but I'm worried about financial stability."
    ]

    for i, message in enumerate(conversations, 1):
        print(f"💬 Question {i}: {message}")
        print()

        response = client.chat(user_id, message)

        print(f"🤖 Response (confidence: {response['confidence']:.2%}):")
        print(f"   Intent: {response['intent']}")
        print(f"   Agents: {', '.join(response['agents_used'])}")
        print()
        print(response['response'])
        print()
        print("-" * 80)
        print()

        # Submit feedback
        if i == 1:
            print("📝 Submitting positive feedback...")
            client.submit_feedback(i, helpful=True, rating=5)
            print("✅ Feedback submitted")
            print()

    # Get user profile
    print("📊 Getting user profile...")
    profile = client.get_profile(user_id)
    print(json.dumps(profile, indent=2))


if __name__ == "__main__":
    main()
