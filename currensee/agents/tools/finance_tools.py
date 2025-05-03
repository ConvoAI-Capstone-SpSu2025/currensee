from typing import TypedDict, List, Dict, Any, Optional
from langchain_community.utilities import GoogleSerperAPIWrapper

import matplotlib.pyplot as plt

from currensee.agents.tools.base import SupervisorState


class FinNewsState(TypedDict):

    client_company: str

    client_industry: str

    client_holdings: list[str]

    start_date: str
    
    end_date: str

    # Response generation
    macro_news_summary: Optional[str]
    client_industry_summary: Optional[str]
    client_holdings_summary: Optional[str]
    complete_summary: Optional[str]

    # Processing metadata
    messages: List[Dict[str, Any]]  # Track conversation with LLM for analysis


#definitions

def format_google_date(date_str):
    parts = date_str.split("/")
    return f"{parts[2]}{parts[0].zfill(2)}{parts[1].zfill(2)}"

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
query_ci = "{site_filter} news about {client_company} and about {industry} industry"

# Query for holdings
query_ch = "{site_filter} news about any of these top holdings:{largest_holdings}"


#=====tools=====

def retrieve_client_industry_news(state: SupervisorState) -> str:
    """Return the most relevant news about the client and its industry."""

    print("GETTING CLIENT INDUSTRY")

    start_date = state["start_date"]
    end_date = state["end_date"]
    client_company = state["client_company"]
    industry = state["client_industry"]

    google_start = format_google_date(start_date)
    google_end = format_google_date(end_date)

    sort_param = f"date:r:{google_start}:{google_end}"  # Google's date range format

    # Search with date filter
    search = GoogleSerperAPIWrapper(k=30, sort=sort_param)  # Pass sort parameter
    filled_query = query_ci.format(site_filter=site_filter, client_company=client_company, industry=industry)
    results = search.results(filled_query)

    if results.get("organic"):
        sorted_results_client = sorted(results.get("organic", []), key=score_result, reverse=True)
        industry_summary = sorted_results_client
    else:
        industry_summary = "No results found for client or industry news."

    new_state = state.copy()
    new_state['client_industry_summary'] = industry_summary

    print(new_state.keys())

    return new_state


# Function to retrieve macroeconomic events news (Tool MACRO NEWS)
def retrieve_macro_news(state: SupervisorState) -> str:
    """Return the most relevant macroeconomic news based on the query."""

    print("GETTING MACRO")

    start_date = state["start_date"]
    end_date = state["end_date"]

    google_start = format_google_date(start_date)
    google_end = format_google_date(end_date)

    sort_param = f"date:r:{google_start}:{google_end}"

    search = GoogleSerperAPIWrapper(k=30, sort=sort_param)  # Pass sort parameter
    filled_query = query_mn.format(site_filter=site_filter)
    results = search.results(filled_query)

    if results.get("organic"):
        sorted_results_econ = sorted(results.get("organic", []), key=score_result, reverse=True)
        macro_summary = sorted_results_econ
    else:
        macro_summary = "No results found for macroeconomic events."

    new_state = state.copy()
    new_state['macro_news_summary'] = macro_summary

    print(new_state.keys())

    return new_state

# Function to retrieve macroeconomic events news (Tool HOLDINGS NEWS)
def retrieve_holdings_news(state: SupervisorState) -> str:
    """Return the most relevant news based on each major holding of a specific client."""

    start_date = state["start_date"]
    end_date = state["end_date"]
    client_holdings = state["client_holdings"]

    google_start = format_google_date(start_date)
    google_end = format_google_date(end_date)

    sort_param = f"date:r:{google_start}:{google_end}"

    search = GoogleSerperAPIWrapper(k=30, sort=sort_param)  # Pass sort parameter
    filled_query = query_ch.format(site_filter=site_filter, largest_holdings=client_holdings)
    results = search.results(filled_query)

    if results.get("organic"):
        sorted_results_econ = sorted(results.get("organic", []), key=score_result, reverse=True)
        holdings_summary = sorted_results_econ
    else:
        holdings_summary = "No results found for holdings."

    new_state = state.copy()
    new_state['client_holdings_summary'] = holdings_summary

    print(new_state.keys())

    return new_state


