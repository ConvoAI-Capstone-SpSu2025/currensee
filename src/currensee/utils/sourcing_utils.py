import re
from textwrap import wrap
from typing import Any, Dict, List, Optional, TypedDict

import matplotlib.pyplot as plt
# import yfinance as yf
import pandas as pd
import pandas_datareader.data as web
from dotenv import load_dotenv
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.messages import HumanMessage
from langgraph.graph.state import CompiledStateGraph
from tabulate import tabulate

from currensee.agents.tools.base import SupervisorState
from currensee.core import get_model, settings
from currensee.schema import AgentInfo

load_dotenv()

import logging
from dataclasses import dataclass


@dataclass
class Agent:
    description: str
    graph: CompiledStateGraph


logger = logging.getLogger(__name__)
model = get_model(settings.DEFAULT_MODEL)


def chunk_sources_with_metadata(
    sources: dict[str, list[dict]], max_length: int = 1000
) -> dict[str, tuple[str, str]]:
    """
    Chunk each source's snippet and retain the original link with each chunk.
    Returns a dict like { 'Client Industry Summary [1.1]': (chunk_text, source_url) }
    """
    chunked = {}
    for category, entries in sources.items():
        for i, entry in enumerate(entries):
            snippet = entry.get("snippet", "")
            link = entry.get("link", "")
            title = entry.get("title", "")

            full_text = f"{title}\n{snippet}".strip()
            chunks = wrap(
                full_text, max_length, break_long_words=False, replace_whitespace=False
            )

            for j, chunk in enumerate(chunks):
                key = f"{category} [{i+1}.{j+1}]"
                chunked[key] = (chunk.strip(), link)
    return chunked


def build_prompt_with_urls(
    summary: str, chunked_sources: dict[str, tuple[str, str]]
) -> str:
    formatted_sources = "\n\n".join(
        f"{key} (Source: {url}):\n{chunk}"
        for key, (chunk, url) in chunked_sources.items()
    )

    return f"""
You are a financial analyst assistant. You generated the following summary:

--- Summary ---
{summary}

You used these source snippets (each with its original URL):

--- Sources ---
{formatted_sources}

Please map each claim from the summary to the URLs that support it. Format:

- Summary claim: "..."
  → Source URL(s): ["https://..."]

Use only the URLs in the provided sources. Don't invent URLs.
"""


def format_holdings_sources(raw_sources):
    if not raw_sources:
        return []

    formatted = []
    for ticker, articles in raw_sources.items():
        for article in articles:
            formatted.append(
                {
                    "title": article.get("title", ticker),
                    "snippet": article.get("snippet", ""),
                    "link": article.get("link", ""),
                }
            )

    return formatted


def get_soucing_prompt(state: SupervisorState) -> str:
    sources = {
        # "Client Industry Summary": result.get("client_industry_sources", []),
        "Client Industry Summary": state["client_industry_sources"],
        "Holdings Summary": format_holdings_sources(state["client_holdings_sources"]),
        "Macro Summary": state["macro_news_sources"],
    }
    summary = state["final_summary"]
    chunked_sources = chunk_sources_with_metadata(sources)

    # Step 2: Compose prompt and ask LLM
    prompt = build_prompt_with_urls(summary, chunked_sources)
    return prompt


# Step 3.5: Filter the output to remove claims with no supporting URLs
def filter_empty_sources(response_text: str) -> str:
    # Split the output into individual claim blocks
    claim_blocks = re.split(r"\n(?=- Summary claim:)", response_text.strip())

    # Keep only those blocks that contain at least one URL
    filtered_blocks = [
        block
        for block in claim_blocks
        if not re.search(r"→ Source URL\(s\):\s*\[\s*\]\s*(\*.*\*)?", block)
    ]

    return "\n\n".join(filtered_blocks)


def extract_claim_url_pairs(response_text: str) -> list[tuple[str, list[str]]]:
    """
    Extracts a list of (claim, urls) from the LLM's response.
    """
    claim_url_pairs = []
    blocks = re.findall(
        r'- Summary claim:\s*"(.*?)"\s*→ Source URL\(s\):\s*(\[.*?\])',
        response_text,
        re.DOTALL,
    )
    for claim, urls_str in blocks:
        try:
            urls = eval(urls_str, {"__builtins__": None}, {})
            if isinstance(urls, list) and all(isinstance(u, str) for u in urls):
                claim_url_pairs.append((claim.strip(), urls))
        except Exception:
            continue
    return claim_url_pairs


def insert_links_into_summary(
    summary: str, claim_url_pairs: list[tuple[str, list[str]]]
) -> str:
    """
    Inserts Markdown-style [Source] links after corresponding claims in the summary.
    Only includes up to 3 sources per claim (truncates any extra).
    """
    updated_summary = summary

    for claim, urls in claim_url_pairs:
        truncated_urls = urls[:3]  # Truncate to at most 3 URLs

        if len(truncated_urls) == 1:
            link_text = f" ([Source]({truncated_urls[0]}))"
        else:
            link_text = (
                " ("
                + ", ".join(
                    f"[Source {i+1}]({url})" for i, url in enumerate(truncated_urls)
                )
                + ")"
            )

        pattern = re.escape(claim)
        replacement = f"{claim}{link_text}"

        updated_summary, count = re.subn(pattern, replacement, updated_summary, count=1)
    #  if count == 0:
    #     print(f" Could not find claim in summary: '{claim}'")

    return updated_summary


def get_fin_linked_summary(state: SupervisorState) -> str:
    prompt = get_soucing_prompt(state)
    response = model.invoke([HumanMessage(content=prompt)])
    filtered_output = filter_empty_sources(response.content)
    claim_url_pairs = extract_claim_url_pairs(filtered_output)
    summary = state["final_summary"]
    linked_summary = insert_links_into_summary(summary, claim_url_pairs)

    new_state = state.copy()
    new_state["final_summary_sourced"] = linked_summary
    return new_state
