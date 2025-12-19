"""
Advanced Example: Life Simulation
Demonstrates the Prediction & Simulation Engine
"""
import asyncio
from src.prediction.simulation_engine import LifeSimulationEngine
from src.prediction.digital_twin import DigitalTwinEngine


async def simulate_career_change():
    """Example: Simulate career change decision"""

    # Initialize engines
    simulation_engine = LifeSimulationEngine()
    twin_engine = DigitalTwinEngine()

    # Create digital twin
    user_id = "demo_user"
    twin = await twin_engine.create_twin(
        user_id,
        initial_data={
            "health_score": 0.7,
            "finance_score": 0.6,
            "psychology_score": 0.5,  # Current stress from job
            "relationships_score": 0.7,
            "development_score": 0.4   # Feeling stuck
        }
    )

    print("🧬 Digital Twin Created")
    print(f"   Life Satisfaction: {twin.life_satisfaction:.2%}")
    print(f"   Stress Level: {twin.stress_level:.2%}")
    print()

    # Simulate decision: Change career
    user_profile = {
        "personality_traits": {
            "openness": 0.7,          # Willing to try new things
            "conscientiousness": 0.8,  # Organized and responsible
            "extraversion": 0.6,
            "agreeableness": 0.7,
            "neuroticism": 0.4         # Relatively stable emotionally
        }
    }

    context = {
        "health_score": twin.health.current_state,
        "financial_score": twin.finance.current_state,
        "emotional_score": twin.psychology.current_state,
        "social_score": twin.relationships.current_state,
        "stress_level": twin.stress_level,
        "current_situation": "Unhappy with current job, considering career change"
    }

    decision = "Change career to a field I'm passionate about"

    print("🎯 Simulating Decision:", decision)
    print()

    # Run simulation
    result = await simulation_engine.simulate_decision(
        user_profile=user_profile,
        decision=decision,
        context=context,
        timeframes=["1_month", "6_months", "1_year", "5_years"]
    )

    print("📊 Simulation Results")
    print("=" * 80)
    print()

    # Display scenarios
    for scenario in result.scenarios:
        print(f"⏰ Timeframe: {scenario.timeframe.replace('_', ' ').title()}")
        print(f"   Confidence: {scenario.confidence:.2%}")
        print(f"   Probability of success: {scenario.probability:.2%}")
        print(f"   Domains affected: {', '.join(scenario.domains_affected)}")
        print()

        outcomes = scenario.predicted_outcomes
        print("   Predicted Outcomes:")
        for key, value in outcomes.items():
            if isinstance(value, dict) and "mean" in value:
                print(f"      {key}: {value['mean']:.2%} (±{value['std']:.2%})")
        print()

    print("-" * 80)
    print()

    # Risk assessment
    print("⚠️  Risk Assessment")
    for risk_type, risk_value in result.risk_assessment.items():
        risk_level = "🟢 Low" if risk_value < 0.3 else "🟡 Medium" if risk_value < 0.6 else "🔴 High"
        print(f"   {risk_type}: {risk_level} ({risk_value:.2%})")
    print()

    # Recommendation
    print("💡 Recommendation")
    print(f"   {result.recommended_action}")
    print()

    # Best vs Worst scenario
    print("📈 Best Case Scenario")
    best = result.best_scenario
    print(f"   Timeframe: {best.timeframe}")
    print(f"   Satisfaction: {best.predicted_outcomes['overall_satisfaction']['mean']:.2%}")
    print()

    print("📉 Worst Case Scenario")
    worst = result.worst_scenario
    print(f"   Timeframe: {worst.timeframe}")
    print(f"   Satisfaction: {worst.predicted_outcomes['overall_satisfaction']['mean']:.2%}")
    print()


async def track_twin_evolution():
    """Example: Track how digital twin evolves over time"""

    twin_engine = DigitalTwinEngine()

    user_id = "demo_user_2"

    # Create twin
    twin = await twin_engine.create_twin(user_id)

    print("🧬 Digital Twin - Initial State")
    print(f"   Health: {twin.health.current_state:.2%}")
    print(f"   Finance: {twin.finance.current_state:.2%}")
    print(f"   Psychology: {twin.psychology.current_state:.2%}")
    print(f"   Life Satisfaction: {twin.life_satisfaction:.2%}")
    print()

    # Simulate decisions and updates
    decisions = [
        {
            "decision": {"type": "health", "action": "Started regular exercise"},
            "outcome": {
                "affected_domains": ["health", "psychology"],
                "health_impact": 0.1,
                "psychology_impact": 0.05,
                "satisfaction": 0.8
            }
        },
        {
            "decision": {"type": "finance", "action": "Created budget and savings plan"},
            "outcome": {
                "affected_domains": ["finance", "psychology"],
                "finance_impact": 0.15,
                "psychology_impact": 0.05,
                "satisfaction": 0.9
            }
        },
        {
            "decision": {"type": "relationships", "action": "Improved communication with partner"},
            "outcome": {
                "affected_domains": ["relationships", "psychology"],
                "relationships_impact": 0.2,
                "psychology_impact": 0.1,
                "satisfaction": 0.9
            }
        }
    ]

    print("🔄 Simulating Decisions Over Time...")
    print()

    for i, decision_data in enumerate(decisions, 1):
        print(f"Decision {i}: {decision_data['decision']['action']}")

        await twin_engine.update_from_decision(
            user_id,
            decision_data["decision"],
            decision_data["outcome"]
        )

        twin = await twin_engine.get_twin(user_id)

        print(f"   Health: {twin.health.current_state:.2%} ({twin.health.trend})")
        print(f"   Finance: {twin.finance.current_state:.2%} ({twin.finance.trend})")
        print(f"   Psychology: {twin.psychology.current_state:.2%} ({twin.psychology.trend})")
        print(f"   Relationships: {twin.relationships.current_state:.2%} ({twin.relationships.trend})")
        print(f"   Life Satisfaction: {twin.life_satisfaction:.2%}")
        print()

    # Export twin data
    print("📦 Exporting Digital Twin...")
    export = twin_engine.export_twin(user_id)
    print(f"   Created: {export['created_at']}")
    print(f"   Last Updated: {export['last_updated']}")
    print(f"   Overall Life Satisfaction: {export['overall']['life_satisfaction']:.2%}")
    print()


async def main():
    """Run examples"""
    print("=" * 80)
    print("🧠 LifeAI - Advanced Simulation Examples")
    print("=" * 80)
    print()

    print("Example 1: Career Change Simulation")
    print("-" * 80)
    await simulate_career_change()

    print()
    print("=" * 80)
    print()

    print("Example 2: Digital Twin Evolution")
    print("-" * 80)
    await track_twin_evolution()


if __name__ == "__main__":
    asyncio.run(main())
