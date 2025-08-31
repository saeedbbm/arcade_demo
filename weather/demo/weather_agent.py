#!/usr/bin/env python3
"""
Weather Tools Usage Example - Python Client

This demonstrates how to use deployed weather tools in Python applications 
using Arcade's official Python client.

Based on: https://docs.arcade.dev/home/quickstart
"""

import os

try:
    from arcadepy import Arcade
    ARCADE_AVAILABLE = True
except ImportError:
    ARCADE_AVAILABLE = False
    print("❌ Install: pip install arcadepy")


def basic_weather_client():
    """Basic usage example - how most developers would integrate weather tools."""
    print("🌤️  Weather Tools - Python Client Demo")
    print("=" * 45)
    
    if not ARCADE_AVAILABLE:
        return None
    
    # Initialize client
    client = Arcade(api_key="arc_o19usaCegaoBJDD3xqmQGYktA8hm3syPBeLQeGdSgDtuJR4QsHnK")
    user_id = "saeed.babamohamadi@gmail.com"
    
    try:
        # Get current weather
        print("🔧 Testing current weather...")
        weather = client.tools.execute(
            tool_name="Weather.GetCurrentWeather",
            input={"location": "Tokyo, Japan"},
            user_id=user_id,
        )
        
        print(f"✅ Tokyo Weather: {weather.output.value['temperature']}°C")
        print(f"   Condition: {weather.output.value['description']}")
        print(f"   Wind: {weather.output.value['wind_speed']} m/s")
        
        print("\n🔧 Testing forecast...")
        forecast = client.tools.execute(
            tool_name="Weather.GetForecast",
            input={"location": "London, UK", "days": 3},
            user_id=user_id,
        )
        
        forecast_data = forecast.output.value
        if forecast_data and "forecast" in forecast_data:
            forecast_days = forecast_data["forecast"]
            print(f"✅ London {forecast_data['total_days']}-day Forecast:")
            for day in forecast_days:
                print(f"   {day['date']}: {day['temperature_min']}-{day['temperature_max']}°C ({day['description']})")
        else:
            print(f"❌ Forecast failed: {forecast_data}")
        
        # Get weather alerts
        print("\n🔧 Testing weather alerts...")
        alerts = client.tools.execute(
            tool_name="Weather.GetWeatherAlerts",
            input={"location": "Miami, US"},
            user_id=user_id,
        )
        
        alerts_data = alerts.output.value
        if alerts_data:
            print(f"✅ Miami Weather Alerts: {len(alerts_data)} alerts")
            for alert in alerts_data:
                print(f"   🚨 {alert['event']}: {alert['description']}")
        else:
            print("✅ Miami Weather Alerts: No active alerts")
            
        return client
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def flask_integration_example(client):
    """Example showing how to integrate with a Flask web application."""
    print("\n🌐 Flask Integration Pattern")
    print("=" * 30)
    
    def get_city_weather_summary(city):
        """Function that could be used in a Flask route."""
        try:
            # Get current weather
            current = client.tools.execute(
                tool_name="Weather.GetCurrentWeather",
                input={"location": city},
                user_id="web_user",
            )
            
            # Get 3-day forecast  
            forecast = client.tools.execute(
                tool_name="Weather.GetForecast",
                input={"location": city, "days": 3},
                user_id="web_user",
            )
            
            current_data = current.output.value
            forecast_data = forecast.output.value
            
            return {
                "current": {
                    "temperature": current_data["temperature"],
                    "condition": current_data["description"],
                    "wind": current_data["wind_speed"]
                },
                "forecast": forecast_data["forecast"] if forecast_data else []
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    # Demo the function
    result = get_city_weather_summary("Paris, FR")
    print(f"📊 Paris Weather Summary:")
    print(f"   Current: {result['current']['temperature']}°C, {result['current']['condition']}")
    print(f"   3-day forecast: {len(result['forecast'])} days available")


def business_logic_example(client):
    """Example of business logic using weather data."""
    print("\n💼 Business Logic Pattern")
    print("=" * 25)
    
    def should_schedule_outdoor_event(city, days_ahead=3):
        """Business logic: Should we schedule an outdoor event?"""
        try:
            forecast = client.tools.execute(
                tool_name="Weather.GetForecast",
                input={"location": city, "days": days_ahead},
                user_id="business_user",
            )
            
            forecast_data = forecast.output.value
            if not forecast_data or "forecast" not in forecast_data:
                return False, "No forecast data available"
            
            forecast_days = forecast_data["forecast"]
            good_weather_days = 0
            
            for day in forecast_days:
                # Good weather = no rain, temp 10-30°C
                if (day["condition"] not in ["Rain", "Thunderstorm", "Snow"] and 
                    10 <= day["temperature_max"] <= 30):
                    good_weather_days += 1
            
            success_rate = good_weather_days / len(forecast_days)
            recommend = success_rate >= 0.7  # 70% good weather
            
            return recommend, f"{good_weather_days}/{len(forecast_days)} days have good weather"
            
        except Exception as e:
            return False, f"Error: {e}"
    
    # Test the business logic
    cities = ["Barcelona, ES", "London, UK", "Singapore, SG"]
    
    for city in cities:
        recommend, reason = should_schedule_outdoor_event(city)
        status = "✅ SCHEDULE" if recommend else "❌ RESCHEDULE"
        print(f"   {city}: {status} - {reason}")


if __name__ == "__main__":
    client = basic_weather_client()
    
    if client:
        flask_integration_example(client)
        business_logic_example(client)
        
        print(f"\n🎉 SUCCESS! Weather Tools Working!")
        print(f"📋 Developer Integration Summary:")
        print(f"   🔧 Tool format: Weather.{{ToolName}}")
        print(f"   🔌 Client: arcadepy.Arcade") 
        print(f"   🌍 Real weather data from deployed tools!")
        print(f"   💼 No weather API keys needed!")
        print(f"   📊 Forecast format: dict with 'forecast' key containing days list")