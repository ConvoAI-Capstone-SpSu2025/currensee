"""Financial news retrieval and analysis tools.

This module provides comprehensive financial news gathering capabilities for:
- Client industry news and company-specific information
- Macroeconomic events and market indicators  
- Client holdings and investment portfolio news
- Financial data summarization and analysis

Designed for enterprise-grade financial intelligence gathering.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, TypedDict
import pprint

import matplotlib.pyplot as plt
import pandas as pd
import pandas_datareader.data as web
from dateutil import parser as date_parser
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.messages import HumanMessage
from tabulate import tabulate

from currensee.agents.tools.base import SupervisorState
from currensee.core import get_model, settings

# === Model ===
model = get_model(settings.DEFAULT_MODEL)


# definitions


def format_google_date(date_obj):
    return date_obj.strftime("%Y%m%d")


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


keywords_client = [
    "announces",
    "acquires",
    "launches",
    "earnings",
    "report",
    "profit",
    "CEO",
    "crisis",
    "disaster",
    "recession",
    "recovery",
    "red flag",
    "urgent",
    "challenge",
    "emergency",
    "tumble",
    "drop",
    "opportunity",
    "slowdown",
]

keywords_econ = [
    "recovery",
    "crisis",
    "disaster",
    "recession",
    "red flag",
    "urgent",
    "challenge",
    "emergency",
    "tumble",
    "drop",
    "slowdown",
]

trusted_sources = [
    "reuters.com",
    "bloomberg.com",
    "cnn.com",
#    "forbes.com",
    "finance.yahoo.com",
    "marketwatch.com",
#    "morningstar.com",
    "WSJ.com",
#    "ft.com",
]

# Define trusted sources and search strategies
allowed_sites = trusted_sources

# Use individual site queries instead of complex OR filters to avoid URL encoding issues
def get_site_queries(base_query: str) -> List[str]:
    """Generate individual site-specific queries to avoid URL encoding issues with OR operators."""
    return [f"site:{site} {base_query}" for site in allowed_sites]

def aggregate_search_results(search: GoogleSerperAPIWrapper, queries: List[str], max_results_per_site: int = 5) -> List[Dict[str, Any]]:
    """Execute multiple queries and aggregate results with deduplication."""
    all_results = []
    seen_urls = set()
    
    for query in queries:
        try:
            results = search.results(query)
            organic_results = results.get("organic", [])
            
            # Add unique results from this site
            for result in organic_results[:max_results_per_site]:
                url = result.get("link", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    all_results.append(result)
                    
        except Exception as e:
            print(f"Warning: Query failed for '{query[:50]}...': {e}")
            continue
    
    return all_results

# Simple query templates (no complex OR operators)
query_mn_base = "news about relevant macro events and the economy"
query_ci_base = "news about {client_company} and about {industry} industry"
query_ch_base = "news about {holding}"


# =====tools=====



def retrieve_client_industry_news(state: SupervisorState) -> dict:
    """
    Return the most relevant news about the client and its industry.
    Uses robust multi-query approach with individual site searches.
    """
    
    # Enhanced date handling with fallback logic
    try:
        end_date = datetime.strptime(state["meeting_timestamp"], "%Y-%m-%d %H:%M:%S")
        if state.get("last_meeting_timestamp"):
            start_date = datetime.strptime(state["last_meeting_timestamp"], "%Y-%m-%d %H:%M:%S")
        else:
            start_date = end_date - timedelta(days=90)  # 90-day lookback for comprehensive news coverage
            print(f"INFO: Using 90-day lookback as last_meeting_timestamp not available")
    except (ValueError, KeyError) as e:
        print(f"ERROR: Invalid date format in state. Details: {e}")
        return state

    client_company = state["client_company"]
    industry = state["client_industry"]
    
    print(f"DEBUG: Filtering date range is from {start_date.date()} to {end_date.date()}")

    # --- Step 1: Use robust multi-query approach ---
    base_query = query_ci_base.format(client_company=client_company, industry=industry)
    queries = get_site_queries(base_query)
    
    print(f"DEBUG: Executing {len(queries)} site-specific queries for client industry news")
    
    search = GoogleSerperAPIWrapper()
    raw_results = aggregate_search_results(search, queries, max_results_per_site=8)
    
    print(f"DEBUG: Aggregated {len(raw_results)} unique results from all sites")
    
    # --- Step 2: Enhanced filtering with flexible date logic ---
    filtered_results = []
    
    for result in raw_results:
        # Enhanced scoring
        score = score_result(result)
        result["relevance_score"] = score
        
        # Check if from trusted source (should always be true with our approach)
        link = result.get("link", "")
        is_trusted = any(site in link for site in allowed_sites)
        
        # Enhanced date filtering with fallback handling
        result_date = None
        if "date" in result:
            try:
                if isinstance(result["date"], str):
                    result_date = date_parser.parse(result["date"]).replace(tzinfo=None)
                else:
                    result_date = result["date"]
            except (ValueError, TypeError) as e:
                print(f"DEBUG: Could not parse date '{result.get('date')}': {e}")
                # For articles without valid dates, include if high relevance score
                if score >= 4:
                    result_date = end_date  # Treat as recent
        
        # Flexible date filtering: include if within meeting window OR recent high-quality
        is_recent_or_relevant = False
        if result_date:
            is_within_window = start_date <= result_date <= end_date
            is_recent_quality = (end_date - timedelta(days=30)) <= result_date <= end_date and score >= 3
            is_recent_or_relevant = is_within_window or is_recent_quality
        elif score >= 5:  # Very high relevance, include even without date
            is_recent_or_relevant = True
        
        # Multi-tier filtering: prefer trusted + relevant, but include high-scoring articles
        if (is_trusted and is_recent_or_relevant) or score >= 5:
            filtered_results.append(result)
    
    # Sort by relevance score (highest first)
    filtered_results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    
    print(f"DEBUG: After filtering: {len(filtered_results)} articles remain")
    
    state["client_industry_sources"] = filtered_results
    return state



# Function to retrieve macroeconomic events news (Tool MACRO NEWS)
def retrieve_macro_news(state: SupervisorState) -> dict:
    """
    Return the most relevant macroeconomic news using robust multi-query approach.
    Avoids URL encoding issues by using individual site queries.
    """
    
    # Enhanced date handling with fallback logic
    try:
        end_date = datetime.strptime(state["meeting_timestamp"], "%Y-%m-%d %H:%M:%S")
        if state.get("last_meeting_timestamp"):
            start_date = datetime.strptime(state["last_meeting_timestamp"], "%Y-%m-%d %H:%M:%S")
        else:
            start_date = end_date - timedelta(days=180)  # 6-month lookback for macro context
            print(f"INFO: Using 180-day lookback for macro news")
    except (ValueError, KeyError) as e:
        print(f"ERROR: Invalid date format in state. Details: {e}")
        return state

    print(f"DEBUG: Filtering date range is from {start_date.date()} to {end_date.date()}")
    
    # --- Step 1: Use robust multi-query approach ---
    queries = get_site_queries(query_mn_base)
    
    print(f"DEBUG: Executing {len(queries)} site-specific queries for macro news")
    
    search = GoogleSerperAPIWrapper()
    raw_results = aggregate_search_results(search, queries, max_results_per_site=6)
    
    print(f"DEBUG: Aggregated {len(raw_results)} unique macro results from all sites")
    
    # --- Step 2: Enhanced filtering with flexible date logic ---
    filtered_results = []
    
    for result in raw_results:
        # Enhanced scoring
        score = score_result(result)
        result["relevance_score"] = score
        
        # Check if from trusted source (should always be true with our approach)
        link = result.get("link", "")
        is_trusted = any(site in link for site in allowed_sites)
        
        # Enhanced date filtering with fallback handling
        result_date = None
        if "date" in result:
            try:
                if isinstance(result["date"], str):
                    result_date = date_parser.parse(result["date"]).replace(tzinfo=None)
                else:
                    result_date = result["date"]
            except (ValueError, TypeError) as e:
                print(f"DEBUG: Could not parse date '{result.get('date')}': {e}")
                # For articles without valid dates, include if high relevance score
                if score >= 4:
                    result_date = end_date  # Treat as recent
        
        # Flexible date filtering: include if within meeting window OR recent high-quality
        is_recent_or_relevant = False
        if result_date:
            is_within_window = start_date <= result_date <= end_date
            is_recent_quality = (end_date - timedelta(days=60)) <= result_date <= end_date and score >= 3
            is_recent_or_relevant = is_within_window or is_recent_quality
        elif score >= 5:  # Very high relevance, include even without date
            is_recent_or_relevant = True
        
        # Multi-tier filtering: prefer trusted + relevant, but include high-scoring articles
        if (is_trusted and is_recent_or_relevant) or score >= 5:
            filtered_results.append(result)
    
    # Sort by relevance score (highest first)
    filtered_results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    
    print(f"DEBUG: After filtering: {len(filtered_results)} macro articles remain")
    
    state["macro_news_sources"] = filtered_results
    return state



def retrieve_holdings_news(state: SupervisorState) -> dict:
    """
    Return relevant news for client holdings using robust multi-query approach.
    Avoids URL encoding issues by using individual site queries per holding.
    """

    # Enhanced date handling with fallback logic
    try:
        end_date = datetime.strptime(state["meeting_timestamp"], "%Y-%m-%d %H:%M:%S")
        if state.get("last_meeting_timestamp"):
            start_date = datetime.strptime(state["last_meeting_timestamp"], "%Y-%m-%d %H:%M:%S")
        else:
            start_date = end_date - timedelta(days=60)  # 60-day lookback for holdings
            print(f"INFO: Using 60-day lookback for holdings news")
    except (ValueError, KeyError) as e:
        print(f"ERROR: Invalid date format in state. Details: {e}")
        return state

    print(f"DEBUG: Filtering date range is from {start_date.date()} to {end_date.date()}")

    holdings = state.get("client_holdings", [])
    search = GoogleSerperAPIWrapper()
    all_holdings_news = []

    for holding in holdings:
        print(f"DEBUG: Processing holding '{holding}'")
        
        # Use robust multi-query approach for each holding
        base_query = query_ch_base.format(holding=holding)
        queries = get_site_queries(base_query)
        
        print(f"DEBUG: Executing {len(queries)} site-specific queries for holding '{holding}'")
        
        # Get results for this holding
        raw_results = aggregate_search_results(search, queries, max_results_per_site=4)
        
        print(f"DEBUG: Aggregated {len(raw_results)} unique results for holding '{holding}'")
        
        # Enhanced filtering with flexible date logic
        filtered_results = []
        
        for result in raw_results:
            # Enhanced scoring
            score = score_result(result)
            result["relevance_score"] = score
            result["holding"] = holding  # Track which holding this is for
            
            # Check if from trusted source (should always be true with our approach)
            link = result.get("link", "")
            is_trusted = any(site in link for site in allowed_sites)
            
            # Enhanced date filtering with fallback handling
            result_date = None
            if "date" in result:
                try:
                    if isinstance(result["date"], str):
                        result_date = date_parser.parse(result["date"]).replace(tzinfo=None)
                    else:
                        result_date = result["date"]
                except (ValueError, TypeError) as e:
                    print(f"DEBUG: Could not parse date '{result.get('date')}': {e}")
                    # For articles without valid dates, include if high relevance score
                    if score >= 4:
                        result_date = end_date  # Treat as recent
            
            # Flexible date filtering: include if within meeting window OR recent high-quality
            is_recent_or_relevant = False
            if result_date:
                is_within_window = start_date <= result_date <= end_date
                is_recent_quality = (end_date - timedelta(days=45)) <= result_date <= end_date and score >= 3
                is_recent_or_relevant = is_within_window or is_recent_quality
            elif score >= 5:  # Very high relevance, include even without date
                is_recent_or_relevant = True
            
            # Multi-tier filtering: prefer trusted + relevant, but include high-scoring articles
            if (is_trusted and is_recent_or_relevant) or score >= 4:
                filtered_results.append(result)
        
        print(f"DEBUG: After filtering: {len(filtered_results)} articles for holding '{holding}'")
        
        # Add to overall results
        all_holdings_news.extend(filtered_results)
    
    # Sort all holdings news by relevance score (highest first)
    all_holdings_news.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    
    print(f"DEBUG: Total holdings news articles after all filtering: {len(all_holdings_news)}")
    
    state["client_holdings_sources"] = all_holdings_news
    return state


    
def summarize_finance_outputs(state: SupervisorState):
    """
    Summarizes the outputs from all provided tools into one coherent summary.
    Handles empty results gracefully to prevent pipeline crashes.

    Parameters:
    - state: SupervisorState with financial news outputs

    Returns:
    - Updated state with financial summary, even if some sources are empty
    """
    
    client_industry_output = state.get("client_industry_sources", [])
    client_holdings_output = state.get("client_holdings_sources", [])
    macro_finnews_output = state.get("macro_news_sources", [])
    
    # Enhanced robustness: check what data we actually have
    has_industry = isinstance(client_industry_output, list) and len(client_industry_output) > 0
    has_holdings = isinstance(client_holdings_output, list) and len(client_holdings_output) > 0
    has_macro = isinstance(macro_finnews_output, list) and len(macro_finnews_output) > 0
    
    print(f"DEBUG: Summarizer input - Industry: {len(client_industry_output) if has_industry else 0} articles")
    print(f"DEBUG: Summarizer input - Holdings: {len(client_holdings_output) if has_holdings else 0} articles")
    print(f"DEBUG: Summarizer input - Macro: {len(macro_finnews_output) if has_macro else 0} articles")
    
    # If we have NO data at all, provide a helpful fallback
    if not (has_industry or has_holdings or has_macro):
        fallback_summary = (
            "**Financial News Summary - Limited Data Available**\n\n"
            "Unfortunately, no recent financial news articles were found within the specified date range "
            "from our trusted news sources (Reuters, Bloomberg, CNN, Yahoo Finance, MarketWatch, WSJ). "
            "This could be due to:\n"
            "- Very recent meeting date with limited news coverage\n"
            "- Narrow date range between meetings\n"
            "- Technical issues with news retrieval\n\n"
            "**Recommendation:** Consider expanding the date range or checking alternative news sources "
            "for the most current market developments affecting the client's portfolio."
        )
        state["finnews_summary"] = fallback_summary
        return state
    
    # Build summary with available data
    summary_sections = []
    
    if has_industry:
        summary_sections.append(f"**Client Industry News ({len(client_industry_output)} articles):**\n{client_industry_output}")
    else:
        summary_sections.append("**Client Industry News:** No recent industry-specific news found.")
    
    if has_holdings:
        summary_sections.append(f"**Client Holdings News ({len(client_holdings_output)} articles):**\n{client_holdings_output}")
    else:
        summary_sections.append("**Client Holdings News:** No recent holdings-specific news found.")
    
    if has_macro:
        summary_sections.append(f"**Macroeconomic News ({len(macro_finnews_output)} articles):**\n{macro_finnews_output}")
    else:
        summary_sections.append("**Macroeconomic News:** No recent macro news found.")
    
    prompt = f"""
    Please provide a comprehensive but concise summary of the available financial news and insights:

    {chr(10).join(summary_sections)}

    **Instructions:**
    - Focus on the available data and clearly note any missing categories
    - Organize the summary into key themes and highlight important developments
    - Provide actionable insights and identify potential risks or opportunities
    - If data is limited, acknowledge this and focus on what IS available
    - Maintain professional tone suitable for client meeting preparation
    """
    
    try:
        messages = [HumanMessage(content=prompt)]
        result = model.invoke(messages)
        state["finnews_summary"] = result.content
    except Exception as e:
        print(f"ERROR: Summarization failed: {e}")
        # Provide basic fallback even if LLM fails
        basic_summary = f"""
        **Financial News Summary**
        
        Data Available:
        - Industry News: {len(client_industry_output) if has_industry else 0} articles
        - Holdings News: {len(client_holdings_output) if has_holdings else 0} articles  
        - Macro News: {len(macro_finnews_output) if has_macro else 0} articles
        
        Note: Automated summarization temporarily unavailable. Please review individual news items above.
        """
        state["finnews_summary"] = basic_summary
    
    return state


# MACRO TABLE


def generate_macro_table() -> str:
    """Fetch macroeconomic and market data from FRED and return a Markdown table."""

    def fetch_fred_latest(series_id):
        data = web.DataReader(series_id, "fred")
        return data

    def compute_percent_change(series, months):
        # Approximate months as 21 trading days per month
        offset = months * 21
        if len(series) <= offset:
            return None
        latest = series.iloc[-1]
        past = series.iloc[-offset]
        return round(((latest - past) / past) * 100, 2)

    def fetch_cpi_changes():
        cpi = fetch_fred_latest("CPIAUCSL")["CPIAUCSL"]
        return {
            "level": round(cpi.iloc[-1], 2),
            "1mo": compute_percent_change(cpi, 1),
            "3mo": compute_percent_change(cpi, 3),
            "6mo": compute_percent_change(cpi, 6),
            "1yr": compute_percent_change(cpi, 12),
            "2yr": compute_percent_change(cpi, 24),
        }

    # Fetch time series data for each FRED-supported indicator
    series_ids = {
        "S&P 500 Index": "SP500",
        "WTI Crude Oil Price": "DCOILWTICO",
        "US Dollar Index (Broad)": "DTWEXBGS",
    }

    series_data = {}
    for label, series_id in series_ids.items():
        try:
            data = fetch_fred_latest(series_id)[series_id].dropna()
            series_data[label] = {
                "level": round(data.iloc[-1], 2),
                "1mo": compute_percent_change(data, 1),
                "3mo": compute_percent_change(data, 3),
                "6mo": compute_percent_change(data, 6),
                "1yr": compute_percent_change(data, 12),
                "2yr": compute_percent_change(data, 24),
            }
        except Exception as e:
            print(f"Failed to fetch {label}: {e}")
            series_data[label] = {
                "level": None,
                "1mo": None,
                "3mo": None,
                "6mo": None,
                "1yr": None,
                "2yr": None,
            }

    cpi_data = fetch_cpi_changes()

    # Static latest values from FRED (single value series)
    static_indicators = {
        "US GDP Growth Rate": "A191RL1Q225SBEA",
        "US Unemployment Rate": "UNRATE",
        "10-Year Treasury Yield": "GS10",
        "Fed Funds Rate": "FEDFUNDS",
    }

    static_data = {}
    for label, sid in static_indicators.items():
        try:
            data = fetch_fred_latest(sid)
            static_data[label] = round(data.iloc[-1, 0], 2)
        except Exception as e:
            print(f"Failed to fetch {label}: {e}")
            static_data[label] = None

    # Build DataFrame
    df = pd.DataFrame(
        {
            "Indicator": [
                "S&P 500 Index",
                "WTI Crude Oil Price",
                "US Dollar Index (Broad)",
                "US CPI",
                "US GDP Growth Rate",
                "US Unemployment Rate",
                "10-Year Treasury Yield",
                "Fed Funds Rate",
            ],
            "Level": [
                series_data["S&P 500 Index"]["level"],
                series_data["WTI Crude Oil Price"]["level"],
                series_data["US Dollar Index (Broad)"]["level"],
                cpi_data["level"],
                static_data["US GDP Growth Rate"],
                static_data["US Unemployment Rate"],
                static_data["10-Year Treasury Yield"],
                static_data["Fed Funds Rate"],
            ],
            "1-Month Change (%)": [
                series_data["S&P 500 Index"]["1mo"],
                series_data["WTI Crude Oil Price"]["1mo"],
                series_data["US Dollar Index (Broad)"]["1mo"],
                cpi_data["1mo"],
                "",
                "",
                "",
                "",
            ],
            "3-Month Change (%)": [
                series_data["S&P 500 Index"]["3mo"],
                series_data["WTI Crude Oil Price"]["3mo"],
                series_data["US Dollar Index (Broad)"]["3mo"],
                cpi_data["3mo"],
                "",
                "",
                "",
                "",
            ],
            "6-Month Change (%)": [
                series_data["S&P 500 Index"]["6mo"],
                series_data["WTI Crude Oil Price"]["6mo"],
                series_data["US Dollar Index (Broad)"]["6mo"],
                cpi_data["6mo"],
                "",
                "",
                "",
                "",
            ],
            "1-Year Change (%)": [
                series_data["S&P 500 Index"]["1yr"],
                series_data["WTI Crude Oil Price"]["1yr"],
                series_data["US Dollar Index (Broad)"]["1yr"],
                cpi_data["1yr"],
                "",
                "",
                "",
                "",
            ],
            "2-Year Change (%)": [
                series_data["S&P 500 Index"]["2yr"],
                series_data["WTI Crude Oil Price"]["2yr"],
                series_data["US Dollar Index (Broad)"]["2yr"],
                cpi_data["2yr"],
                "",
                "",
                "",
                "",
            ],
        }
    )

    return df

    
