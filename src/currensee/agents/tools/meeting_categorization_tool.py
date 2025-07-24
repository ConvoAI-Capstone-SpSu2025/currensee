# Categorization of meeting as "Finance Focus" vs. "Relationship Focus" vs. "Regulatory Focus" vs. "Annual Review"

# Inputs should be meeting description and recent email summary

# Output should be categorization, which will impact the focus of the report (i.e. change the content of the report) via
# length of section + focus of section

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from sqlalchemy import text

from currensee.agents.tools.base import SupervisorState
from currensee.core import get_model, settings
from currensee.utils.db_utils import create_pg_engine

load_dotenv()

# === Model ===
model = get_model(settings.DEFAULT_MODEL)


# === DB Connection ===
DB_NAME = "crm_outlook"
engine = create_pg_engine(db_name=DB_NAME)

def categorize_meeting_topic(state: SupervisorState) -> dict:
    """
    Categorize client meeting topic into Customer Relationship, Finance Planning, or Regulatory
    """
    meeting_description = state["meeting_description"]
    recent_email_summary = state["recent_email_summary"]


    prompt = f"""
    PROMPT

   Classify the meeting topic into one of the following categories ["Customer Relationship", "Finance", "Annual Review", "Regulatory", ] using the guidance below. Use the Meeting Description and Recent Email Summary to do this.

   Guidance:
   - Categorize as "Annual Review" if description focuses on topics such as: portfolio review, annual review, goals, year ahead, or broad objectives
   - Categorize as "Customer Relationship" if description focuses on topics such as: onboarding, product needs, relationship review, or introduction to bankwell
   - Categorize as "Regulatory" if description focuses on topics such as: insider trading, regulatory, regulations, SCC, FINRA, or compliance
   - Categorize as "Benchmark Change" if description focuses on topics such as: benchmark changed, reporting, re-alignment, or transition
   - Categorize as "ESG Investing" if description focuses on topics such as: ESG, environmental, green investing, Carbon score, climate, or sustainability
   - Categorize as "Risk Management" if description focuses on topics such as: risk, stress testing, hedging, diversification, or exposure
   - Categorize as "Tax Optimization" if description focuses on topics such as: tax, charitable deductions, capital gains, loss realization, or IRS
   - Categorize as "New Funds Offerings" if description focuses on topics such as: fund launch, fund enhancements, new fund allocation, or innovative funds
   - Categorize as "Macro Update" if description focuses on topics such as: macro, headwinds, federal reserve, fed policy, central bank, geopolitical, political, commodity trends, currency trends, or market conditions
     
    Important Instructions:
    1. Only return a categorization from this list ["Customer Relationship", "Benchmark Change", "Annual Review", "Regulatory", "ESG Investing", "Risk Management", "Tax Optimization", "New Funds Offerings", "Macro Update"]
    2. If the categorization is not clear based on the Meeting Description, then refer to the Recent Email Summary.

 Inputs:
    Meeting Description: {meeting_description} 
    Recent Email Summary: {recent_email_summary}

"""

    # Create the messages to pass to the model
    messages = [HumanMessage(content=prompt)]

    # Use the 'invoke' method for summarization
    meeting_category = model.invoke(messages)

    ############# Return the new state ###############

    new_state = state.copy()
    new_state["meeting_category"] = meeting_category.content

    return new_state

def determine_topic_of_news(state: SupervisorState) -> dict:
    meeting_category = state["meeting_category"]
    
    holdings_news_pref = state["holdings_detail"]
    client_news_pref = state["client_news_detail"]
    macro_pref = state["macro_news_detail"]
    comms_dtl_pref = state["past_meeting_detail"]
    
    news_topic = "Finance"
    if meeting_category == "Regulatory":
        news_topic = "Regulatory, SEC, SCC, FINRA"
    elif meeting_category == "ESG Investing":
        news_topic = "ESG Investing, Sustainability"
    elif meeting_category == "Tax Optimization":
        news_topic = "Taxes, IRS"
    elif meeting_category == "Macro Update":
        news_topic = "Federal Reserve Bank, Interest Rates, politics, market conditions"
    
    new_state = state.copy()
    new_state["news_focus"] = news_topic
    return new_state

    
        

    

    