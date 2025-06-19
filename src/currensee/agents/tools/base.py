from typing import Any, Dict, List, Optional, TypedDict

import matplotlib.pyplot as plt


class SupervisorState(TypedDict):

    # initial state attributes from
    # meeting invite
    client_name: str
    client_email: str

    meeting_timestamp: str
    meeting_description: str

    # CRM response generation
    client_company: Optional[str]
    client_holdings: Optional[list[str]]
    client_industry: Optional[str]
    all_client_emails: Optional[list[str]]

    # outlook response generation
    last_meeting_timestamp: Optional[str]
    relevant_client_emails: Optional[list[str]]
    email_summary: Optional[str]  # final outlook output 1
    recent_email_summary: Optional[str]  # final outlook output 2
    recent_client_questions: Optional[str]  # final outlook output 3

    # Finnews response generation
    macro_news_sources: Optional[list[dict]]
    client_industry_sources: Optional[list[dict]]
    client_holdings_sources: Optional[list[dict]]
    finnews_summary: Optional[str]  # final finnews output

    # Complete response
    final_summary: Optional[str]
    report_length: Optional[str]  # Controls report format: 'short', 'medium', or 'long'

    # final summary with links for sourcing
    final_summary_sourced: Optional[str]

    # Processing metadata
    messages: List[Dict[str, Any]]  # Track conversation with LLM for analysis
