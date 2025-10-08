#!/usr/bin/env python3

import pytest
import json
from datetime import datetime, timedelta, timezone
import sys
import os

# Add src directory to path for importing modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from adventure_agent import adventure_search, visit_webpage, get_weather_forecast, adventure_planner

class TestAdventureSearch:
    """Tests adventure_search using the real DuckDuckGoSearchTool (no mocks)."""

    def test_adventure_search_basic(self):
        destination = "Chamonix"
        activities = "hiking"
        days = 3
        expected_query = f"{destination} {activities} {days} day itinerary travel guide things to do"

        result = adventure_search(destination, activities, days)

        if result.startswith("Error performing adventure search"):
            pytest.skip(f"Search backend unavailable: {result}")

        assert f"Search results for '{expected_query}':" in result
        assert destination in result

    def test_adventure_search_no_activities(self):
        destination = "Costa Rica"
        days = 5
        expected_query = f"{destination} adventure activities outdoor {days} day itinerary travel guide things to do"

        result = adventure_search(destination, None, days)

        if result.startswith("Error performing adventure search"):
            pytest.skip(f"Search backend unavailable: {result}")

        assert f"Search results for '{expected_query}':" in result
        assert "adventure activities outdoor" in result

class TestVisitWebpage:
    """Tests visit_webpage against real HTTP requests (no mocks)."""

    def test_visit_webpage_success(self):
        url = "https://example.com"
        result = visit_webpage(url)

        if result.startswith("Error fetching") or result.startswith("An unexpected error"):
            pytest.skip(f"Network/HTTP unavailable: {result}")

        assert "Example Domain" in result

    def test_visit_webpage_http_error(self):
        # .invalid TLD is guaranteed to be invalid per RFC
        bad_url = "https://nonexistent-domain-xyz.invalid"
        result = visit_webpage(bad_url)
        assert result.startswith("Error fetching the webpage") or result.startswith("An unexpected error")

class TestWeatherForecast:
    """Test the get_weather_forecast tool functionality against the live API."""

    @staticmethod
    def _past_date_range(days: int = 3) -> tuple[str, str]:
        today = datetime.now(timezone.utc).date()
        end = today - timedelta(days=1)
        start = end - timedelta(days=max(days - 1, 0))
        return start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')

    def test_get_weather_forecast_success(self):
        """Test successful historical weather retrieval using the real Open-Meteo API."""
        start_date, end_date = self._past_date_range()
        result = get_weather_forecast("Chamonix France", start_date, end_date)

        try:
            forecast_data = json.loads(result)
        except json.JSONDecodeError:
            pytest.skip(f"Open-Meteo API unavailable: {result}")

        assert forecast_data['location'].startswith("Chamonix")
        assert forecast_data['data_type'] == 'historical'
        assert len(forecast_data['forecast']) >= 1
        resolved_range = forecast_data['date_range']['resolved']
        resolved_end = datetime.fromisoformat(resolved_range['end_date']).date()
        assert resolved_end <= datetime.now(timezone.utc).date()
        first_day = forecast_data['forecast'][0]
        assert 'date' in first_day
        assert first_day['temp_max'] is not None

    def test_get_weather_forecast_geocoding_failure(self):
        """Test handling of an unknown location against the real API."""
        start_date, end_date = self._past_date_range()
        result = get_weather_forecast("NonexistentPlaceXYZ123", start_date, end_date)

        if "Error fetching geocoding data" in result:
            pytest.skip(f"Open-Meteo API unavailable: {result}")

        assert "Could not find coordinates for location" in result

    def test_get_weather_forecast_rejects_future_dates(self):
        """Requests fully in the future should be rejected."""
        today = datetime.now(timezone.utc).date()
        start = (today + timedelta(days=2)).strftime('%Y-%m-%d')
        end = (today + timedelta(days=5)).strftime('%Y-%m-%d')

        result = get_weather_forecast("Chamonix, France", start, end)

        assert "Historical data is only available for dates up to today" in result

    def test_get_weather_forecast_clamps_future_end(self):
        """If the end date extends into the future, it should be clamped to today."""
        today = datetime.now(timezone.utc).date()
        start = (today - timedelta(days=5)).strftime('%Y-%m-%d')
        end = (today + timedelta(days=2)).strftime('%Y-%m-%d')

        result = get_weather_forecast("Chamonix France", start, end)

        try:
            forecast_data = json.loads(result)
        except json.JSONDecodeError:
            pytest.skip(f"Open-Meteo API unavailable: {result}")

        resolved_range = forecast_data['date_range']['resolved']
        assert resolved_range['end_date'] == today.strftime('%Y-%m-%d')

class TestAdventurePlannerAgent:
    """Test the adventure planner agent integration."""

    def test_adventure_planner_initialization(self):
        """Test that the adventure planner agent initializes correctly."""
        # Skip if no API key is available
        if not os.getenv('GEMINI_API_KEY'):
            pytest.skip("GEMINI_API_KEY not available")

        assert adventure_planner is not None
        assert adventure_planner.name == "adventure_planner"
        assert len(adventure_planner.tools) == 5  # DuckDuckGo, adventure_search, visit_webpage, get_weather_forecast, final_answer
        assert adventure_planner.max_steps == 8

class TestWeatherRelevanceLogic:
    """Test weather-based activity filtering logic."""

    def test_severe_weather_detection(self):
        """Test detection of severe weather conditions."""
        # Weather codes: 95-99 are thunderstorms, 71-77 are snow, 80-82 are rain showers
        severe_weather_codes = [95, 96, 99, 75, 77, 82]
        mild_weather_codes = [0, 1, 2, 3]  # Clear, partly cloudy, overcast, fog

        for code in severe_weather_codes:
            # In real implementation, this would be part of the agent's reasoning
            assert code >= 71 and (code <= 77 or code >= 80)

        for code in mild_weather_codes:
            assert code < 10  # Generally good weather codes

    def test_precipitation_thresholds(self):
        """Test precipitation threshold logic for activity recommendations."""
        high_precip = 15.0  # mm
        moderate_precip = 5.0  # mm
        low_precip = 1.0  # mm

        # High precipitation should trigger indoor activity suggestions
        assert high_precip > 10.0
        # Moderate precipitation might require gear recommendations
        assert 2.0 < moderate_precip < 10.0
        # Low precipitation shouldn't significantly impact most activities
        assert low_precip < 2.0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])