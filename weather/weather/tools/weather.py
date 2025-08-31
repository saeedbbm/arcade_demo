import os
import requests
from typing import Annotated, Optional, List, Any, Callable, Dict, Union
from arcade_tdk import tool, ToolContext
from datetime import datetime, timezone
from functools import wraps
import time
from threading import Lock


class RateLimiter:
    """
    Simple rate limiter to prevent API abuse.
    
    In production, consider using Redis-based distributed rate limiting
    for multi-instance deployments or async libraries like aiohttp for
    better concurrency handling.
    """
    def __init__(self, calls_per_minute: int = 60) -> None:
        self.calls_per_minute = calls_per_minute
        self.calls: List[float] = []
        self.lock = Lock()
    
    def allow_request(self) -> bool:
        """Check if request is allowed under rate limit."""
        with self.lock:
            now = time.time()
            # Remove calls older than 1 minute
            self.calls = [call_time for call_time in self.calls if now - call_time < 60]
            
            if len(self.calls) < self.calls_per_minute:
                self.calls.append(now)
                return True
            return False


# Global rate limiter instance
_rate_limiter = RateLimiter(calls_per_minute=50)  # Conservative limit


def rate_limited(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to add rate limiting to API calls.
    
    This prevents hitting OpenWeatherMap's rate limits and can be extended
    for distributed systems using Redis or database-backed limiters.
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if not _rate_limiter.allow_request():
            raise ValueError("Rate limit exceeded. Please wait before making more requests.")
        return func(*args, **kwargs)
    return wrapper


@tool(requires_secrets=["OPENWEATHERMAP_API_KEY"])
@rate_limited
def get_current_weather(
    context: ToolContext,
    location: Annotated[str, "The city and country, e.g., 'San Francisco, US'"]
) -> Annotated[Dict[str, Any], "Current weather data including temperature, condition, etc."]:
    """
    Fetch current weather for a given location using OpenWeatherMap.

    Examples:
        get_current_weather(context, "London, UK") -> {'temp': 15.0, 'condition': 'Clouds', ...}
    """

    # Get API key from Arcade's secure secret management
    api_key = context.get_secret("OPENWEATHERMAP_API_KEY")
    
    url = "https://api.openweathermap.org/data/2.5/weather"
    params: Dict[str, str] = {
        "q": location,
        "appid": api_key,
        "units": "metric"
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()  # Raise error if API fails
    data = response.json()
    
    return {
        "location": f"{data['name']}, {data['sys']['country']}",
        "temperature": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "condition": data["weather"][0]["main"],
        "description": data["weather"][0]["description"],
        "humidity": data["main"]["humidity"],
        "pressure": data["main"]["pressure"],
        "wind_speed": data["wind"]["speed"],
        "visibility": data.get("visibility", 0) / 1000 if data.get("visibility") else 0,  # Convert to km
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@tool(requires_secrets=["OPENWEATHERMAP_API_KEY"])
@rate_limited
def get_forecast(
    context: ToolContext,
    location: Annotated[str, "The city and country, e.g., 'San Francisco, US'"],
    days: Annotated[int, "Number of forecast days (1-5)"] = 5
) -> Annotated[Dict[str, Any], "Forecast data with location and days list"]:
    """
    Fetch weather forecast for the next few days.

    Returns a dict with forecast data to work around Arcade's List[Dict] serialization bug.
    
    Examples:
        get_forecast(context, "Paris, FR", 3) -> {
            "location": "Paris, FR", 
            "requested_days": 3,
            "forecast": [{'date': '2025-01-27', 'temp': 20.5, ...}, ...],
            "total_days": 3
        }
    """

    original_days_request = days

    # Get API key from Arcade's secure secret management
    try:
        api_key = context.get_secret("OPENWEATHERMAP_API_KEY")
    except Exception as e:
        return {
            "location": location,
            "requested_days": original_days_request,
            "forecast": [],
            "total_days": 0,
            "error": f"API key error: {str(e)}"
        }

    if days > 5:
        days = 5  # API limitation
    
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params: Dict[str, str] = {
        "q": location,
        "appid": api_key,
        "units": "metric"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
    except Exception as e:
        return {
            "location": location,
            "requested_days": original_days_request,
            "forecast": [],
            "total_days": 0,
            "error": f"API call error: {str(e)}"
        }
    
    # Check if we have forecast data
    if "list" not in data or not data["list"]:
        return {
            "location": location,
            "requested_days": original_days_request,
            "forecast": [],
            "total_days": 0,
            "error": "No forecast data available"
        }
    
    # Group by date and get daily summaries
    daily_forecasts: Dict[str, Dict[str, Any]] = {}
    
    try:
        for item in data["list"]:
            # Safety checks for required fields
            if not all(key in item for key in ["dt", "main", "weather"]):
                continue
                
            if not item["weather"] or not item["weather"][0]:
                continue
            
            # Convert timestamp to date string
            try:
                date = datetime.fromtimestamp(item["dt"], timezone.utc).date().isoformat()
            except (ValueError, OSError):
                continue  # Skip invalid timestamps
            
            if date not in daily_forecasts:
                daily_forecasts[date] = {
                    "date": date,
                    "temperature_min": item["main"]["temp"],
                    "temperature_max": item["main"]["temp"],
                    "condition": item["weather"][0]["main"],
                    "description": item["weather"][0]["description"],
                    "humidity": item["main"]["humidity"],
                    "wind_speed": item.get("wind", {}).get("speed", 0)
                }
            else:
                # Update min/max temperatures
                daily_forecasts[date]["temperature_min"] = min(
                    daily_forecasts[date]["temperature_min"], 
                    item["main"]["temp"]
                )
                daily_forecasts[date]["temperature_max"] = max(
                    daily_forecasts[date]["temperature_max"], 
                    item["main"]["temp"]
                )
            
            # Stop after we have enough days
            if len(daily_forecasts) >= days:
                break
                
    except Exception as e:
        return {
            "location": location,
            "requested_days": original_days_request,
            "forecast": [],
            "total_days": 0,
            "error": f"Processing error: {str(e)}"
        }
    
    forecast_list = list(daily_forecasts.values())[:days]
    
    return {
        "location": location,
        "requested_days": original_days_request,
        "forecast": forecast_list,  
        "total_days": len(forecast_list)
    }

@tool(requires_secrets=["OPENWEATHERMAP_API_KEY"])
@rate_limited  
def get_weather_alerts(
    context: ToolContext,
    location: Annotated[str, "The city and country, e.g., 'San Francisco, US'"]
) -> Annotated[List[Dict[str, Any]], "List of active weather alerts/warnings"]:
    """
    Fetch active weather alerts for a given location using OpenWeatherMap.
    
    Examples:
        get_weather_alerts(context, "Miami, US") -> [{'event': 'Hurricane Warning', ...}]
    """
    # Get API key from Arcade's secure secret management
    api_key = context.get_secret("OPENWEATHERMAP_API_KEY")

    try:
        # Get coordinates for the location
        geocoding_url = "https://api.openweathermap.org/geo/1.0/direct"
        geocoding_params: Dict[str, Union[str, int]] = {
            "q": location,
            "limit": 1,
            "appid": api_key
        }
        
        geocoding_response = requests.get(geocoding_url, params=geocoding_params)
        geocoding_response.raise_for_status()
        geocoding_data = geocoding_response.json()
        
        if not geocoding_data:
            return []
        
        lat = geocoding_data[0]["lat"]
        lon = geocoding_data[0]["lon"]
        
        # Get weather alerts using One Call API
        alerts_url = "https://api.openweathermap.org/data/3.0/onecall"
        alerts_params: Dict[str, Union[str, float]] = {
            "lat": lat,
            "lon": lon,
            "appid": api_key,
            "exclude": "minutely,hourly,daily,current"  # Only get alerts
        }
        
        alerts_response = requests.get(alerts_url, params=alerts_params)
        alerts_response.raise_for_status()
        alerts_data = alerts_response.json()
        
        alerts: List[Dict[str, Any]] = []
        if "alerts" in alerts_data:
            for alert in alerts_data["alerts"]:
                alerts.append({
                    "event": alert["event"],
                    "start": datetime.fromtimestamp(alert["start"], timezone.utc).isoformat(),
                    "end": datetime.fromtimestamp(alert["end"], timezone.utc).isoformat(),
                    "description": alert["description"],
                    "sender": alert["sender_name"]
                })
        
        return alerts
        
    except requests.HTTPError as e:
        # One Call API 3.0 requires a subscription for some features
        # Return empty list if we can't access alerts
        if hasattr(e, 'response') and e.response and e.response.status_code == 401:
            return []
        raise
    except Exception:
        # Return empty list for any other issues with alerts
        return []
    

@tool(requires_secrets=["OPENWEATHERMAP_API_KEY"])
def bug_demo_empty_list(
    context: ToolContext,
    location: Annotated[str, "Location"]
) -> Annotated[List[Dict[str, Any]], "Empty List[Dict] - WORKS"]:
    """
    BUG DEMO: Empty List[Dict] works fine in Arcade runtime.
    This function should return [] successfully.
    """
    return []


@tool(requires_secrets=["OPENWEATHERMAP_API_KEY"])
def bug_demo_non_empty_list(
    context: ToolContext,
    location: Annotated[str, "Location"]  
) -> Annotated[List[Dict[str, Any]], "Non-empty List[Dict] - FAILS"]:
    """
    BUG DEMO: Non-empty List[Dict] fails in Arcade runtime.
    This function should return the list but will return None due to Arcade bug.
    
    Expected: [{"test": "data"}]
    Actual in Arcade: None
    """
    return [{"test": "data", "number": 42, "working": True}]