from typing import TypedDict, List, Dict, Any, Optional
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.messages import HumanMessage

import matplotlib.pyplot as plt

from currensee.core import get_model, settings
from currensee.agents.tools.base import SupervisorState
import pandas_datareader.data as web
#import yfinance as yf
import pandas as pd
from tabulate import tabulate


# === Model ===
model = get_model(settings.DEFAULT_MODEL)


#definitions

def format_google_date(date_str):
    
    parts = date_str.split()[0].split("-")
    return f"{parts[0]}{parts[1].zfill(2)}{parts[0].zfill(2)}"

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

    start_date = state["meeting_timestamp"]
    end_date = state["last_meeting_timestamp"]
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


    return new_state


# Function to retrieve macroeconomic events news (Tool MACRO NEWS)
def retrieve_macro_news(state: SupervisorState) -> str:
    """Return the most relevant macroeconomic news based on the query."""

    start_date = state["meeting_timestamp"]
    end_date = state["last_meeting_timestamp"]

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

    return new_state

# Function to retrieve macroeconomic events news (Tool HOLDINGS NEWS)
# def retrieve_holdings_news(state: SupervisorState) -> str:
#     """Return the most relevant news based on each position. Focus on what are the key things that have happened in those names. Do not search for funds and their holdings."""

#     start_date = state["meeting_timestamp"]
#     end_date = state["last_meeting_timestamp"]
#     client_holdings = state["client_holdings"]

#     google_start = format_google_date(start_date)
#     google_end = format_google_date(end_date)

#     sort_param = f"date:r:{google_start}:{google_end}"

#     search = GoogleSerperAPIWrapper(k=30, sort=sort_param)  # Pass sort parameter
#     filled_query = query_ch.format(site_filter=site_filter, largest_holdings=client_holdings)
#     results = search.results(filled_query)

#     if results.get("organic"):
#         sorted_results_econ = sorted(results.get("organic", []), key=score_result, reverse=True)
#         holdings_summary = sorted_results_econ
#     else:
#         holdings_summary = "No results found for holdings."

#     new_state = state.copy()
#     new_state['client_holdings_summary'] = holdings_summary

#     return new_state

def retrieve_holdings_news(state: SupervisorState) -> str:
    """Return a concatenated summary of relevant news for each holding separately. Make the summary long."""

    start_date = state["meeting_timestamp"]
    end_date = state["last_meeting_timestamp"]
    client_holdings = state["client_holdings"]

    google_start = format_google_date(start_date)
    google_end = format_google_date(end_date)
    sort_param = f"date:r:{google_start}:{google_end}"

    search = GoogleSerperAPIWrapper(k=30, sort=sort_param)  # Serper search instance

    holdings_summary = ""  # Final concatenated summary

    for holding in client_holdings:
        # Fill in query template for each holding individually
        filled_query = query_ch.format(site_filter=site_filter, largest_holdings=holding)

        results = search.results(filled_query)

        if results.get("organic"):
            sorted_results = sorted(results["organic"], key=score_result, reverse=True)
            summary = sorted_results
        else:
            summary = f"No news found for {holding}.\n"

        holdings_summary += f"\n### Summary for {holding}:\n{summary}\n"

    new_state = state.copy()
    new_state["client_holdings_summary"] = holdings_summary

    return new_state    





    
