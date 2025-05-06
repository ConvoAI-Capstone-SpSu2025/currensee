from typing import TypedDict, List, Dict, Any, Optional
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.messages import HumanMessage

import matplotlib.pyplot as plt

from currensee.core import get_model, settings
from currensee.agents.tools.base import SupervisorState
import pandas_datareader.data as web
import yfinance as yf
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
def retrieve_holdings_news(state: SupervisorState) -> str:
    """Return the most relevant news based on each major holding of a specific client."""

    start_date = state["meeting_timestamp"]
    end_date = state["last_meeting_timestamp"]
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


def generate_macro_table() -> str:
    """Fetch macroeconomic data and return it as a Markdown-style table string."""

    def fetch_fred_data(series_id):
        data = web.DataReader(series_id, 'fred')
        return round(data.iloc[-1, 0], 2)

    def fetch_cpi_levels():
        cpi = web.DataReader('CPIAUCSL', 'fred')
        latest = cpi.iloc[-1, 0]
        one_month_ago = cpi.iloc[-2, 0]
        three_months_ago = cpi.iloc[-4, 0]
        six_months_ago = cpi.iloc[-7, 0]
        one_year_ago = cpi.iloc[-13, 0]
        two_years_ago = cpi.iloc[-25, 0]
        return {
            'level': round(latest, 2),
            '1mo': round(((latest - one_month_ago) / one_month_ago) * 100, 2),
            '3mo': round(((latest - three_months_ago) / three_months_ago) * 100, 2),
            '6mo': round(((latest - six_months_ago) / six_months_ago) * 100, 2),
            '1yr': round(((latest - one_year_ago) / one_year_ago) * 100, 2),
            '2yr': round(((latest - two_years_ago) / two_years_ago) * 100, 2)
        }

    def fetch_yf_data(ticker, period='1d', interval='1d'):
        data = yf.download(ticker, period=period, interval=interval)
        return float(round(data['Close'].iloc[-1], 2))

    def fetch_yf_change(ticker, period):
        data = yf.download(ticker, period=period, interval='1d')
        start = data['Close'].iloc[0]
        end = data['Close'].iloc[-1]
        return float(round(((end - start) / start) * 100, 2))

    indicators = {
        "S&P 500": {"fetch_func": fetch_yf_data, "source": "^GSPC"},
        "NASDAQ": {"fetch_func": fetch_yf_data, "source": "^IXIC"},
        "WTI Crude Oil Price": {"fetch_func": fetch_yf_data, "source": "CL=F"},
        "US GDP Growth Rate": {"fetch_func": fetch_fred_data, "source": "A191RL1Q225SBEA"},
        "US Unemployment Rate": {"fetch_func": fetch_fred_data, "source": "UNRATE"},
        "10-Year Treasury Yield": {"fetch_func": fetch_fred_data, "source": "GS10"},
        "Fed Funds Rate": {"fetch_func": fetch_fred_data, "source": "FEDFUNDS"},
        "US Dollar Index (DXY)": {"fetch_func": fetch_yf_data, "source": "DX-Y.NYB"},
    }

    data = {}
    for indicator, details in indicators.items():
        func = details["fetch_func"]
        source = details.get("source")
        value = func(source)
        data[indicator] = value

    cpi_data = fetch_cpi_levels()

    for ticker, label in {
        "^GSPC": "S&P 500",
        "^IXIC": "NASDAQ",
        "CL=F": "WTI Crude Oil Price",
        "DX-Y.NYB": "US Dollar Index (DXY)"
    }.items():
        for period, tag in [('1mo', '1-Month'), ('3mo', '3-Month'), ('6mo', '6-Month'), ('1y', '1-Year'), ('2y', '2-Year')]:
            data[f"{label} {tag} Change (%)"] = fetch_yf_change(ticker, period)

    df_macrofin = pd.DataFrame({
        'Indicator': [
            'S&P 500',
            'NASDAQ',
            'WTI Crude Oil Price',
            'US CPI',
            'US Dollar Index (DXY)',
            'US GDP Growth Rate',
            'US Unemployment Rate',
            '10-Year Treasury Yield',
            'Fed Funds Rate'
        ],
        'Level': [
            data['S&P 500'],
            data['NASDAQ'],
            data['WTI Crude Oil Price'],
            cpi_data['level'],
            data['US Dollar Index (DXY)'],
            data['US GDP Growth Rate'],
            data['US Unemployment Rate'],
            data['10-Year Treasury Yield'],
            data['Fed Funds Rate']
        ],
        '1-Month Change (%)': [
            data['S&P 500 1-Month Change (%)'],
            data['NASDAQ 1-Month Change (%)'],
            data['WTI Crude Oil Price 1-Month Change (%)'],
            cpi_data['1mo'],
            data['US Dollar Index (DXY) 1-Month Change (%)'],
            '', '', '', ''
        ],
        '3-Month Change (%)': [
            data['S&P 500 3-Month Change (%)'],
            data['NASDAQ 3-Month Change (%)'],
            data['WTI Crude Oil Price 3-Month Change (%)'],
            cpi_data['3mo'],
            data['US Dollar Index (DXY) 3-Month Change (%)'],
            '', '', '', ''
        ],
        '6-Month Change (%)': [
            data['S&P 500 6-Month Change (%)'],
            data['NASDAQ 6-Month Change (%)'],
            data['WTI Crude Oil Price 6-Month Change (%)'],
            cpi_data['6mo'],
            data['US Dollar Index (DXY) 6-Month Change (%)'],
            '', '', '', ''
        ],
        '1-Year Change (%)': [
            data['S&P 500 1-Year Change (%)'],
            data['NASDAQ 1-Year Change (%)'],
            data['WTI Crude Oil Price 1-Year Change (%)'],
            cpi_data['1yr'],
            data['US Dollar Index (DXY) 1-Year Change (%)'],
            '', '', '', ''
        ],
        '2-Year Change (%)': [
            data['S&P 500 2-Year Change (%)'],
            data['NASDAQ 2-Year Change (%)'],
            data['WTI Crude Oil Price 2-Year Change (%)'],
            cpi_data['2yr'],
            data['US Dollar Index (DXY) 2-Year Change (%)'],
            '', '', '', ''
        ]
    })

    df_macrofin.set_index('Indicator', inplace=True)
    return tabulate(df_macrofin.reset_index(), headers="keys", tablefmt="github")
