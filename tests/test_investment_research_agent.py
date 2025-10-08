#!/usr/bin/env python3

import pytest
import os
import sys
from pathlib import Path

# Add the src directory to the Python path so we can import the agent
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from investment_research_agent import jefe


class TestInvestmentResearchAgent:
    """Test suite for the investment research agent."""
    
    def test_apple_ceo_question(self):
        """Test that the agent correctly identifies Tim Cook as Apple's CEO"""
        question = "Who is the CEO of Apple?"
        
        # Run the agent
        answer = jefe.run(question)
        
        # Convert answer to string if it's not already
        answer_str = str(answer).lower()
        
        # Verify Tim Cook is mentioned in the response
        assert "tim cook" in answer_str, f"Expected 'Tim Cook' in response but got: {answer}"
        
        # Verify CEO or Chief Executive is mentioned
        ceo_mentioned = ("ceo" in answer_str or 
                        "chief executive" in answer_str or 
                        "chief executive officer" in answer_str)
        assert ceo_mentioned, f"Expected CEO/Chief Executive reference but got: {answer}"
        
    def test_agent_responds_to_investment_questions(self):
        """Test that the agent can handle general investment questions"""
        question = "What is Apple's stock ticker symbol?"
        
        # Run the agent
        answer = jefe.run(question)
        
        # Convert answer to string if it's not already
        answer_str = str(answer).lower()
        
        # Should mention AAPL
        assert "aapl" in answer_str, f"Expected 'AAPL' in response but got: {answer}"
        
    def test_non_investment_question_rejection(self):
        """Test that the agent rejects non-investment questions"""
        question = "What is the weather today?"
        
        # Run the agent
        answer = jefe.run(question)
        
        # Convert answer to string if it's not already
        answer_str = str(answer).lower()
        
        # Should reject non-investment questions
        rejection_phrases = [
            "i can only answer investment-related questions",
            "investment-related",
            "not investment-related"
        ]
        
        rejected = any(phrase in answer_str for phrase in rejection_phrases)
        assert rejected, f"Expected rejection of non-investment question but got: {answer}"
        
    def test_find_ticker_symbol_tool(self):
        """Test that the find_ticker_symbol tool works correctly"""
        from investment_research_agent import find_ticker_symbol
        
        # Test with a well-known company
        company = "Apple"
        
        # Call the tool directly
        result = find_ticker_symbol(company)
        
        # Convert result to string if it's not already
        result_str = str(result).lower()
        
        # Check that we don't get an error message
        assert "error" not in result_str, f"Expected successful API call but got error: {result}"
        
        # For a valid API response, we should get JSON-like content
        # The Alphavantage API returns bestMatches array
        assert "bestmatches" in result_str or "bestMatches" in str(result), f"Expected ticker search results but got: {result}"
        
    def test_find_ticker_symbol_handles_invalid_input(self):
        """Test that the find_ticker_symbol tool handles invalid input gracefully"""
        from investment_research_agent import find_ticker_symbol
        
        # Test with empty or nonsensical input
        result = find_ticker_symbol("")
        
        # Should either return empty results or handle gracefully
        # The exact behavior depends on the API response
        assert result is not None, "Expected some response even for empty input"
        
    def test_get_company_overview_tool(self):
        """Test that the get_company_overview tool works correctly"""
        from investment_research_agent import get_company_overview
        
        # Test with a well-known ticker symbol
        symbol = "AAPL"
        
        # Call the tool directly
        result = get_company_overview(symbol)
        
        # Convert result to string if it's not already
        result_str = str(result).lower()
        
        # Check that we don't get an error message
        assert "error" not in result_str, f"Expected successful API call but got error: {result}"
        
        # For a valid company overview, we should get company info
        # The Alphavantage API returns company details like Name, Symbol, etc.
        expected_fields = ["symbol", "name", "description"]
        field_found = any(field in result_str for field in expected_fields)
        assert field_found, f"Expected company overview data but got: {result}"
        
    def test_get_company_overview_handles_invalid_symbol(self):
        """Test that the get_company_overview tool handles invalid symbols gracefully"""
        from investment_research_agent import get_company_overview
        
        # Test with invalid ticker symbol
        result = get_company_overview("INVALID123")
        
        # Should either return empty results or handle gracefully
        # The exact behavior depends on the API response
        assert result is not None, "Expected some response even for invalid symbol"


if __name__ == "__main__":
    # Check for API key before running tests
    if not os.getenv("GEMINI_API_KEY"):
        print("Warning: GEMINI_API_KEY not found in environment variables")
        print("Make sure to set it in your .env file or environment")
    
    pytest.main([__file__, "-v"])