import numpy as np
import pandas as pd
from dotenv import load_dotenv

from currensee.agents.tools.base import SupervisorState
from currensee.core import get_model, settings
from currensee.utils.db_utils import create_pg_engine


load_dotenv()

# === Model ===
model = get_model(settings.DEFAULT_MODEL)


# === DB Connection ===
DB_NAME = "crm_outlook"
engine = create_pg_engine(db_name=DB_NAME)


def retrieve_current_formatt_preferences(state: SupervisorState) -> dict:
    """
    Find the current user preferences for the length and formatt of the report pieces
    """
    user_email = state["user_email"]
    meeting_timestamp = state["meeting_timestamp"]

    mx_dt_df = pd.read_sql(f"""
    SELECT max(p.as_of_date) as as_of_date
    FROM preferences p
    where p.email = '{user_email}'
    and as_of_date <= '{meeting_timestamp}'
    """, con=engine)
    
    max_dt = mx_dt_df['as_of_date'][0]
    
    query_str = f"""
    SELECT p.as_of_date
    , p.employee_first_name
    , p.employee_last_name
    , p.finance_detail
    , p.news_detail
    , p.macro_news_detail
    , p.past_meeting_detail 
    , p.email	
    FROM preferences p
    where p.email = '{user_email}' and p.as_of_date = '{max_dt}'
    """

    pref_df = pd.read_sql(query_str, con=engine)
    fin_detail = pref_df["finance_detail"][0]
    news_detail = pref_df["news_detail"][0]
    macro_news_detail = pref_df["macro_news_detail"][0]
    past_meeting_detail = pref_df["past_meeting_detail"][0]


    new_state = state.copy()
    new_state["finance_detail"] = fin_detail
    new_state["news_detail"] = news_detail
    new_state["macro_news_detail"] = macro_news_detail
    new_state["past_meeting_detail"] = past_meeting_detail
    return new_state
