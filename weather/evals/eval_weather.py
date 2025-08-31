from arcade_tdk import ToolCatalog
from arcade_evals import (
    EvalRubric,
    EvalSuite,
    ExpectedToolCall,
    tool_eval,
)
from arcade_evals.critic import SimilarityCritic

import weather
from weather.tools.weather import get_current_weather, get_forecast, get_weather_alerts


# Evaluation rubric for weather tools
rubric = EvalRubric(
    fail_threshold=0.75,  # 75% pass rate required
    warn_threshold=0.90,  # 90% for good performance
)

catalog = ToolCatalog()
catalog.add_module(weather)


def create_weather_eval_suite() -> EvalSuite:
    """Create comprehensive evaluation suite for weather tools."""
    suite = EvalSuite(
        name="Weather Toolkit Evaluation",
        system_message=(
            "You are a helpful weather assistant with access to weather tools. "
            "Use the available tools to provide accurate weather information and "
            "helpful activity suggestions based on weather conditions. "
            "Always specify locations clearly and handle errors gracefully."
        ),
        catalog=catalog,
        rubric=rubric,
    )

    # Test 1: Basic current weather request
    suite.add_case(
        name="Current Weather Query",
        user_message="What's the current weather in London?",
        expected_tool_calls=[
            ExpectedToolCall(
                func=get_current_weather, 
                args={"location": "London, UK"}
            )
        ],
        rubric=rubric,
        critics=[
            SimilarityCritic(critic_field="location", weight=0.8),
        ],
    )
    
    # Test 2: Weather forecast request
    suite.add_case(
        name="Weather Forecast Query", 
        user_message="Give me a 3-day forecast for New York",
        expected_tool_calls=[
            ExpectedToolCall(
                func=get_forecast,
                args={"location": "New York, US", "days": 3}
            )
        ],
        rubric=rubric,
        critics=[
            SimilarityCritic(critic_field="location", weight=0.6),
            SimilarityCritic(critic_field="days", weight=0.4),
        ],
    )
    
    # Test 3: Weather alerts inquiry
    suite.add_case(
        name="Weather Alerts Query",
        user_message="Are there any weather warnings for Miami?",
        expected_tool_calls=[
            ExpectedToolCall(
                func=get_weather_alerts,
                args={"location": "Miami, US"}
            )
        ],
        rubric=rubric,
        critics=[
            SimilarityCritic(critic_field="location", weight=0.8),
        ],
    )
    
    # Test 4: Complex multi-step weather query
    suite.add_case(
        name="Multi-step Weather Analysis",
        user_message="I'm planning a trip to Tokyo tomorrow. What's the current weather and what should I expect for the next 2 days?",
        expected_tool_calls=[
            ExpectedToolCall(
                func=get_current_weather,
                args={"location": "Tokyo, JP"}
            ),
            ExpectedToolCall(
                func=get_forecast,
                args={"location": "Tokyo, JP", "days": 2}
            )
        ],
        rubric=rubric,
        critics=[
            SimilarityCritic(critic_field="location", weight=0.7),
        ],
    )
    
    # Test 5: Explicit location query
    suite.add_case(
        name="Explicit Location Query",
        user_message="Current weather in Paris, France please",
        expected_tool_calls=[
            ExpectedToolCall(
                func=get_current_weather,
                args={"location": "Paris, France"}
            )
        ],
        rubric=rubric,
        critics=[
            SimilarityCritic(critic_field="location", weight=0.9),
        ],
    )

    return suite


def main():
    """Main function to demonstrate evaluation setup."""
    print("🌤️  Weather Toolkit Evaluation Suite")
    print("=" * 50)
    
    try:
        # Create evaluation suite
        suite = create_weather_eval_suite()
        
        print(f"✅ Evaluation suite created successfully!")
        print(f"📊 Suite name: {suite.name}")
        print(f"🧪 Test cases: {len(suite.cases)}")
        print(f"📈 Success threshold: {rubric.fail_threshold * 100}%")
        print(f"⚠️  Warning threshold: {rubric.warn_threshold * 100}%")
        
        print("\n📋 Test Cases:")
        for i, case in enumerate(suite.cases, 1):
            print(f"  {i}. {case.name}")
            print(f"     Query: \"{case.user_message}\"")
            print(f"     Expected tools: {len(case.expected_tool_calls)}")
        
        print("\n" + "="*50)
        print("💡 To run evaluations:")
        print("   1. Set up your LLM provider (OpenAI, etc.)")
        print("   2. Configure arcade-evals with your API keys")
        print("   3. Run: arcade-evals run eval_weather.py")
        print("\n📚 For more info: https://docs.arcade.dev/evals")
        
    except Exception as e:
        print(f"❌ Error creating evaluation suite: {e}")
        print("📝 Make sure all dependencies are installed:")
        print("   - arcade-evals")
        print("   - weather toolkit")


# Optional: Create a tool_eval decorated function for arcade-evals CLI
@tool_eval()
def weather_eval_suite(config, base_url, model) -> EvalSuite:
    """Tool eval function for arcade-evals CLI integration."""
    return create_weather_eval_suite()


if __name__ == "__main__":
    main()