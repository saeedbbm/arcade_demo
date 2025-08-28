# Arcade Weather Toolkit

A comprehensive toolkit for fetching real-time weather data, forecasts, and alerts using the OpenWeatherMap API. This toolkit enables AI agents to provide weather-based insights and activity suggestions.
# LLM usedL Clause and Grok

## 🌟 Features

- **Current Weather**: Get real-time weather conditions for any location
- **Weather Forecasts**: 5-day weather forecasts with daily summaries  
- **Weather Alerts**: Active weather warnings and emergency alerts
- **Agent Integration**: Ready-to-use with AI frameworks like LangChain
- **Environment Support**: Automatic API key loading from .env files
- **Production Ready**: Rate limiting, comprehensive error handling, full type safety

## 🚀 Quick Start

### Prerequisites

1. **OpenWeatherMap API Key** (free): Sign up at [OpenWeatherMap](https://openweathermap.org/api)
2. **Python 3.10+**
3. **uv package manager**: Follow [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/)

### Installation

```bash
# Clone or navigate to the weather toolkit directory
cd weather

# Set up the development environment  
uv venv --seed -p 3.13

# Install dependencies and pre-commit hooks
make install

# Activate the environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Environment Configuration

Create a `.env` file in your project:

```bash
OPENWEATHERMAP_API_KEY=your_api_key_here
```

### Basic Usage

```python
from weather import get_current_weather, get_forecast, get_weather_alerts

# Get current weather
weather = get_current_weather("London, UK")
print(f"Temperature: {weather['temperature']}°C")
print(f"Condition: {weather['description']}")

# Get 3-day forecast  
forecast = get_forecast("Paris, FR", days=3)
for day in forecast:
    print(f"{day['date']}: {day['temperature_min']}°C - {day['temperature_max']}°C")

# Check for weather alerts
alerts = get_weather_alerts("Miami, US") 
for alert in alerts:
    print(f"⚠️ {alert['event']}: {alert['description']}")
```

## 🧪 Development

The Makefile provides several helpful commands:

- `make install` - Install dependencies and pre-commit hooks
- `make test` - Run all tests with pytest
- `make coverage` - Generate coverage report
- `make check` - Run linting and type checking
- `make clean-build` - Clean build artifacts

### Running Tests

```bash
make test              # Run all tests
make coverage          # Generate coverage report
make check             # Run linting and type checking
```

### Verify Local Installation

Your toolkit should be installed locally from the `make install` command. Verify it's properly registered:

```bash
arcade show --local
```

### Test Your Tools Locally

Serve your toolkit locally with the Arcade CLI:

```bash
# From the parent directory (where worker.toml is located)
cd ..
arcade serve --reload
```

Visit http://localhost:8002/worker/health to see that your worker is running.

### Running Evaluations

```bash
uv run python evals/eval_weather.py
```

### Demo Applications

```bash
# Simple demo (basic toolkit usage)
uv run python demo/weather_agent.py

# Advanced LangChain demo (requires optional dependencies)
uv add langchain langchain-openai langchain-community
uv run python demo/langchain_agent.py
```

## 🚀 Deployment

### Deploy to Arcade Cloud

Deploy directly to Arcade's cloud:

```bash
# From the parent directory (where worker.toml is located)
cd ..
arcade deploy
```

Verify deployment:
```bash
arcade worker list
```

### Package and Publish

1. **Clean previous builds:**
```bash
make clean-build
```

2. **Bump version (if updating):**
```bash
make bump-version
```

3. **Build package:**
```bash
make build
```

4. **Publish to PyPI:**
```bash
uv publish --token YOUR_PYPI_TOKEN_HERE
```

## 📊 API Reference

### `get_current_weather(location, api_key=None)`

Fetch current weather conditions.

**Parameters:**
- `location` (str): City and country, e.g., "San Francisco, US"
- `api_key` (str, optional): OpenWeatherMap API key

**Returns:** Dict with current weather data

### `get_forecast(location, api_key=None, days=5)`

Fetch weather forecast for upcoming days.

**Parameters:**
- `location` (str): City and country
- `api_key` (str, optional): OpenWeatherMap API key
- `days` (int): Number of forecast days (1-5)

**Returns:** List of daily forecast dicts

### `get_weather_alerts(location, api_key=None)`

Fetch active weather alerts and warnings.

**Parameters:**
- `location` (str): City and country
- `api_key` (str, optional): OpenWeatherMap API key

**Returns:** List of active weather alerts

## 🎯 Use Cases

- **Travel Planning**: Check weather before trips
- **Activity Suggestions**: AI agents that recommend indoor/outdoor activities
- **Safety Alerts**: Monitor severe weather warnings
- **Agricultural Apps**: Weather data for farming decisions
- **Event Planning**: Weather-aware scheduling

## 🧪 Testing & Quality

- **96% Test Coverage**: Comprehensive unit tests with mocking
- **Type Safety**: Full type annotations with mypy validation
- **Error Handling**: Graceful handling of API failures and edge cases
- **Rate Limiting**: Built-in protection against API abuse
- **Cross-Platform**: Tested on Windows, macOS, and Linux

## ⚡ Development Philosophy

This toolkit was built with rapid iteration principles:

- **6-hour delivery**: From concept to working demo
- **AI-assisted development**: Used LLM for planning and architecture
- **Production-ready**: Built for scale with proper error handling
- **Developer-focused**: Clear APIs and comprehensive documentation

## 🌟 Originality Statement

This Weather Toolkit is an original integration created specifically for the Arcade ecosystem. It provides OpenWeatherMap API integration that is not available in the existing Arcade toolkit collection, offering unique value for weather-aware AI applications.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines and how to contribute.

---

Built with ❤️ for the Arcade AI ecosystem