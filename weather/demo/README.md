# Weather Toolkit Demos

This directory contains demos showing how to integrate with deployed Weather Toolkit tools on the Arcade platform.

## 🌤️ Python Client Demo (`weather_agent.py`)

Demonstrates how to use deployed weather tools with Arcade's Python client. Shows direct API integration patterns for developers.

**Requirements:**
- Deployed Weather Toolkit on Arcade platform
- Arcade API key
- Python 3.10+

**Run:**
```bash
python demo/weather_agent.py
```

## 🤖 LangChain Integration Demo (`langchain_agent.py`)

Professional agent using LangChain with deployed Arcade tools. Demonstrates production-ready agent architecture with conversational weather assistance.

**Requirements:**
- Deployed Weather Toolkit on Arcade platform
- Arcade API key
- OpenAI API key (for LangChain agent)
- LangChain dependencies

**Setup:**
```bash
# Install LangChain dependencies
uv sync --extra langchain

# Create demo/.env file:
echo "OPENAI_API_KEY=your_openai_key_here" > demo/.env
```

**Run:**
```bash
python demo/langchain_agent.py
```

## 🐛 Bug Reproduction Demo (`bug_reproduction.py`)

Demonstrates an Arcade platform serialization bug where non-empty `List[Dict]` return types fail in the runtime.

**Run:**
```bash
python demo/bug_reproduction.py
```

## 🔧 Setup Requirements

### 1. Deploy Weather Toolkit

First, ensure the weather toolkit is deployed to Arcade:

```bash
cd weather  # Navigate to toolkit directory
cd ..       # Go to directory with worker.toml
arcade deploy
```

### 2. Environment Setup (for LangChain demo only)

Create `demo/.env` file:
```bash
OPENAI_API_KEY=your_openai_key_here
```

**Note**: The `OPENWEATHERMAP_API_KEY` is managed by Arcade's secure secret management system, not environment variables.

### 3. Install Demo Dependencies

```bash
# For LangChain demo only
uv sync --extra langchain
```

## 💡 What Each Demo Shows

### Python Client Demo (`weather_agent.py`)
- **Direct tool usage** with `arcadepy.Arcade` client
- **Business logic examples** (event scheduling, travel planning)
- **Flask integration patterns** for web applications
- **Real API responses** from deployed tools
- **Error handling** and data validation

### LangChain Demo (`langchain_agent.py`)
- **LangChain integration** with `langchain-arcade` package
- **Conversational interface** with natural language processing
- **Agent-based architecture** for production use
- **Real tool execution** through deployed Arcade tools
- **Professional response formatting**

### Bug Demo (`bug_reproduction.py`)
- **Minimal bug reproduction** for Arcade engineering team
- **Clear demonstration** of List[Dict] serialization issue
- **Comparison testing** (empty vs non-empty lists)
- **Documentation** for issue reporting

## 🎯 Integration Patterns

### Direct API Integration
```python
from arcadepy import Arcade

client = Arcade(api_key="your_arcade_api_key")
result = client.tools.execute(
    tool_name="Weather.GetCurrentWeather",
    input={"location": "London, UK"},
    user_id="your_user_id"
)
```

### LangChain Integration
```python
from langchain_arcade import ArcadeToolManager

manager = ArcadeToolManager(api_key="your_arcade_api_key")
tools = manager.get_tools(toolkits=["weather"])
# Use tools with any LangChain agent
```

### Business Logic Integration
```python
def should_schedule_event(location):
    forecast = client.tools.execute(
        tool_name="Weather.GetForecast",
        input={"location": location, "days": 3},
        user_id="business_logic"
    )
    # Analyze forecast data for business decisions
    return analysis_result
```

## 📊 Expected Output Examples

### Python Client Demo Output: