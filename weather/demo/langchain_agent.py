#!/usr/bin/env python3
"""
Advanced Weather Agent using LangChain

This demonstrates professional LLM integration with the Weather Toolkit,
showing how to build production-ready agentic applications.
"""

import os
import sys
from typing import List, Optional

# Add parent directory to import weather tools
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Install python-dotenv: uv add python-dotenv")

try:
    from langchain_openai import ChatOpenAI
    from langchain.agents import create_tool_calling_agent, AgentExecutor
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.tools import Tool
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    if __name__ == "__main__":
        print("⚠️ LangChain not installed. Install with:")
        print("   uv add langchain langchain-openai langchain-community")

from weather.tools.weather import get_current_weather, get_forecast, get_weather_alerts


def create_weather_tools() -> Optional[List]:
    """
    Convert weather toolkit functions into LangChain tools.
    
    This shows how to integrate Arcade tools with LangChain for production
    agentic applications. The tools are designed to be AI-friendly with
    structured outputs that LLMs can easily parse and reason about.
    """
    if not LANGCHAIN_AVAILABLE:
        return None
    
    def current_weather_tool(location: str) -> str:
        """Get current weather with AI-friendly formatting."""
        try:
            result = get_current_weather(location)
            # Format for LLM consumption with clear structure
            return f"""Current weather in {result['location']}:
Temperature: {result['temperature']}°C (feels like {result['feels_like']}°C)
Condition: {result['description']}
Humidity: {result['humidity']}%
Wind: {result['wind_speed']} m/s
Pressure: {result['pressure']} hPa

Activity Suggestions:
{_get_activity_suggestions(result)}"""
        except Exception as e:
            return f"Error getting weather for {location}: {str(e)}"
    
    def forecast_tool(location_and_days: str) -> str:
        """Get weather forecast with intelligent parsing."""
        try:
            # Smart parsing: "London,3" or "Paris, France|5"
            if '|' in location_and_days:
                location, days_str = location_and_days.split('|')
                days = int(days_str.strip())
            elif ',' in location_and_days and location_and_days.split(',')[-1].strip().isdigit():
                parts = location_and_days.split(',')
                days = int(parts[-1].strip())
                location = ','.join(parts[:-1]).strip()
            else:
                location = location_and_days
                days = 3  # Default
            
            result = get_forecast(location, days=days)
            
            forecast_text = f"{days}-day forecast for {location}:\n\n"
            for day in result:
                forecast_text += f"{day['date']}: {day['temperature_min']:.1f}°C to {day['temperature_max']:.1f}°C\n"
                forecast_text += f"  Condition: {day['description']}\n"
                forecast_text += f"  Humidity: {day['humidity']}%\n\n"
            
            return forecast_text.strip()
        except Exception as e:
            return f"Error getting forecast: {str(e)}"
    
    def alerts_tool(location: str) -> str:
        """Get weather alerts with safety focus."""
        try:
            result = get_weather_alerts(location)
            if not result:
                return f"✅ No active weather alerts for {location}. Weather conditions are normal."
            
            alerts_text = f"⚠️ WEATHER ALERTS for {location}:\n\n"
            for alert in result:
                alerts_text += f"🚨 {alert['event']}\n"
                alerts_text += f"   Description: {alert['description']}\n"
                alerts_text += f"   Valid until: {alert['end']}\n"
                alerts_text += f"   Source: {alert['sender']}\n\n"
            
            alerts_text += "⚠️ Please take appropriate safety precautions!"
            return alerts_text
        except Exception as e:
            return f"Error checking alerts for {location}: {str(e)}"
    
    return [
        Tool(
            name="get_current_weather",
            description="Get current weather conditions for any location. Input: 'City, Country' format",
            func=current_weather_tool
        ),
        Tool(
            name="get_weather_forecast",
            description="Get weather forecast for multiple days. Input: 'City, Country|days' (e.g., 'London, UK|3')",
            func=forecast_tool
        ),
        Tool(
            name="get_weather_alerts",
            description="Check for weather warnings and alerts. Input: 'City, Country' format",
            func=alerts_tool
        )
    ]


