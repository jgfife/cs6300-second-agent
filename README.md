# Adventure Planning Agent

An AI-powered adventure planner that creates detailed trip itineraries by searching for activities, checking weather forecasts, and providing weather-aware recommendations for any destination.

## Features

- **Adventure Trip Planning**: Creates day-by-day itineraries for any destination and duration
- **Weather Integration**: Fetches real-time weather forecasts and adjusts recommendations accordingly
- **Smart Activity Search**: Finds adventure activities, attractions, and experiences tailored to your interests
- **ReAct Reasoning**: Uses step-by-step reasoning to gather information and create comprehensive plans
- **Web Research**: Searches and visits travel websites to gather detailed activity information
- **Weather-Aware Recommendations**: Suggests appropriate activities based on weather conditions and alerts to potential risks
- **Interactive CLI**: Chat-based interface with detailed planning output

## Quick Start

### 1. Setup Environment
```bash
# Install dependencies
make install

# Set up your Gemini API key
export GEMINI_API_KEY="your_api_key_here"
# Or create a .env file with: GEMINI_API_KEY=your_api_key_here
```

### 2. Run the Agent
```bash
# Interactive mode
python src/adventure_agent.py

# Example requests to try:
# - "Plan a 3-day hiking trip to Yosemite from June 15-17, 2024"
# - "Create a 5-day adventure itinerary for Costa Rica in December"
# - "What are the best outdoor activities in Chamonix for 2 days?"
```

### 3. Run Tests
```bash
# Run all tests
pytest tests/ -v

# Run specific test categories
pytest tests/test_adventure_agent.py::TestWeatherForecast -v
pytest tests/test_adventure_agent.py::TestAdventureSearch -v
```

## API Setup

### Gemini API Key (Required)
1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Click "Get API key" 
3. Create a new API key
4. Set it as `GEMINI_API_KEY` environment variable

### Weather Data (No API Key Required)
- Uses free Open-Meteo API for weather forecasts
- Includes automatic geocoding for location coordinates

### Supported Models
- Primary: `gemini-2.5-flash` (configured in code)
- API Base: `https://generativelanguage.googleapis.com/v1beta/openai/`
- Compatibility: Uses OpenAI-compatible API format

## Project Structure

```
cs6300-second-agent/
├── src/
│   └── adventure_agent.py              # Main adventure planning agent
├── tests/
│   └── test_adventure_agent.py         # Test suite for adventure planning
├── requirements.txt                    # Dependencies (includes beautifulsoup4, python-dotenv)
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

- **adventure_planner (ToolCallingAgent)**: Main ReAct agent that orchestrates the planning process
- **adventure_search**: Custom tool for finding destination-specific activities and itineraries
- **visit_webpage**: Enhanced webpage content extraction with HTML cleaning
- **get_weather_forecast**: Weather data retrieval using Open-Meteo API with geocoding
- **DuckDuckGoSearchTool**: Built-in web search functionality

### ReAct Reasoning Flow
1. **Search**: Find activities and attractions for the destination
2. **Research**: Visit relevant websites to gather detailed information
3. **Weather Check**: Get forecast for travel dates
4. **Analysis**: Consider weather impact on activities
5. **Synthesis**: Create comprehensive itinerary with weather-appropriate recommendations

## Tools & APIs

### Adventure Search Tool
- Builds targeted search queries based on destination, activities, and trip duration
- Integrates with DuckDuckGo for comprehensive results
- Handles various activity types (hiking, climbing, water sports, etc.)

### Weather Forecast Tool
- Free Open-Meteo API integration (no API key required)
- Automatic geocoding for any location worldwide
- Provides temperature, precipitation, and weather condition codes
- Returns JSON-formatted forecasts for easy processing

### Web Content Extraction
- BeautifulSoup-powered HTML cleaning
- Removes navigation, ads, and non-content elements
- Handles large pages with intelligent truncation
- Robust error handling for failed requests

## Testing

The test suite verifies:
- ✅ Adventure search query generation and results processing
- ✅ Weather forecast retrieval and JSON formatting
- ✅ Webpage content extraction and cleaning
- ✅ Error handling for network failures and invalid inputs
- ✅ Weather relevance logic for activity recommendations
- ✅ Agent initialization and tool integration

## Example Output

```
## Itinerary
Day 1: Cable car to Aiguille du Midi, glacier viewing
Day 2: Hiking Lac Blanc trail, village exploration

## Weather Summary
Partly cloudy, 15-18°C highs, light rain possible Day 2

## Gear Recommendations
- Rain jacket for Day 2 afternoon
- Hiking boots for mountain trails
- Layers for temperature variation

## Sources
- https://adventurebackpack.com/chamonix-itinerary
- https://www.earthtrekkers.com/best-things-to-do-in-chamonix/
```

## Development

Built with:
- **smolagents**: Hugging Face agent framework with ReAct reasoning
- **Google Gemini**: LLM backend via OpenAI-compatible API
- **Open-Meteo**: Free weather API service
- **DuckDuckGo**: Web search capabilities
- **BeautifulSoup**: HTML parsing and content extraction
- **pytest**: Testing framework with mocking
