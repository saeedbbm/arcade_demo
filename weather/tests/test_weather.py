import pytest
import requests
from unittest.mock import Mock, patch
from arcade_tdk.errors import ToolExecutionError

from weather.tools.hello import say_hello
from weather.tools.weather import get_current_weather, get_forecast, get_weather_alerts


# Basic hello tool tests (keep for completeness)
def test_hello() -> None:
    """Test the basic hello tool functionality."""
    assert say_hello("developer") == "Hello, developer!"


def test_hello_raises_error() -> None:
    """Test hello tool error handling."""
    with pytest.raises(ToolExecutionError):
        say_hello(1)


class TestWeatherTools:
    """Comprehensive test suite for weather tools."""
    
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
    def test_get_current_weather_success(self, mock_get, mock_weather_response):
        """Test successful current weather retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = mock_weather_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = get_current_weather("London, UK", "test_api_key")
        
        # Verify core data structure
        assert result["location"] == "London, GB"
        assert result["temperature"] == 15.5
        assert result["feels_like"] == 14.2
        assert result["condition"] == "Clouds"
        assert result["description"] == "overcast clouds"
        assert result["humidity"] == 72
        assert result["wind_speed"] == 3.2
        assert "timestamp" in result
        
        # Verify API call was made
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        # Check the params were passed correctly
        assert call_args.kwargs['params']['q'] == 'London, UK'
        assert call_args.kwargs['params']['appid'] == 'test_api_key'
        assert call_args.kwargs['params']['units'] == 'metric'
    
    @patch('weather.tools.weather.requests.get')
    def test_get_current_weather_api_error(self, mock_get):
        """Test API error handling - should be wrapped in ToolExecutionError."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_get.return_value = mock_response
        
        # Arcade TDK wraps exceptions in ToolExecutionError
        with pytest.raises(ToolExecutionError) as exc_info:
            get_current_weather("InvalidCity", "test_api_key")
        
        # Verify the error message contains useful information
        assert "GetCurrentWeather" in str(exc_info.value)
    
    @patch.dict('os.environ', {}, clear=True)
    def test_get_current_weather_missing_api_key(self):
        """Test missing API key handling - should be wrapped in ToolExecutionError."""
        # Arcade TDK wraps ValueError in ToolExecutionError
        with pytest.raises(ToolExecutionError) as exc_info:
            get_current_weather("London, UK")
        
        # Verify the error message indicates the issue
        assert "GetCurrentWeather" in str(exc_info.value)

    # Forecast Tests
    @patch('weather.tools.weather.requests.get')
    def test_get_forecast_success(self, mock_get, mock_forecast_response):
        """Test successful forecast retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = mock_forecast_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = get_forecast("London, UK", "test_api_key", 2)
        
        # Verify forecast structure
        assert len(result) <= 2
        assert "date" in result[0]
        assert "temperature_min" in result[0]
        assert "temperature_max" in result[0]
        assert "condition" in result[0]
        assert "description" in result[0]
    
    @patch('weather.tools.weather.requests.get')
    def test_get_forecast_days_limit(self, mock_get, mock_forecast_response):
        """Test forecast days limitation."""
        mock_response = Mock()
        mock_response.json.return_value = mock_forecast_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Test days > 5 gets limited to 5
        result = get_forecast("London, UK", "test_api_key", 10)
        # Should be limited by API and our logic
        assert len(result) <= 5

    # Weather Alerts Tests
    @patch('weather.tools.weather.requests.get')
    def test_get_weather_alerts_no_alerts(self, mock_get):
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
        
        result = get_weather_alerts("London, UK", "test_api_key")
        assert result == []
    
    @patch('weather.tools.weather.requests.get')
    def test_get_weather_alerts_api_subscription_error(self, mock_get):
        """Test weather alerts when API requires subscription."""
        # Mock geocoding response
        geocoding_response = Mock()
        geocoding_response.json.return_value = [{"lat": 51.5074, "lon": -0.1278}]
        geocoding_response.raise_for_status.return_value = None
        
        # Mock 401 error for alerts (subscription required)
        alerts_response = Mock()
        
        # Create a proper HTTPError with response object
        http_error = requests.HTTPError("401 Unauthorized")
        mock_response_obj = Mock()
        mock_response_obj.status_code = 401
        http_error.response = mock_response_obj
        
        alerts_response.raise_for_status.side_effect = http_error
        mock_get.side_effect = [geocoding_response, alerts_response]
        
        # Should handle gracefully and return empty list
        result = get_weather_alerts("London, UK", "test_api_key")
        assert result == []


class TestToolIntegration:
    """Integration tests for tool workflow."""
    
    @patch('weather.tools.weather.requests.get')
    def test_weather_workflow(self, mock_get):
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
        current = get_current_weather("Paris, FR", "test_key")
        assert current["location"] == "Paris, FR"
        assert current["temperature"] == 20.0
        
        # Test forecast
        forecast = get_forecast("Paris, FR", "test_key", 1)
        assert len(forecast) >= 1
        assert "date" in forecast[0]


# Test environment configuration
class TestEnvironmentConfig:
    """Test environment variable handling."""
    
    @patch.dict('os.environ', {'OPENWEATHERMAP_API_KEY': 'test_env_key'})
    @patch('weather.tools.weather.requests.get')
    def test_api_key_from_environment(self, mock_get):
        """Test API key loading from environment."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "name": "Test", "sys": {"country": "US"},
            "main": {"temp": 25, "feels_like": 24, "humidity": 50, "pressure": 1000},
            "weather": [{"main": "Clear", "description": "clear"}],
            "wind": {"speed": 1.0}, "visibility": 10000
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Should use environment API key automatically
        result = get_current_weather("Test City, US")
        assert result["location"] == "Test, US"
        
        # Verify API key from environment was used
        call_args = mock_get.call_args
        assert call_args.kwargs['params']['appid'] == 'test_env_key'


# Test data validation
class TestDataValidation:
    """Test input validation and data processing."""
    
    @patch('weather.tools.weather.requests.get')
    def test_temperature_data_types(self, mock_get):
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
        
        result = get_current_weather("Tokyo, JP", "test_key")
        
        # Verify numeric types
        assert isinstance(result["temperature"], (int, float))
        assert isinstance(result["feels_like"], (int, float))
        assert isinstance(result["humidity"], int)
        assert isinstance(result["wind_speed"], (int, float))
    
    @patch('weather.tools.weather.requests.get')
    def test_forecast_date_format(self, mock_get):
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
        
        result = get_forecast("London, UK", "test_key", 1)
        
        # Verify date format (should be ISO date string)
        assert len(result) > 0
        date_str = result[0]["date"]
        assert isinstance(date_str, str)
        assert len(date_str) == 10  # YYYY-MM-DD format
        assert date_str.count('-') == 2


# Test edge cases
class TestEdgeCases:
    """Test edge cases and error scenarios."""
    
    @patch('weather.tools.weather.requests.get')
    def test_weather_alerts_location_not_found(self, mock_get):
        """Test weather alerts when location geocoding fails."""
        # Mock geocoding response with empty results
        geocoding_response = Mock()
        geocoding_response.json.return_value = []  # No location found
        geocoding_response.raise_for_status.return_value = None
        
        mock_get.return_value = geocoding_response
        
        result = get_weather_alerts("NonexistentCity", "test_api_key")
        assert result == []
    
    @patch('weather.tools.weather.requests.get')
    def test_forecast_empty_response(self, mock_get):
        """Test forecast handling when API returns empty list."""
        mock_response = Mock()
        mock_response.json.return_value = {"list": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = get_forecast("London, UK", "test_api_key", 3)
        assert result == []