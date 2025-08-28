# Weather Toolkit Demos

This directory contains two demos showing different levels of integration with the Weather Toolkit.

## 🌤️ Simple Demo (`weather_agent.py`)

A basic demonstration of toolkit usage without external dependencies. Perfect for understanding core functionality.

**Requirements:**
- OpenWeatherMap API key
- Python 3.10+

**Run:**
```bash
uv run python demo/weather_agent.py
```

## 🤖 Advanced Demo (`langchain_agent.py`)

Professional AI agent using LangChain for conversational weather assistance. Demonstrates production-ready agent architecture.

**Requirements:**
- OpenWeatherMap API key
- OpenAI API key  
- LangChain dependencies

**Install LangChain:**
```bash
uv add langchain langchain-openai langchain-community
```

**Run:**
```bash
uv run python demo/langchain_agent.py
```

## 🔧 Setup

1. **Environment setup:**
```bash
cd weather
uv venv --seed -p 3.13
make install
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

2. **Install optional dependencies (for advanced demo):**
```bash
uv add langchain langchain-openai langchain-community
```

3. **Create `.env` file in the weather directory:**
OPENWEATHERMAP_API_KEY=your_weather_key
OPENAI_API_KEY=your_openai_key



4. **Run demos:**
```bash
# Simple demo
uv run python demo/weather_agent.py

# Advanced demo  
uv run python demo/langchain_agent.py
```

## 💡 What Each Demo Shows

### Simple Demo
- **Direct toolkit usage** with function calls
- **Activity suggestions** based on weather conditions
- **Error handling** and user-friendly output
- **Environment variable** configuration

### Advanced Demo
- **LangChain integration** with tool-calling agents
- **Conversational interface** with natural language processing
- **Enterprise-grade error handling** and retry logic
- **Professional agent architecture** for production use

Both demonstrate real-world usage of the Weather Toolkit in agentic applications, from basic automation to sophisticated AI assistants.

## 🎯 Example Interactions

**Simple Demo Output:**
🌤️ Weather Agent Demo
Current weather in Tokyo:
🌡️ Temperature: 28.2°C
☁️ Condition: broken clouds
💡 Great weather for outdoor activities!


**Advanced Demo Interaction:**
🌤️ You: What should I pack for my trip to London tomorrow?
🤖 Weather Agent: Let me check the current weather and forecast for London...
[Uses tools to fetch data]
Based on the forecast showing 15°C and light rain, I recommend:
Waterproof jacket or umbrella
Layers for changing temperatures
Comfortable walking shoes
