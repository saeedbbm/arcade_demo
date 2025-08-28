#!/usr/bin/env python3
"""
Weather Agent Demo

A simple demonstration of how to use the Weather Toolkit with an AI agent.
This shows real-world usage of the weather tools in an agentic context.
"""

import os
import sys

# Add parent directory to path to import weather tools
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv not installed. Install with: pip install python-dotenv")

from weather.tools.weather import get_current_weather, get_forecast


def simple_weather_agent():
    """A simple weather agent demonstrating toolkit usage."""
    print("🌤️  Weather Agent Demo")
    print("=" * 40)
    
    # Check API key
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    if not api_key:
        print("❌ No API key found. Set OPENWEATHERMAP_API_KEY in .env file")
        return
    
    print("✅ API key loaded!")
    
    # Demo scenarios
    scenarios = [
        {
            "query": "Current weather in Tokyo",
            "location": "Tokyo, JP",
            "action": "current"
        },
        {
            "query": "3-day forecast for London", 
            "location": "London, UK",
            "action": "forecast",
            "days": 3
        }
    ]
    
    for scenario in scenarios:
        print(f"\n🔍 Query: {scenario['query']}")
        
        try:
            if scenario['action'] == 'current':
                result = get_current_weather(scenario['location'])
                print(f"🌡️ Temperature: {result['temperature']}°C")
                print(f"☁️ Condition: {result['description']}")
                print(f"💨 Wind: {result['wind_speed']} m/s")
                
                # Activity suggestion
                temp = result['temperature']
                if temp > 25:
                    print("💡 Great weather for outdoor activities!")
                elif temp < 5:
                    print("💡 Perfect for cozy indoor activities!")
                else:
                    print("💡 Nice weather for any activities!")
                    
            elif scenario['action'] == 'forecast':
                result = get_forecast(scenario['location'], days=scenario['days'])
                print(f"📅 {scenario['days']}-day forecast:")
                for day in result:
                    print(f"  {day['date']}: {day['temperature_min']:.1f}°C - {day['temperature_max']:.1f}°C")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n🎉 Demo completed!")


if __name__ == "__main__":
    simple_weather_agent()