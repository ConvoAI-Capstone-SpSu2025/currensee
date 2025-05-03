from typing import TypedDict, List, Dict, Any, Optional

import matplotlib.pyplot as plt


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






class SupervisorState(TypedDict):


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
    last_meeting_date: Optional[str]
    relevant_client_emails: Optional[list[str]]
    email_summary: Optional[str]


    # Finnews response generation
    macro_news_summary: Optional[str]
    client_industry_summary: Optional[str]
    client_holdings_summary: Optional[str]
    finnews_summary: Optional[str]




    # Processing metadata
    messages: List[Dict[str, Any]]  # Track conversation with LLM for analysis





