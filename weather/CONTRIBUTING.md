# Contributing to Weather Toolkit

Thank you for your interest in contributing to the Weather Toolkit! This project aims to provide high-quality weather integration for AI agents and applications.

## 🚀 Quick Start

1. **Fork the repository**
2. **Clone your fork**: `git clone https://github.com/saeedbbm/weather-toolkit`
3. **Set up development environment**:
   ```bash
   cd weather-toolkit/weather
   uv venv --seed -p 3.13
   make install
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

## 🛠️ Development Setup

```bash
# Set up the development environment (following Arcade standards)
cd weather
uv venv --seed -p 3.13

# Install all dependencies and pre-commit hooks
make install

# Activate the environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install optional dependencies for full development
uv sync --extra langchain
```

## 📋 Development Guidelines

### Code Style
- Follow PEP 8 guidelines
- Use type annotations for all functions (mypy strict mode)
- Run `make check` before submitting (must pass with zero errors)
- Maintain 90%+ test coverage
- Use proper error handling with Arcade's `ToolExecutionError`

### Available Make Commands
- `make install` - Install dependencies and pre-commit hooks
- `make test` - Run all tests with pytest
- `make coverage` - Generate detailed coverage report  
- `make check` - Run linting and type checking (mypy + ruff)
- `make clean-build` - Clean build artifacts
- `make build` - Build wheel file
- `make bump-version` - Bump version for releases

### Adding New Tools
1. **Create tool function** in `weather/tools/weather.py`:
   ```python
   from arcade_tdk import tool, ToolContext
   
   @tool(requires_secrets=["OPENWEATHERMAP_API_KEY"])
   @rate_limited
   def your_new_tool(
       context: ToolContext,
       param: Annotated[str, "Description"]
   ) -> Annotated[Dict[str, Any], "Return description"]:
       """Comprehensive docstring with examples."""
       api_key = context.get_secret("OPENWEATHERMAP_API_KEY")
       # Your implementation here
   ```

2. **Add comprehensive tests** in `tests/test_weather.py`
3. **Add evaluation cases** in `evals/eval_weather.py`
4. **Update exports** in `__init__.py` files
5. **Update documentation** in README.md

### Testing Requirements

- **Unit tests**: Mock all external API calls using `pytest-mock`
- **Error conditions**: Test API failures, invalid inputs, missing keys
- **Edge cases**: Empty responses, rate limiting, network timeouts
- **Type safety**: All functions must pass mypy strict checking
- **Coverage**: Maintain >90% test coverage
- **Arcade Integration**: Use `MockToolContext` for testing

```bash
# Run comprehensive testing
make test           # Unit tests
make coverage       # Coverage report  
make check          # Type checking + linting
```

### Code Quality Standards

This project follows strict quality standards:

- **Arcade Integration**: All tools use `@tool` decorator and `ToolContext`
- **Secret Management**: Use `context.get_secret()` instead of environment variables
- **Type annotations**: Every function parameter and return value
- **Error handling**: Proper exception handling with meaningful messages
- **Documentation**: Comprehensive docstrings with examples
- **Performance**: Rate limiting and efficient API usage

## 🔄 Pull Request Process

1. **Create feature branch**: `git checkout -b feature/your-feature`
2. **Implement changes** with tests and documentation
3. **Quality checks**: Ensure all checks pass
   ```bash
   make check && make test && make coverage
   ```
4. **Test deployment**: `arcade deploy` and verify tools work
5. **Update documentation** if needed
6. **Submit PR** with clear description of changes

### PR Checklist

- [ ] All tests pass (`make test`)
- [ ] Type checking passes (`make check`)
- [ ] Coverage >90% (`make coverage`)
- [ ] Documentation updated
- [ ] New tools have comprehensive tests
- [ ] Arcade secret management used (no `os.getenv()`)
- [ ] Tools deploy successfully with `arcade deploy`

## 🧪 Running Demos

Test your changes with the demo applications:

```bash
# Python client demo (uses deployed tools)
python demo/weather_agent.py

# LangChain integration demo (uses deployed tools)
python demo/langchain_agent.py

# Bug reproduction demo (for Arcade team)
python demo/bug_reproduction.py
```

## 🔧 Environment Setup

### For Development/Testing
Create `.env` file in `demo/` directory:

```bash
# For LangChain demo only
OPENAI_API_KEY=your_openai_key
```

### For Arcade Deployment
Set secrets in Arcade Dashboard:
- `OPENWEATHERMAP_API_KEY` - Your OpenWeatherMap API key

## 🐛 Bug Reports

When reporting bugs, please include:

- **Python version and OS**
- **Weather toolkit version** 
- **Arcade CLI version**
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **Tool execution results** (redact API keys!)
- **Error tracebacks** if applicable

## 💡 Feature Requests

We welcome ideas for:

- **New weather data sources** (AccuWeather, Weather.gov, etc.)
- **Additional analysis tools** (historical data, weather patterns)
- **Integration improvements** (more frameworks beyond LangChain)
- **Performance improvements** (caching, async support)
- **Enterprise features** (authentication, monitoring)

## 📞 Getting Help

- **Documentation**: Check README.md first
- **Code examples**: Look at demo/ directory
- **Issues**: Search existing issues before creating new ones
- **Discussions**: Use GitHub Discussions for questions
- **Arcade Docs**: https://docs.arcade.dev/

## 🌟 Recognition

Contributors are recognized in:

- **README.md contributors section**
- **Release notes and changelogs**
- **GitHub contributor statistics**
- **Special mentions for significant contributions**

## 🚀 Development Philosophy

This project follows these principles:

- **Rapid iteration**: Ship fast, iterate based on feedback
- **Production quality**: Every commit should be production-ready
- **Developer experience**: APIs should be intuitive and well-documented
- **Arcade-first design**: Built specifically for Arcade platform integration
- **Cross-platform**: Works seamlessly on Windows, macOS, and Linux

Thank you for helping make weather data more accessible to Arcade applications! 🌤️