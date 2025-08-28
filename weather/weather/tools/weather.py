import os
import requests
from typing import Annotated, Optional, List, Any, Callable, Dict, Union
from arcade_tdk import tool
from datetime import datetime, timezone
from functools import wraps
import time
from threading import Lock

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, skip loading .env file
    pass


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


@tool
@rate_limited
def get_current_weather(
    location: Annotated[str, "The city and country, e.g., 'San Francisco, US'"],
    api_key: Annotated[Optional[str], "OpenWeatherMap API key"] = None
) -> Annotated[Dict[str, Any], "Current weather data including temperature, condition, etc."]:
    """
    Fetch current weather for a given location using OpenWeatherMap.

    Examples:
        get_current_weather("London, UK", "your_api_key") -> {'temp': 15.0, 'condition': 'Clouds', ...}
    """
    # Use provided api_key or fall back to environment variable
    if api_key is None:
        api_key = os.getenv("OPENWEATHERMAP_API_KEY")
        if not api_key:
            raise ValueError("API key is required. Provide it as parameter or set OPENWEATHERMAP_API_KEY environment variable.")
    
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


@tool
@rate_limited
def get_forecast(
    location: Annotated[str, "The city and country, e.g., 'San Francisco, US'"],
    api_key: Annotated[Optional[str], "OpenWeatherMap API key"] = None,
    days: Annotated[int, "Number of forecast days (1-5)"] = 5
) -> Annotated[List[Dict[str, Any]], "List of daily forecast data"]:
    """
    Fetch weather forecast for the next few days.

    Examples:
        get_forecast("Paris, FR", "your_api_key", 3) -> [{'date': '2025-01-27', 'temp': 20.5, ...}, ...]
    """
    # Use provided api_key or fall back to environment variable
    if api_key is None:
        api_key = os.getenv("OPENWEATHERMAP_API_KEY")
        if not api_key:
            raise ValueError("API key is required. Provide it as parameter or set OPENWEATHERMAP_API_KEY environment variable.")
    
    if days > 5:
        days = 5  # API limitation
    
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params: Dict[str, str] = {
        "q": location,
        "appid": api_key,
        "units": "metric"
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    
    # Group by date and get daily summaries
    daily_forecasts: Dict[str, Dict[str, Any]] = {}
    for item in data["list"][:days * 8]:  # 8 forecasts per day (3-hour intervals)
        date = datetime.fromtimestamp(item["dt"], timezone.utc).date().isoformat()
        if date not in daily_forecasts:
            daily_forecasts[date] = {
                "date": date,
                "temperature_min": item["main"]["temp"],
                "temperature_max": item["main"]["temp"],
                "condition": item["weather"][0]["main"],
                "description": item["weather"][0]["description"],
                "humidity": item["main"]["humidity"],
                "wind_speed": item["wind"]["speed"]
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
    
    return list(daily_forecasts.values())[:days]


@tool
@rate_limited  
def get_weather_alerts(
    location: Annotated[str, "The city and country, e.g., 'San Francisco, US'"],
    api_key: Annotated[Optional[str], "OpenWeatherMap API key"] = None
) -> Annotated[List[Dict[str, Any]], "List of active weather alerts/warnings"]:
    """
    Fetch active weather alerts for a given location using OpenWeatherMap.
    
    Examples:
        get_weather_alerts("Miami, US", "your_api_key") -> [{'event': 'Hurricane Warning', ...}]
    """
    # Use provided api_key or fall back to environment variable
    if api_key is None:
        api_key = os.getenv("OPENWEATHERMAP_API_KEY")
        if not api_key:
            raise ValueError("API key is required. Provide it as parameter or set OPENWEATHERMAP_API_KEY environment variable.")
    
    try:
        # First get coordinates for the location
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