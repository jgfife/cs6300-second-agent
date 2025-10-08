#!/usr/bin/env python3

import requests
import dotenv
import os
from requests.exceptions import RequestException
from smolagents import (
    CodeAgent,
    ToolCallingAgent,
    OpenAIServerModel,
    DuckDuckGoSearchTool,
    tool
)
from phoenix.otel import register
from openinference.instrumentation.smolagents import SmolagentsInstrumentor

dotenv.load_dotenv()
register()
SmolagentsInstrumentor().instrument()

@tool
def visit_webpage(url: str) -> str:
    """Visits a webpage at the given URL and returns its content as text.

    Args:
        url: The URL of the webpage to visit.

    Returns:
        The content of the webpage, or an error message if the request fails.
    """
    try:
        # Send a GET request to the URL with proper headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes

        return response.text

    except RequestException as e:
        return f"Error fetching the webpage: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

# Call Alphavantage API for company-to-ticker lookups https://www.alphavantage.co/documentation/#symbolsearch
@tool
def find_ticker_symbol(company: str) -> str:
    """Calls the Alphavantage API and returns the ticker symbol search results for the given company as a json string.

    Args:
        company: The name of the company to retrieve the ticker symbol for.

    Returns:
        The API content as a json string, or an error message if the request fails.
    """
    try:
        url = f"https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={company}&apikey={os.getenv('ALPHAVANTAGE_API_KEY')}"
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes

        return response.json()

    except RequestException as e:
        return f"Error fetching the webpage: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

# Call Alphavantage API for company info https://www.alphavantage.co/documentation/#company-overview
@tool
def get_company_overview(symbol: str) -> str:
    """Calls the Alphavantage API and returns company overview content as json string.

    Args:
        symbol: The stock symbol of the company to retrieve information for.

    Returns:
        The API content as a json string, or an error message if the request fails.
    """
    try:
        url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={os.getenv('ALPHAVANTAGE_API_KEY')}"
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes

        return response.json()

    except RequestException as e:
        return f"Error fetching the webpage: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

model_id="gemini-2.5-flash"
model = OpenAIServerModel(model_id=model_id,
                          api_base="https://generativelanguage.googleapis.com/v1beta/openai/",
                          api_key=os.getenv("GEMINI_API_KEY"),
                          )

seeker = ToolCallingAgent(
    tools=[DuckDuckGoSearchTool(), visit_webpage, get_company_overview, find_ticker_symbol],
    model=model,
    max_steps=3,
    name="search_agent",
    description="Runs web searches and calls APIs for investment information for you.",
    instructions="You are a helpful research assistant that can search the web, visit webpages, and call APIs to gather information about investment-related topics. You respond with a concise summary of the information you pages you visit.",
)

jefe = CodeAgent(
    tools=[],
    model=model,
    managed_agents=[seeker],
    additional_authorized_imports=["time", "numpy", "pandas"],
    name="jefe",
    description="Orchestrating agent that uses sub-agents to research investment-related questions.",
    instructions="You are a helpful research assistant that can only answer investment-related questions and visit webpages that pertain to the queried company to gather information. You always include your sources in your response. If the question is not investment-related, respond with 'I can only answer investment-related questions.'",
)

def main():
    """Interactive CLI for the investment research agent."""
    while True:
        try:
            question = input("How can I help you? ")
            if question.lower() in ['exit', 'quit', 'q']:
                print("Goodbye!")
                break
            
            answer = jefe.run(question)
            print(answer)

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            continue

if __name__ == "__main__":
    main()