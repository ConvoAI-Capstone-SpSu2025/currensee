from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent
from langchain_core.runnables import RunnableLambda
from langchain.tools import tool
from langchain_community.utilities import GoogleSerperAPIWrapper
import os
import pprint
from currensee.core import get_model, settings
from dotenv import load_dotenv
import pandas_datareader.data as web
from datetime import datetime, timedelta

import matplotlib.pyplot as plt

from currensee.agents.agent_utils import summarize_outputs, query_tool


#definitions

keywords_client = ["announces", "acquires", "launches", "earnings", "report", 
               "profit", "CEO", "crisis", "disaster","recession","recovery", "red flag", 
               "urgent","challenge","emergency", "tumble","drop","opportunity","slowdown"]

keywords_econ = ["recovery","crisis", "disaster","recession","red flag", 
               "urgent","challenge","emergency", "tumble","drop","slowdown"]

trusted_sources = ["reuters.com", "bloomberg.com", "cnn.com", "forbes.com", 
                "finance.yahoo.com","marketwatch.com","morningstar.com", "https://www.wsj.com","www.ft.com"]

# Define trusted sources
allowed_sites = trusted_sources
site_filter = " OR ".join(f"site:{site}" for site in allowed_sites)

# Query for macroeconomic events
query_mn = "{site_filter} news about relevant macro events and the economy."

# Query for stock market and industry-related news
query_ci = "{site_filter} news about {client_name} and about {industry} industry"

# Query for holdings
query_ch = "{site_filter} news about any of these top holdings:{largest_holdings}"


#=====tools=====

@tool
def client_and_industry(client_name: str, industry: str, site_filter: str = site_filter) -> str:
    """Return the most relevant news about the client and its industry."""
    def format_google_date(date_str):
        parts = date_str.split("/")
        return f"{parts[2]}{parts[0].zfill(2)}{parts[1].zfill(2)}"

    google_start = format_google_date(start_date)
    google_end = format_google_date(end_date)

    sort_param = f"date:r:{google_start}:{google_end}"  # Google's date range format

    # Search with date filter
    search = GoogleSerperAPIWrapper(k=30, sort=sort_param)  # Pass sort parameter
    filled_query = query_ci.format(site_filter=site_filter, client_name=client_name, industry=industry)
    results = search.results(filled_query)

    def score_result(result):
        score = 0
        keywords = keywords_client  # Assume this variable is defined elsewhere
        link = result.get("link", "")
        title = result.get("title", "").lower()
        snippet = result.get("snippet", "").lower()

        if any(site in link for site in allowed_sites):
            score += 3

        if any(word in title or word in snippet for word in keywords):
            score += 2

        if "date" in result:
            score += 1

        return score

    if results.get("organic"):
        sorted_results_client = sorted(results.get("organic", []), key=score_result, reverse=True)
        return sorted_results_client
    else:
        return "No results found for client or industry news."



# Function to retrieve macroeconomic events news (Tool MACRO NEWS)
@tool
def macro_news(site_filter: str = site_filter) -> str:
    """Return the most relevant macroeconomic news based on the query."""
    def format_google_date(date_str):
        parts = date_str.split("/")
        return f"{parts[2]}{parts[0].zfill(2)}{parts[1].zfill(2)}"

    google_start = format_google_date(start_date)
    google_end = format_google_date(end_date)

    sort_param = f"date:r:{google_start}:{google_end}"

    search = GoogleSerperAPIWrapper(k=30, sort=sort_param)  # Pass sort parameter
    filled_query = query_mn.format(site_filter=site_filter)
    results = search.results(filled_query)

    def score_result(result):
        score = 0
        keywords = keywords_econ  # Assume this variable is defined elsewhere
        link = result.get("link", "")
        title = result.get("title", "").lower()
        snippet = result.get("snippet", "").lower()

        if any(site in link for site in allowed_sites):
            score += 3

        if any(word in title or word in snippet for word in keywords):
            score += 2

        if "date" in result:
            score += 1

        return score

    if results.get("organic"):
        sorted_results_econ = sorted(results.get("organic", []), key=score_result, reverse=True)
        return sorted_results_econ
    else:
        return "No results found for macroeconomic events."



# Function to retrieve macroeconomic events news (Tool HOLDINGS NEWS)
@tool
def holdings_news(largest_holdings: list[str], site_filter: str = site_filter) -> str:
    """Return the most relevant news based on each major holding."""
    def format_google_date(date_str):
        parts = date_str.split("/")
        return f"{parts[2]}{parts[0].zfill(2)}{parts[1].zfill(2)}"

    google_start = format_google_date(start_date)
    google_end = format_google_date(end_date)

    sort_param = f"date:r:{google_start}:{google_end}"

    search = GoogleSerperAPIWrapper(k=30, sort=sort_param)  # Pass sort parameter
    filled_query = query_hn.format(site_filter=site_filter, largest_holdings=largest_holdings)
    results = search.results(filled_query)

    def score_result(result):
        score = 0
        keywords = keywords_client
        link = result.get("link", "")
        title = result.get("title", "").lower()
        snippet = result.get("snippet", "").lower()

        if any(site in link for site in allowed_sites):
            score += 3

        if any(word in title or word in snippet for word in keywords):
            score += 2

        if "date" in result:
            score += 1

        return score

    if results.get("organic"):
        sorted_results_econ = sorted(results.get("organic", []), key=score_result, reverse=True)
        return sorted_results_econ
    else:
        return "No results found for holdings."


