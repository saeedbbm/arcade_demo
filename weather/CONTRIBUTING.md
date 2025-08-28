# Contributing to Weather Toolkit

Thank you for your interest in contributing to the Weather Toolkit! This project aims to provide high-quality weather integration for AI agents and applications.

## 🚀 Quick Start

1. **Fork the repository**
2. **Clone your fork**: `git clone https://github.com/yourusername/weather-toolkit`
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
uv add langchain langchain-openai langchain-community
```

## 📋 Development Guidelines

### Code Style
- Follow PEP 8 guidelines
- Use type annotations for all functions (mypy strict mode)
- Run `make check` before submitting (must pass with zero errors)
- Maintain 90%+ test coverage
- Use proper error handling with `raise_for_status()`

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
   @tool
   @rate_limited
   def your_new_tool(
       param: Annotated[str, "Description"],
       api_key: Annotated[Optional[str], "OpenWeatherMap API key"] = None
   ) -> Annotated[Dict[str, Any], "Return description"]:
       """Comprehensive docstring with examples."""
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

```bash
# Run comprehensive testing
make test           # Unit tests
make coverage       # Coverage report  
make check          # Type checking + linting
```

### Code Quality Standards

This project follows strict quality standards:

- **Type annotations**: Every function parameter and return value
- **Error handling**: Proper exception handling with meaningful messages
- **Documentation**: Comprehensive docstrings with examples
- **Performance**: Rate limiting and efficient API usage
- **Security**: Environment-based API key management

## 🔄 Pull Request Process

1. **Create feature branch**: `git checkout -b feature/your-feature`
2. **Implement changes** with tests and documentation
3. **Quality checks**: Ensure all checks pass
   ```bash
   make check && make test && make coverage
   ```
4. **Update documentation** if needed
5. **Submit PR** with clear description of changes

### PR Checklist

- [ ] All tests pass (`make test`)
- [ ] Type checking passes (`make check`)
- [ ] Coverage >90% (`make coverage`)
- [ ] Documentation updated
- [ ] New tools have comprehensive tests
- [ ] API keys and secrets are handled securely

## 🧪 Running Demos

Test your changes with the demo applications:

```bash
# Simple demo (no external dependencies)
uv run python demo/weather_agent.py

# Advanced LangChain demo
uv add langchain langchain-openai langchain-community
uv run python demo/langchain_agent.py
```

## 🔧 Environment Setup

Create `.env` file for testing:

```bash
# Required for testing
OPENWEATHERMAP_API_KEY=your_test_key

# Optional for LangChain demos
OPENAI_API_KEY=your_openai_key
```

## 🐛 Bug Reports

When reporting bugs, please include:

- **Python version and OS**
- **Weather toolkit version** 
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **API responses** (redact API keys!)
- **Error tracebacks** if applicable

## 💡 Feature Requests

We welcome ideas for:

- **New weather data sources** (AccuWeather, Weather.gov, etc.)
- **Additional analysis tools** (historical data, weather patterns)
- **AI agent integrations** (more LLM frameworks)
- **Performance improvements** (caching, async support)
- **Enterprise features** (authentication, monitoring)

## 📞 Getting Help

- **Documentation**: Check README.md first
- **Code examples**: Look at demo/ directory
- **Issues**: Search existing issues before creating new ones
- **Discussions**: Use GitHub Discussions for questions

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
- **AI-first design**: Built specifically for AI agent integration
- **Cross-platform**: Works seamlessly on Windows, macOS, and Linux

Thank you for helping make weather data more accessible to AI applications! 🌤️