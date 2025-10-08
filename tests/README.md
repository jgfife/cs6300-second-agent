# Testing the Investment Research Agent

This directory contains tests for the investment research agent.

## Setup

1. Make sure you have installed all dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up your Gemini API key:
   ```bash
   export GEMINI_API_KEY="your_api_key_here"
   ```
   Or create a `.env` file with:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

## Running Tests

### Option 1: Using pytest (recommended)
```bash
pytest tests/ -v
```

### Option 2: Run specific test
```bash
pytest tests/test_investment_research_agent.py::TestInvestmentResearchAgent::test_apple_ceo_question -v
```

## Test Details

The main test (`test_apple_ceo_question`) verifies that:
1. The agent correctly identifies Tim Cook as Apple's CEO
2. The response mentions "CEO" or "Chief Executive"
3. The agent provides a coherent answer to investment-related questions

Additional tests verify:
- The agent can answer other investment questions (stock ticker symbols)
- The agent rejects non-investment related questions

## Notes

- Tests make real API calls to Gemini and web searches
- Tests require an active internet connection
- Response times may vary based on web search results
- The agent's responses may vary slightly but should consistently identify Tim Cook as Apple's CEO