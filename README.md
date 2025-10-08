# Investment Research Agent

An AI-powered investment research assistant built with Hugging Face smolagents, Alphavantage, and Google Gemini.

## Disclaimer: This is a toy agent and should not be relied upon for actual investment advice!

## Features

- **Investment-focused Q&A**: Answers questions about companies, stocks, and financial topics
- **Web search capabilities**: Uses DuckDuckGo search and webpage content extraction
- **CEO identification**: Accurately identifies company leadership (tested with Apple/Tim Cook)
- **Interactive CLI**: Chat-based interface with conversation logging
- **Comprehensive testing**: Full test suite with pytest framework

## Quick Start

### 1. Setup Environment
```bash
# Install dependencies
pip install -r requirements.txt

# Set up your Gemini API and Alphavantage key
export GEMINI_API_KEY="your_api_key_here"
export ALPHAVANTAGE_API_KEY="your_api_key_here"
# Or create a .env file with: GEMINI_API_KEY=your_api_key_here

# Alternatively you can run make commands
make install # install dependencies
```
### 2. Run the Agent
```bash
# Interactive mode
python src/investment_research_agent.py

# Alternatively you can run make commands
make research-agent # start phoenix server for open telemetry and run main agent

# Example questions to try:
# - "Who is the CEO of Apple?"
# - "What is Tesla's stock ticker symbol?"
# - "Tell me about Microsoft's recent earnings"

# Once done, cleanup the Phoenix server
make kill-phoenix
```

### 3. Run Tests
```bash
# Run all tests
pytest tests/ -v

# Run just the CEO test
pytest tests/test_investment_research_agent.py::TestInvestmentResearchAgent::test_apple_ceo_question -v

# Alternatively you can run make commands
make test # run tests
```

## API Setup

### Gemini API Key
1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Click "Get API key" 
3. Create a new API key
4. Set it as `GEMINI_API_KEY` environment variable

### Alphavantage API Key
1. Visit [Alphavantage Website](https://www.alphavantage.co/support/#api-key)
2. Fill out form
2. Click "GET FREE API KEY" 
4. Set it as `ALPHAVANTAGE_API_KEY` environment variable

### Supported Models
- Primary: `gemini-2.5-flash` (configured in code)
- API Base: `https://generativelanguage.googleapis.com/v1beta/openai/`
- Compatibility: Uses OpenAI-compatible API format

## Project Structure

```
cs6300-first-agent/
├── src/
│   └── investment_research_agent.py    # Main agent implementation
├── tests/
│   ├── test_investment_research_agent.py # Test suite
│   └── README.md                        # Testing documentation
├── requirements.txt                     # Dependencies
├── pytest.ini                         # Test configuration
├── Makefile                            # Build and run commands
├── .env.template                       # Environment variables template
└── README.md                           # This file
```

## Phoenix Server - Open Telemetry

This project integrates with Phoenix Server for comprehensive observability and tracing of agent interactions. Phoenix provides real-time monitoring of:

- Agent conversation flows
- Tool usage and performance
- API call traces and latency
- Error tracking and debugging

### Accessing Phoenix Dashboard

When running the agent with `make research-agent`, the Phoenix server automatically starts in the background. You can access the observability dashboard at:

**http://localhost:6006/projects/**

The dashboard provides:
- Real-time trace visualization
- Performance metrics
- Conversation history
- Tool usage analytics
- Error logs and debugging information

### Phoenix Server Management

```bash
# Start agent with Phoenix server
make research-agent

# Stop Phoenix server when done
make kill-phoenix
```

The Phoenix server runs headlessly in the background, allowing full interaction with the agent while collecting telemetry data.

## Architecture

- **jefe (CodeAgent)**: Main orchestrator that manages sub-agents and handles user queries
- **seeker (ToolCallingAgent)**: Specialized search agent with web search, page visit, and API calling capabilities
- **DuckDuckGoSearchTool**: Built-in search functionality

## Testing

The test suite verifies:
- ✅ Correct CEO identification (Tim Cook for Apple)
- ✅ Stock ticker symbol retrieval (AAPL for Apple) 
- ✅ Investment question handling
- ✅ Non-investment question rejection
- ✅ Ticker symbol tool functionality
- ✅ Company overview tool functionality

See `tests/README.md` for detailed testing documentation.

## Development

Built with:
- **smolagents**: Hugging Face agent framework
- **Google Gemini**: LLM backend via OpenAI-compatible API
- **DuckDuckGo**: Web search capabilities
- **pytest**: Testing framework
- **Alphavantage API**: Company data API
