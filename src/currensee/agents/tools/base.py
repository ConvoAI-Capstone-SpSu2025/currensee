from typing import Any, Dict, List, Optional, TypedDict

import matplotlib.pyplot as plt


class SupervisorState(TypedDict):

    # initial state attributes from
    # meeting invite
    user_email: str
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
    recent_all_emails_dict: Optional[dict]
    recent_client_emails_dict: Optional[dict]


    # Finnews response generation
    macro_news_sources: Optional[list[dict]]
    client_industry_sources: Optional[list[dict]]
    client_holdings_sources: Optional[list[dict]]
    finnews_summary: Optional[str]  # final finnews output

    # Preference Data
    finance_detail: Optional[str]
    news_detail: Optional[str]
    macro_news_detail: Optional[str]
    past_meeting_detail: Optional[str]

    #Meeting Topic
    meeting_category: Optional[str]

    # Complete response
   # final_summary: Optional[str]
    #report_length: Optional[str]  # Controls report format: 'short', 'medium', or 'long'

    # final summary with links for sourcing
   # final_summary_sourced: Optional[str]

    # modular responses
    summary_fin_hold: Optional[str]
    summary_client_news: Optional[str]
    summary_client_comms: Optional[str]
    fin_hold_summary_sourced: Optional[str]
    client_news_summary_sourced: Optional[str]

    # Processing metadata
    messages: List[Dict[str, Any]]  # Track conversation with LLM for analysis
