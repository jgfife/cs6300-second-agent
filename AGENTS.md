# Agent Development Guide

## Build/Test/Run Commands
- **Install dependencies**: `make install` (creates virtual environment and installs requirements)
- **Run investment research agent**: `python src/investment_research_agent.py`
- **Run tests**: `pytest tests/ -v` (requires `pip install -r requirements.txt`)

## Code Style Guidelines
- **Python version**: 3.12+ (see Makefile install-deb target)
- **Imports**: Standard library first, then third-party, then local (see existing code)
- **Classes**: Use type annotations for class attributes (e.g., `name: str = "calculator"`)
- **Functions**: Include docstrings with Args/Returns sections for public methods
- **Naming**: snake_case for variables/functions, PascalCase for classes
- **Environment**: Use `dotenv` for API keys, store in `.env` file
- **Error handling**: Use standard Python exceptions, no specific patterns observed

## Project Structure
- Main code in `src/` directory
- Tests in `tests/` directory with pytest framework
- Use virtual environment `.virtual_environment/`
- API keys: Store Gemini API key as `GEMINI_API_KEY` in `.env` file
- Dependencies managed via `requirements.txt`
- Logs stored in `logs/` directory with timestamped filenames

## Current Implementation
- **Investment Research Agent** (`src/investment_research_agent.py`): Main agent for answering investment-related questions
- **Web Search Tool** (`visit_webpage`): Custom tool for fetching and converting web content to markdown
- **Test Suite** (`tests/test_investment_research_agent.py`): Comprehensive tests including CEO identification
- **Interactive CLI**: Run agent interactively or import programmatically for testing

## Framework-Specific Notes  
- Uses `smolagents` framework with `OpenAIServerModel` for Gemini API compatibility
- Custom tools inherit from `smolagents.Tool` base class or use `@tool` decorator
- Agent types: `ToolCallingAgent` for search operations, `CodeAgent` for orchestration
- Agent initialization requires `tools`, `model`, and optional `additional_authorized_imports`
- Agents can be nested: `CodeAgent` can manage multiple `ToolCallingAgent` instances

## Testing Guidelines
- Tests use pytest framework with custom test discovery
- Mock external API calls for reliable unit tests when possible
- Integration tests verify real API functionality (require valid API keys)
- Test naming: `test_*` functions in `Test*` classes
- Use descriptive assertions with failure messages for better debugging