from typing import Any, Dict, List, Optional, TypedDict

import matplotlib.pyplot as plt
# import yfinance as yf
import pandas as pd
import pandas_datareader.data as web
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.messages import HumanMessage
from tabulate import tabulate
from datetime import datetime
from dateutil import parser as date_parser
import pprint

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

# Define trusted sources
allowed_sites = trusted_sources
site_filter = "(" + " OR ".join(f"site:{site}" for site in allowed_sites) + ")"


# Query for macroeconomic events
query_mn = "{site_filter} news about relevant macro events and the economy"

# Query for stock market and industry-related news
query_ci = "{site_filter} news about {client_company} and about {industry} industry"

# Query for holdings
query_ch = "{site_filter} news about any of these top holdings:{largest_holdings}"


# =====tools=====



def retrieve_client_industry_news(state: SupervisorState) -> dict:
    """
    Return the most relevant news about the client and its industry.
    It performs a broad search and then filters by date and trusted sources.
    """
    
    try:
        start_date = datetime.strptime(state["last_meeting_timestamp"], "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(state["meeting_timestamp"], "%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        print(f"ERROR: Invalid date format in state. Details: {e}")
        return state

    
    client_company = state["client_company"]
    industry = state["client_industry"]
    
    print(f"DEBUG: Filtering date range is from {start_date.date()} to {end_date.date()}")

    # --- Step 1: Perform the simplest possible API search ---
    filled_query = query_ci.format(site_filter= "site_filter", client_company=client_company, industry=industry)
    print(f"DEBUG: Sending query to API: '{filled_query}'")
    
    search = GoogleSerperAPIWrapper(k=30)
    results = search.results(filled_query)

    print("\nDEBUG: --- Raw API Results (before filtering) ---")
    pprint.pprint(results.get("organic"))
    print("--------------------------------------------------\n")

    # --- Step 2: Manually filter the results (filters: dates)---
    filtered_results = []
    if results.get("organic"):
        for result in results["organic"]:
            date_str = result.get("date")
            link = result.get("link", "")

            
            
            # Check if the result is from an allowed site
            is_from_trusted_source = any(site in link for site in allowed_sites)

            #check date
            is_within_date_range = False
            if date_str:
                try:
                    article_date = date_parser.parse(date_str, fuzzy=True)
                    if start_date <= article_date <= end_date:
                        is_within_date_range = True
                except (TypeError, ValueError):
                    # Skip results without a proper date
                    continue

            
            if is_from_trusted_source and is_within_date_range:
                filtered_results.append(result)

    print(f"DEBUG: Found {len(filtered_results)} articles after filtering.")
    
    # --- Step 3: Sort & update state ---
    sorted_results_client = sorted(filtered_results, key=score_result, reverse=True)
    new_state = state.copy()
    new_state["client_industry_sources"] = sorted_results_client or "No relevant news in date range."

    return new_state



# Function to retrieve macroeconomic events news (Tool MACRO NEWS)
def retrieve_macro_news(state: SupervisorState) -> dict:
    """
    Return the most relevant macroeconomic news based on the query.
    Filters by date range and trusted sources.
    """

    try:
        start_date = datetime.strptime(state["last_meeting_timestamp"], "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(state["meeting_timestamp"], "%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        print(f"ERROR: Invalid date format in state. Details: {e}")
        return state

    print(f"DEBUG: Filtering macro news from {start_date.date()} to {end_date.date()}")


    google_start = format_google_date(start_date)
    google_end = format_google_date(end_date)
    sort_param = f"date:r:{google_start}:{google_end}"

    # --- Step 1: Query all API ---
    filled_query = query_mn.format(site_filter="site_filter")
    print(f"DEBUG: Sending macro query to API: '{filled_query}'")

    search = GoogleSerperAPIWrapper(k=30)
    results = search.results(filled_query)

    print("\nDEBUG: --- Raw Macro API Results (before filtering) ---")
    pprint.pprint(results.get("organic"))
    print("--------------------------------------------------------\n")

    #--- Step 2: Filter by trusted sources and date range ---
    filtered_results = []
    if results.get("organic"):
        for result in results["organic"]:
            date_str = result.get("date")
            link = result.get("link", "")

            is_from_trusted_source = any(site in link for site in allowed_sites)
            is_within_date_range = False

            if date_str:
                try:
                    article_date = date_parser.parse(date_str, fuzzy=True)
                    if start_date <= article_date <= end_date:
                        is_within_date_range = True
                except (TypeError, ValueError):
                    continue

            if is_from_trusted_source and is_within_date_range:
                filtered_results.append(result)

    print(f"DEBUG: Found {len(filtered_results)} macro articles after filtering.")

    sorted_results_macro = sorted(filtered_results, key=score_result, reverse=True)
    new_state = state.copy()
    new_state["macro_news_sources"] = sorted_results_macro or "No relevant macro news in date range."

    return new_state



def retrieve_holdings_news(state: SupervisorState) -> dict:
    """
    Return a raw list of relevant news dictionaries for each holding.
    Filters by date range and trusted sources.
    """

    try:
        start_date = datetime.strptime(state["last_meeting_timestamp"], "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(state["meeting_timestamp"], "%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        print(f"ERROR: Invalid date format in state. Details: {e}")
        return state

    print(f"DEBUG: Filtering date range is from {start_date.date()} to {end_date.date()}")

    holdings = state.get("client_holdings", [])
    search = GoogleSerperAPIWrapper(k=30)
    holdings_news = {}

    for holding in holdings:
        query = query_ch.format(site_filter="site_filter", largest_holdings=holding)
        print(f"DEBUG: Sending query for holding '{holding}': '{query}'")

        results = search.results(query)

        print(f"\nDEBUG: --- Raw API Results for '{holding}' ---")
        pprint.pprint(results.get("organic"))
        print("------------------------------------------------\n")

        filtered_results = []
        if results.get("organic"):
            for result in results["organic"]:
                date_str = result.get("date")
                link = result.get("link", "")

                # Check source
                is_trusted = any(site in link for site in allowed_sites)

                # Check date
                is_within_date_range = False
                if date_str:
                    try:
                        parsed_date = date_parser.parse(date_str, fuzzy=True)
                        if start_date <= parsed_date <= end_date:
                            is_within_date_range = True
                    except (ValueError, TypeError):
                        continue

                if is_trusted and is_within_date_range:
                    filtered_results.append(result)

        print(f"DEBUG: Found {len(filtered_results)} articles for holding '{holding}' after filtering.")

        sorted_results = sorted(filtered_results, key=score_result, reverse=True)

        holdings_news[holding] = [
            {
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "snippet": item.get("snippet", ""),
                "date": item.get("date", ""),
                "position": i + 1,
            }
            for i, item in enumerate(sorted_results)
        ] or "No relevant news in date range."

    new_state = state.copy()
    new_state["client_holdings_sources"] = holdings_news

    return new_state


    
def summarize_finance_outputs(state: SupervisorState) -> str:
    """
    Summarizes the outputs from all provided tools into one coherent summary.

    Parameters:
    - tool_outputs: A list of strings (outputs from different tools)

    Returns:
    - A summarized string with key points from all the tool outputs.
    """

    client_industry_output = state["client_industry_sources"]
    client_holdings_output = state["client_holdings_sources"]
    macro_finnews_output = state["macro_news_sources"]

    # Define what counts as "no results"
    no_result_markers = [None, "", "No relevant news in date range.", "No relevant macro news in date range."]

    # Check for missing or empty outputs
    if any(
        output in no_result_markers
        or (isinstance(output, (list, dict)) and len(output) == 0)
        for output in [client_industry_output, client_holdings_output, macro_finnews_output]
    ):
        raise ValueError("One or more finance tool outputs are empty or missing. Cannot summarize.")

    
    # Combine all outputs into a formatted prompt
    combined_prompt = "\n\n".join(
        [
            f"Tool {i+1} Output:\n{output}"
            for i, output in enumerate(
                [client_industry_output, client_holdings_output, macro_finnews_output]
            )
        ]
    )
    combined_prompt += "\n\nPlease summarize the key points from all the outputs into one concise, long summary. Include specific numbers where applicable."

    # Create the messages to pass to the model
    messages = [HumanMessage(content=combined_prompt)]

    # Use the 'invoke' method for summarization
    summary = model.invoke(messages)

    new_state = state.copy()
    new_state["finnews_summary"] = summary.content

    # Access the message content correctly
    return new_state

    


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

    
