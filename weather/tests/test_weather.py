import pytest
import requests
from unittest.mock import Mock, patch
from arcade_tdk.errors import ToolExecutionError
from weather.tools.weather import get_current_weather, get_forecast, get_weather_alerts


class MockToolContext:
    """Mock ToolContext for testing."""
    
    def __init__(self, api_key="test_api_key"):
        self.api_key = api_key
    
    def get_secret(self, secret_name: str) -> str:
        if secret_name == "OPENWEATHERMAP_API_KEY":
            return self.api_key
        raise ValueError(f"Secret {secret_name} not found")


class TestWeatherTools:
    """Comprehensive test suite for weather tools."""
    
    @pytest.fixture
    def mock_context(self):
        """Mock ToolContext for testing."""
        return MockToolContext()
    
    @pytest.fixture
    def mock_weather_response(self):
        """Mock successful weather API response."""
        return {
            "name": "London",
            "sys": {"country": "GB"},
            "main": {
                "temp": 15.5,
                "feels_like": 14.2,
                "humidity": 72,
                "pressure": 1013
            },
            "weather": [{
                "main": "Clouds",
                "description": "overcast clouds"
            }],
            "wind": {"speed": 3.2},
            "visibility": 10000
        }
    
    @pytest.fixture
    def mock_forecast_response(self):
        """Mock successful forecast API response."""
        return {
            "list": [
                {
                    "dt": 1672531200,
                    "main": {"temp": 10.5, "humidity": 80},
                    "weather": [{"main": "Rain", "description": "light rain"}],
                    "wind": {"speed": 2.1}
                },
                {
                    "dt": 1672617600,  # Next day
                    "main": {"temp": 12.0, "humidity": 75},
                    "weather": [{"main": "Clouds", "description": "cloudy"}],
                    "wind": {"speed": 2.5}
                }
            ]
        }

    # Current Weather Tests
    @patch('weather.tools.weather.requests.get')
    def test_get_current_weather_success(self, mock_get, mock_context, mock_weather_response):
        """Test successful current weather retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = mock_weather_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = get_current_weather(mock_context, "London, UK")
        
        # Verify core data structure
        assert result["location"] == "London, GB"
        assert result["temperature"] == 15.5
        assert result["feels_like"] == 14.2
        assert result["condition"] == "Clouds"
        assert result["description"] == "overcast clouds"
        assert result["humidity"] == 72
        assert result["wind_speed"] == 3.2
        assert "timestamp" in result
        
        # Verify API call was made with secret
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args.kwargs['params']['q'] == 'London, UK'
        assert call_args.kwargs['params']['appid'] == 'test_api_key'
        assert call_args.kwargs['params']['units'] == 'metric'
    
    @patch('weather.tools.weather.requests.get')
    def test_get_current_weather_api_error(self, mock_get, mock_context):
        """Test API error handling."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_get.return_value = mock_response
        
        with pytest.raises(ToolExecutionError):  # Changed from requests.HTTPError
            get_current_weather(mock_context, "InvalidCity")

    def test_get_current_weather_missing_api_key(self):
        """Test missing API key handling."""
        # Context without API key
        bad_context = MockToolContext(api_key="")
        bad_context.get_secret = Mock(side_effect=ValueError("Secret not found"))
        
        with pytest.raises(ToolExecutionError):  # Changed from ValueError
            get_current_weather(bad_context, "London, UK")

    # Forecast Tests
    @patch('weather.tools.weather.requests.get')
    def test_get_forecast_success(self, mock_get, mock_context, mock_forecast_response):
        """Test successful forecast retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = mock_forecast_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = get_forecast(mock_context, "London, UK", 2)
        
        # Verify forecast structure - NOW DICT FORMAT
        assert isinstance(result, dict)
        assert "forecast" in result
        assert "location" in result  
        assert "requested_days" in result
        assert "total_days" in result
        
        forecast_list = result["forecast"]
        assert len(forecast_list) <= 2
        assert "date" in forecast_list[0]
        assert "temperature_min" in forecast_list[0]
        assert "temperature_max" in forecast_list[0]
        assert "condition" in forecast_list[0]
        assert "description" in forecast_list[0]
        
    @patch('weather.tools.weather.requests.get')
    def test_get_forecast_days_limit(self, mock_get, mock_context, mock_forecast_response):
        """Test forecast days limitation."""
        mock_response = Mock()
        mock_response.json.return_value = mock_forecast_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Test days > 5 gets limited to 5
        result = get_forecast(mock_context, "London, UK", 10)
        forecast_list = result["forecast"]  # Access forecast from dict
        assert len(forecast_list) <= 5
        assert result["requested_days"] == 10  # Original request
        assert result["total_days"] <= 5       # Actual returned

    # Weather Alerts Tests
    @patch('weather.tools.weather.requests.get')
    def test_get_weather_alerts_no_alerts(self, mock_get, mock_context):
        """Test weather alerts when none are active."""
        # Mock geocoding response
        geocoding_response = Mock()
        geocoding_response.json.return_value = [{"lat": 51.5074, "lon": -0.1278}]
        geocoding_response.raise_for_status.return_value = None
        
        # Mock alerts response with no alerts
        alerts_response = Mock()
        alerts_response.json.return_value = {}  # No alerts
        alerts_response.raise_for_status.return_value = None
        
        mock_get.side_effect = [geocoding_response, alerts_response]
        
        result = get_weather_alerts(mock_context, "London, UK")
        assert result == []
    
    @patch('weather.tools.weather.requests.get')
    def test_get_weather_alerts_api_subscription_error(self, mock_get, mock_context):
        """Test weather alerts when API requires subscription."""
        # Mock geocoding response
        geocoding_response = Mock()
        geocoding_response.json.return_value = [{"lat": 51.5074, "lon": -0.1278}]
        geocoding_response.raise_for_status.return_value = None
        
        # Mock 401 error for alerts (subscription required)
        alerts_response = Mock()
        http_error = requests.HTTPError("401 Unauthorized")
        mock_response_obj = Mock()
        mock_response_obj.status_code = 401
        http_error.response = mock_response_obj
        
        alerts_response.raise_for_status.side_effect = http_error
        mock_get.side_effect = [geocoding_response, alerts_response]
        
        # Should handle gracefully and return empty list
        result = get_weather_alerts(mock_context, "London, UK")
        assert result == []


class TestToolIntegration:
    """Integration tests for tool workflow."""
    
    @pytest.fixture
    def mock_context(self):
        return MockToolContext()
    
    @patch('weather.tools.weather.requests.get')
    def test_weather_workflow(self, mock_get, mock_context):
        """Test a typical weather workflow: current + forecast."""
        # Mock current weather response
        current_mock = Mock()
        current_mock.json.return_value = {
            "name": "Paris", "sys": {"country": "FR"},
            "main": {"temp": 20.0, "feels_like": 19.5, "humidity": 65, "pressure": 1015},
            "weather": [{"main": "Clear", "description": "clear sky"}],
            "wind": {"speed": 2.5}, "visibility": 10000
        }
        current_mock.raise_for_status.return_value = None
        
        # Mock forecast response
        forecast_mock = Mock()
        forecast_mock.json.return_value = {
            "list": [
                {"dt": 1672531200, "main": {"temp": 18.0, "humidity": 70},
                 "weather": [{"main": "Rain", "description": "light rain"}], "wind": {"speed": 3.0}}
            ]
        }
        forecast_mock.raise_for_status.return_value = None
        
        mock_get.side_effect = [current_mock, forecast_mock]
        
        # Test current weather
        current = get_current_weather(mock_context, "Paris, FR")
        assert current["location"] == "Paris, FR"
        assert current["temperature"] == 20.0
        
        # Test forecast
        forecast = get_forecast(mock_context, "Paris, FR", 1)
        assert isinstance(forecast, dict)  # Changed
        assert "forecast" in forecast     # Changed
        forecast_list = forecast["forecast"]  # Added
        assert len(forecast_list) >= 1    # Changed
        assert "date" in forecast_list[0] # Changed


class TestEnvironmentConfig:
    """Test secret management."""
    
    def test_context_secret_access(self):
        """Test that context properly provides secrets."""
        context = MockToolContext(api_key="test_secret_key")
        secret = context.get_secret("OPENWEATHERMAP_API_KEY")
        assert secret == "test_secret_key"
    
    def test_context_missing_secret(self):
        """Test missing secret handling."""
        context = MockToolContext()
        with pytest.raises(ValueError):
            context.get_secret("NONEXISTENT_SECRET")


class TestDataValidation:
    """Test input validation and data processing."""
    
    @pytest.fixture
    def mock_context(self):
        return MockToolContext()
    
    @patch('weather.tools.weather.requests.get')
    def test_temperature_data_types(self, mock_get, mock_context):
        """Test that temperature values are properly handled."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "name": "Tokyo", "sys": {"country": "JP"},
            "main": {"temp": 28.5, "feels_like": 30.2, "humidity": 69, "pressure": 1015},
            "weather": [{"main": "Clear", "description": "clear sky"}],
            "wind": {"speed": 2.1}, "visibility": 10000
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = get_current_weather(mock_context, "Tokyo, JP")
        
        # Verify numeric types
        assert isinstance(result["temperature"], (int, float))
        assert isinstance(result["feels_like"], (int, float))
        assert isinstance(result["humidity"], int)
        assert isinstance(result["wind_speed"], (int, float))
    
    @patch('weather.tools.weather.requests.get')
    def test_forecast_date_format(self, mock_get, mock_context):
        """Test that forecast dates are properly formatted."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "list": [
                {"dt": 1672531200, "main": {"temp": 15.0, "humidity": 75},
                 "weather": [{"main": "Rain", "description": "rain"}], "wind": {"speed": 3.0}}
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = get_forecast(mock_context, "London, UK", 1)
    
        # Verify date format (should be ISO date string)
        assert isinstance(result, dict)        # Added
        assert "forecast" in result           # Added
        forecast_list = result["forecast"]    # Added
        assert len(forecast_list) > 0         # Changed
        date_str = forecast_list[0]["date"]   # Changed
        assert isinstance(date_str, str)
        assert len(date_str) == 10  # YYYY-MM-DD format
        assert date_str.count('-') == 2


class TestEdgeCases:
    """Test edge cases and error scenarios."""
    
    @pytest.fixture
    def mock_context(self):
        return MockToolContext()
    
    @patch('weather.tools.weather.requests.get')
    def test_weather_alerts_location_not_found(self, mock_get, mock_context):
        """Test weather alerts when location geocoding fails."""
        # Mock geocoding response with empty results
        geocoding_response = Mock()
        geocoding_response.json.return_value = []  # No location found
        geocoding_response.raise_for_status.return_value = None
        
        mock_get.return_value = geocoding_response
        
        result = get_weather_alerts(mock_context, "NonexistentCity")
        assert result == []
    
    @patch('weather.tools.weather.requests.get')
    def test_forecast_empty_response(self, mock_get, mock_context):
        """Test forecast handling when API returns empty list."""
        mock_response = Mock()
        mock_response.json.return_value = {"list": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = get_forecast(mock_context, "London, UK", 3)
        # Should return dict with empty forecast list or error
        assert isinstance(result, dict)                    # Added
        assert result["forecast"] == [] or "error" in result  # Changed