def _get_activity_suggestions(weather: dict) -> str:
    """Generate intelligent activity suggestions based on weather conditions."""
    temp = weather['temperature']
    condition = weather['condition'].lower()
    wind = weather['wind_speed']
    
    suggestions = []
    
    # Temperature-based suggestions
    if temp > 25:
        suggestions.append("🏖️ Perfect for outdoor activities: beach, hiking, cycling")
        if temp > 30:
            suggestions.append("🏊 Consider water activities to stay cool")
    elif temp < 5:
        suggestions.append("🏠 Great for indoor activities: museums, cafes, reading")
        suggestions.append("🧥 If going out, dress warmly!")
    else:
        suggestions.append("🚶 Nice for walking, sightseeing, or light outdoor activities")
    
    # Condition-based suggestions
    if 'rain' in condition:
        suggestions.append("☔ Bring an umbrella! Indoor venues recommended")
    elif 'snow' in condition:
        suggestions.append("⛷️ Great for winter sports or enjoying hot drinks indoors")
    elif 'clear' in condition or 'sun' in condition:
        suggestions.append("☀️ Beautiful weather for photography and outdoor dining")
    
    # Wind considerations
    if wind > 10:
        suggestions.append("💨 Windy conditions - secure loose items")
    
    return ' | '.join(suggestions)


def create_weather_agent():
    """
    Create a sophisticated weather agent using LangChain.
    
    This demonstrates production-ready agent architecture with proper
    tool integration, error handling, and conversational abilities.
    """
    if not LANGCHAIN_AVAILABLE:
        return None
    
    # Initialize LLM - prefer GPT-4 for better reasoning
    try:
        llm = ChatOpenAI(
            model="gpt-4o-mini",  # Cost-effective option
            temperature=0.7,      # Balanced creativity/accuracy
            api_key=os.getenv("OPENAI_API_KEY")
        )
    except Exception as e:
        print(f"Error initializing OpenAI: {e}")
        return None
    
    # Create weather tools
    tools = create_weather_tools()
    if not tools:
        return None
    
    # Design agent prompt for weather expertise
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a professional weather assistant and activity advisor.

Your capabilities:
- Provide accurate, up-to-date weather information
- Suggest activities based on weather conditions  
- Alert users to severe weather warnings
- Help with travel and event planning

Best practices:
- Always specify locations clearly (city, country)
- Provide context for weather data (what it means for daily life)
- Prioritize safety in severe weather situations
- Be conversational and helpful

Use the available weather tools to get real-time data, then provide thoughtful recommendations."""),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}")
    ])
    
    # Create the agent with proper error handling
    try:
        agent = create_tool_calling_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,  # Shows tool usage for debugging
            handle_parsing_errors=True,  # Graceful error recovery
            max_iterations=3  # Prevent infinite loops
        )
        return agent_executor
    except Exception as e:
        print(f"Error creating agent: {e}")
        return None


def main():
    """
    Run the advanced weather agent demo.
    
    This showcases enterprise-grade agent development with proper
    configuration, error handling, and user experience design.
    """
    print("🤖 Advanced Weather Agent (LangChain + Arcade Weather Toolkit)")
    print("=" * 70)
    
    # Check LangChain availability
    if not LANGCHAIN_AVAILABLE:
        print("❌ LangChain not available. Install with:")
        print("   uv add langchain langchain-openai langchain-community")
        return
    
    # Validate environment
    required_keys = ["OPENWEATHERMAP_API_KEY", "OPENAI_API_KEY"]
    missing_keys = [key for key in required_keys if not os.getenv(key)]
    
    if missing_keys:
        print("❌ Missing required environment variables:")
        for key in missing_keys:
            print(f"   - {key}")
        print("\n📝 Add these to your .env file:")
        print("   OPENWEATHERMAP_API_KEY=your_weather_key")
        print("   OPENAI_API_KEY=your_openai_key")
        return
    
    # Create agent
    agent = create_weather_agent()
    if not agent:
        print("❌ Failed to initialize agent")
        return
    
    print("✅ Weather agent initialized successfully!")
    print("\n💡 Example queries:")
    print("• 'What's the weather like in Tokyo right now?'")
    print("• 'I'm planning a picnic in Central Park tomorrow - what's the forecast?'")
    print("• 'Are there any weather warnings for Miami this week?'")
    print("• 'Should I pack a jacket for my trip to London?'")
    print("\nType 'quit' to exit.\n")
    
    # Interactive loop with enhanced UX
    while True:
        try:
            user_input = input("🌤️ You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                print("👋 Thanks for using the Weather Agent! Stay safe!")
                break
            
            if not user_input:
                continue
            
            print("\n🤖 Weather Agent:")
            try:
                response = agent.invoke({"input": user_input})
                print(response["output"])
            except Exception as e:
                print(f"❌ Sorry, I encountered an error: {e}")
                print("💡 Try rephrasing your question or check your API keys.")
            
            print("\n" + "-" * 50 + "\n")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()