def summarize_finance_outputs(state: SupervisorState) -> str:
    """
    Summarizes the outputs from all provided tools into one coherent summary.
    
    Parameters:
    - tool_outputs: A list of strings (outputs from different tools)
    
    Returns:
    - A summarized string with key points from all the tool outputs.
    """

    client_industry_output = state["client_industry_summary"]
    client_holdings_output = state["client_holdings_summary"]
    macro_finnews_output = state["macro_news_summary"]

    # Combine all outputs into a formatted prompt
    combined_prompt = "\n\n".join(
        [f"Tool {i+1} Output:\n{output}" for i, output in enumerate([client_industry_output, client_holdings_output, macro_finnews_output])]
    )
    combined_prompt += "\n\nPlease summarize the key points from all the outputs into one concise, long summary. Include specific numbers where applicable."
    
    # Create the messages to pass to the model
    messages = [
        HumanMessage(content=combined_prompt)
    ]
    
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
        data = web.DataReader(series_id, 'fred')
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
        cpi = fetch_fred_latest('CPIAUCSL')['CPIAUCSL']
        return {
            'level': round(cpi.iloc[-1], 2),
            '1mo': compute_percent_change(cpi, 1),
            '3mo': compute_percent_change(cpi, 3),
            '6mo': compute_percent_change(cpi, 6),
            '1yr': compute_percent_change(cpi, 12),
            '2yr': compute_percent_change(cpi, 24)
        }

    # Fetch time series data for each FRED-supported indicator
    series_ids = {
        'S&P 500 Index': 'SP500',
        'WTI Crude Oil Price': 'DCOILWTICO',
        'US Dollar Index (Broad)': 'DTWEXBGS'
    }

    series_data = {}
    for label, series_id in series_ids.items():
        try:
            data = fetch_fred_latest(series_id)[series_id].dropna()
            series_data[label] = {
                'level': round(data.iloc[-1], 2),
                '1mo': compute_percent_change(data, 1),
                '3mo': compute_percent_change(data, 3),
                '6mo': compute_percent_change(data, 6),
                '1yr': compute_percent_change(data, 12),
                '2yr': compute_percent_change(data, 24)
            }
        except Exception as e:
            print(f"Failed to fetch {label}: {e}")
            series_data[label] = {'level': None, '1mo': None, '3mo': None, '6mo': None, '1yr': None, '2yr': None}

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
    df = pd.DataFrame({
        'Indicator': [
            'S&P 500 Index',
            'WTI Crude Oil Price',
            'US Dollar Index (Broad)',
            'US CPI',
            'US GDP Growth Rate',
            'US Unemployment Rate',
            '10-Year Treasury Yield',
            'Fed Funds Rate'
        ],
        'Level': [
            series_data['S&P 500 Index']['level'],
            series_data['WTI Crude Oil Price']['level'],
            series_data['US Dollar Index (Broad)']['level'],
            cpi_data['level'],
            static_data['US GDP Growth Rate'],
            static_data['US Unemployment Rate'],
            static_data['10-Year Treasury Yield'],
            static_data['Fed Funds Rate']
        ],
        '1-Month Change (%)': [
            series_data['S&P 500 Index']['1mo'],
            series_data['WTI Crude Oil Price']['1mo'],
            series_data['US Dollar Index (Broad)']['1mo'],
            cpi_data['1mo'],
            '', '', '', ''
        ],
        '3-Month Change (%)': [
            series_data['S&P 500 Index']['3mo'],
            series_data['WTI Crude Oil Price']['3mo'],
            series_data['US Dollar Index (Broad)']['3mo'],
            cpi_data['3mo'],
            '', '', '', ''
        ],
        '6-Month Change (%)': [
            series_data['S&P 500 Index']['6mo'],
            series_data['WTI Crude Oil Price']['6mo'],
            series_data['US Dollar Index (Broad)']['6mo'],
            cpi_data['6mo'],
            '', '', '', ''
        ],
        '1-Year Change (%)': [
            series_data['S&P 500 Index']['1yr'],
            series_data['WTI Crude Oil Price']['1yr'],
            series_data['US Dollar Index (Broad)']['1yr'],
            cpi_data['1yr'],
            '', '', '', ''
        ],
        '2-Year Change (%)': [
            series_data['S&P 500 Index']['2yr'],
            series_data['WTI Crude Oil Price']['2yr'],
            series_data['US Dollar Index (Broad)']['2yr'],
            cpi_data['2yr'],
            '', '', '', ''
        ]
    })

    df.set_index('Indicator', inplace=True)
    return tabulate(df.reset_index(), headers="keys", tablefmt="github")