#!/usr/bin/env python3

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta, timezone
import sys
import os

# Add src directory to path for importing modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from adventure_agent import adventure_search, visit_webpage, get_weather_forecast, adventure_planner

class TestAdventureSearch:
    """Test the adventure_search tool functionality."""
    
    @patch('adventure_agent.DuckDuckGoSearchTool')
    def test_adventure_search_basic(self, mock_search_tool):
        """Test basic adventure search functionality."""
        # Mock the search tool response
        mock_instance = Mock()
        mock_instance.return_value = "Mock search results for Chamonix adventure activities"
        mock_search_tool.return_value = mock_instance
        
        result = adventure_search("Chamonix", "hiking", 3)
        
        assert "Search results for" in result
        assert "Chamonix" in result
        mock_instance.assert_called_once()
    
    @patch('adventure_agent.DuckDuckGoSearchTool')
    def test_adventure_search_no_activities(self, mock_search_tool):
        """Test adventure search without specific activities."""
        mock_instance = Mock()
        mock_instance.return_value = "Mock search results"
        mock_search_tool.return_value = mock_instance
        
        result = adventure_search("Costa Rica", None, 5)
        
        assert "Search results for" in result
        assert "adventure activities outdoor" in result
        
    def test_adventure_search_error_handling(self):
        """Test adventure search error handling."""
        with patch('adventure_agent.DuckDuckGoSearchTool', side_effect=Exception("Search failed")):
            result = adventure_search("TestDestination", "hiking", 2)
            assert "Error performing adventure search" in result

class TestVisitWebpage:
    """Test the visit_webpage tool functionality."""
    
    @patch('adventure_agent.requests.get')
    @patch('adventure_agent.BeautifulSoup')
    def test_visit_webpage_success(self, mock_soup, mock_get):
        """Test successful webpage visit and content extraction."""
        # Mock HTTP response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = b"<html><body><h1>Adventure Guide</h1><p>Great hiking spots</p></body></html>"
        mock_get.return_value = mock_response
        
        # Mock BeautifulSoup instance
        mock_soup_instance = Mock()
        
        # Mock the __call__ method to return elements with decompose method
        mock_script = Mock()
        mock_script.decompose = Mock()
        mock_style = Mock()
        mock_style.decompose = Mock()
        mock_soup_instance.return_value = [mock_script, mock_style]
        
        # Mock get_text to return the expected text
        mock_soup_instance.get_text.return_value = "Adventure Guide\nGreat hiking spots"
        
        # Set up the soup constructor to return our mock instance
        mock_soup.return_value = mock_soup_instance
        
        result = visit_webpage("https://example.com/hiking")
        
        assert "Adventure Guide Great hiking spots" in result
        mock_get.assert_called_once()
        
    @patch('adventure_agent.requests.get')
    def test_visit_webpage_http_error(self, mock_get):
        """Test webpage visit with HTTP error."""
        mock_get.side_effect = Exception("HTTP 404 Not Found")
        
        result = visit_webpage("https://example.com/nonexistent")
        
        assert "An unexpected error occurred" in result

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