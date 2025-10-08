#!/usr/bin/env python3

import requests
import dotenv
import os
import json
import re
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List
from requests.exceptions import RequestException
from smolagents import (
    ToolCallingAgent,
    OpenAIServerModel,
    DuckDuckGoSearchTool,
    tool
)
from phoenix.otel import register
from openinference.instrumentation.smolagents import SmolagentsInstrumentor
from bs4 import BeautifulSoup

dotenv.load_dotenv()
register()
SmolagentsInstrumentor().instrument()

@tool
def adventure_search(destination: str, activities: Optional[str] = None, days: int = 3) -> str:
    """Searches for adventure and travel activities in a given destination.

    Args:
        destination: The destination to search for adventures (e.g., "Chamonix", "Costa Rica")
        activities: Optional specific activities to focus on (e.g., "hiking", "climbing", "water sports")
        days: Number of days for the trip to tailor results

    Returns:
        Search results as formatted text with URLs and descriptions
    """
    try:
        # Build targeted search query
        activity_terms = activities if activities else "adventure activities outdoor"
        query_parts = [destination, activity_terms]
        
        if days > 1:
            query_parts.append(f"{days} day itinerary")
        
        query_parts.extend(["travel guide", "things to do"])
        search_query = " ".join(query_parts)
        
        # Use DuckDuckGo search
        search_tool = DuckDuckGoSearchTool()
        results = search_tool(search_query)
        
        return f"Search results for '{search_query}':\n{results}"
        
    except Exception as e:
        return f"Error performing adventure search: {str(e)}"

@tool
def visit_webpage(url: str) -> str:
    """Visits a webpage at the given URL and returns clean text content.

    Args:
        url: The URL of the webpage to visit.

    Returns:
        The clean text content of the webpage, or an error message if the request fails.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML and extract clean text
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get text and clean it up
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Truncate if too long
        if len(clean_text) > 5000:
            clean_text = clean_text[:5000] + "... [truncated]"
        
        return clean_text

    except RequestException as e:
        return f"Error fetching the webpage: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

@tool
def get_weather_forecast(location: str, start_date: str, end_date: str) -> str:
    """Gets historical weather data for a location and date range.

    Args:
        location: The location name (e.g., "Chamonix, France")
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        Historical weather data as JSON string with temperature, precipitation, and conditions
    """
    try:
        start = datetime.fromisoformat(start_date).date()
        end = datetime.fromisoformat(end_date).date()
    except ValueError:
        return "Error: Dates must be in YYYY-MM-DD format."

    try:
        if end < start:
            return "Error: end_date must be on or after start_date."

        requested_start = start
        requested_end = end

        today = datetime.now(timezone.utc).date()
        if start > today:
            return "Error: Historical data is only available for dates up to today."

        if end > today:
            end = today

        normalized_start = start.strftime("%Y-%m-%d")
        normalized_end = end.strftime("%Y-%m-%d")

        def generate_location_candidates(raw_location: str) -> List[str]:
            cleaned = re.sub(r"\s+", " ", raw_location).strip()
            candidates: List[str] = []

            if cleaned:
                candidates.append(cleaned)

            no_parentheses = re.sub(r"\([^)]*\)", "", cleaned).strip()
            if no_parentheses and no_parentheses not in candidates:
                candidates.append(no_parentheses)

            has_comma = ',' in no_parentheses
            comma_parts = [part.strip() for part in no_parentheses.split(',') if part.strip()] if has_comma else []

            if comma_parts:
                first = comma_parts[0]
                if first and first not in candidates:
                    candidates.append(first)

                if len(comma_parts) >= 2:
                    primary_last = f"{comma_parts[0]}, {comma_parts[-1]}"
                    if primary_last not in candidates:
                        candidates.append(primary_last)
            else:
                words = [word for word in no_parentheses.split(' ') if word]
                if words:
                    first_word = words[0]
                    if first_word and first_word not in candidates:
                        candidates.append(first_word)

                    if len(words) >= 2:
                        synthesized = f"{words[0]}, {words[-1]}"
                        if synthesized not in candidates:
                            candidates.append(synthesized)

            return candidates

        def geocode(candidate: str) -> Optional[Dict[str, Any]]:
            geocode_url = "https://geocoding-api.open-meteo.com/v1/search"
            response = requests.get(
                geocode_url,
                params={"name": candidate, "count": 5},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            results = data.get('results') or []
            return results[0] if results else None

        geo_result: Optional[Dict[str, Any]] = None
        last_error: Optional[Exception] = None

        for candidate in generate_location_candidates(location):
            try:
                geo_result = geocode(candidate)
                if geo_result:
                    break
            except RequestException as geo_exc:
                last_error = geo_exc
                continue
            except Exception as geo_exc:  # pragma: no cover - unexpected but handled gracefully
                last_error = geo_exc
                continue

        if not geo_result:
            if last_error:
                return f"Error fetching geocoding data: {str(last_error)}"
            return f"Error: Could not find coordinates for location: {location}"

        lat = geo_result['latitude']
        lon = geo_result['longitude']
        
        # Get historical weather data
        weather_url = "https://archive-api.open-meteo.com/v1/archive"
        daily_metrics = [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "precipitation_hours",
            "weathercode",
            "windspeed_10m_max",
            "windgusts_10m_max",
        ]
        weather_params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": normalized_start,
            "end_date": normalized_end,
            "daily": ",".join(daily_metrics),
            "timezone": "auto",
        }

        weather_response = requests.get(weather_url, params=weather_params, timeout=10)
        weather_response.raise_for_status()
        weather_data = weather_response.json()
        
        # Process and format the weather data
        daily_data = weather_data.get('daily', {})
        dates = daily_data.get('time', [])

        if not dates:
            return "Error: No historical weather data available for the requested dates."

        def safe_daily_value(key: str, index: int, default: Optional[Any] = None) -> Optional[Any]:
            values = daily_data.get(key)
            if isinstance(values, list) and index < len(values):
                return values[index]
            return default

        def safe_daily_any(keys: List[str], index: int, default: Optional[Any] = None) -> Optional[Any]:
            for key in keys:
                value = safe_daily_value(key, index, None)
                if value is not None:
                    return value
            return default

        country = geo_result.get('country') or geo_result.get('country_code', '') or ''
        location_label = f"{geo_result.get('name', location)}, {country}".strip(', ')

        forecast_summary = {
            'location': location_label,
            'coordinates': {'lat': lat, 'lon': lon},
            'resolved_query': geo_result.get('name'),
            'original_query': location,
            'data_type': 'historical',
            'date_range': {
                'requested': {
                    'start_date': requested_start.strftime("%Y-%m-%d"),
                    'end_date': requested_end.strftime("%Y-%m-%d"),
                },
                'resolved': {
                    'start_date': normalized_start,
                    'end_date': normalized_end,
                },
            },
            'forecast': []
        }
        
        for i, date in enumerate(dates):
            day_forecast = {
                'date': date,
                'temp_max': safe_daily_value('temperature_2m_max', i),
                'temp_min': safe_daily_value('temperature_2m_min', i),
                'precipitation_sum': safe_daily_value('precipitation_sum', i),
                'precipitation_hours': safe_daily_value('precipitation_hours', i),
                'precipitation_probability': safe_daily_any(['precipitation_probability_mean', 'precipitation_probability_max'], i),
                'weather_code': safe_daily_any(['weathercode', 'weather_code'], i),
                'wind_speed_max': safe_daily_value('windspeed_10m_max', i),
                'wind_gusts_max': safe_daily_value('windgusts_10m_max', i),
            }
            forecast_summary['forecast'].append(day_forecast)
        
        return json.dumps(forecast_summary, indent=2)
        
    except RequestException as e:
        return f"Error fetching weather data: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

model_id="gemini-2.5-flash"
model = OpenAIServerModel(model_id=model_id,
                          api_base="https://generativelanguage.googleapis.com/v1beta/openai/",
                          api_key=os.getenv("GEMINI_API_KEY"),
                          )

adventure_planner = ToolCallingAgent(
    tools=[DuckDuckGoSearchTool(), adventure_search, visit_webpage, get_weather_forecast],
    model=model,
    max_steps=8,
    name="adventure_planner",
    description="Plans adventure trips by searching for activities, checking weather, and creating itineraries.",
    instructions="""You are an expert adventure travel planner that creates detailed trip itineraries.

    Use ReAct reasoning to:
    1. Search for adventure activities and attractions in the destination
    2. Visit relevant webpages to gather detailed information about activities
    3. Check weather forecasts for the travel dates
    4. Create a day-by-day itinerary that considers weather conditions
    5. Recommend appropriate gear and preparations
    
    Always include:
    - Day-by-day activity recommendations
    - Weather summary and how it affects activities
    - Source URLs for all recommendations
    - Gear/preparation suggestions based on activities and weather
    
    Consider weather when planning:
    - Avoid exposed outdoor activities during storms or severe weather
    - Suggest indoor alternatives when weather is poor
    - Recommend weather-appropriate activities
    
    Format your final response with clear sections: Itinerary, Weather Summary, Gear Recommendations, and Sources."""
)

def main():
    """Interactive CLI for the adventure planning agent."""
    print("Adventure Planning Agent")
    print("========================")
    print("Ask me to plan your next adventure! Include destination, dates, and preferred activities.")
    print("Example: 'Plan a 5-day hiking trip to Patagonia from March 15-20, 2024'")
    print("Type 'exit', 'quit', or 'q' to quit.\n")
    
    while True:
        try:
            question = input("Where would you like to adventure? ")
            if question.lower() in ['exit', 'quit', 'q']:
                print("Happy travels!")
                break
            
            answer = adventure_planner.run(question)
            print(f"\n{answer}\n")

        except KeyboardInterrupt:
            print("\nHappy travels!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            continue

if __name__ == "__main__":
    main()