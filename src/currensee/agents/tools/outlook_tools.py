import numpy as np
import pandas as pd
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from sqlalchemy import text

from currensee.agents.tools.base import SupervisorState
from currensee.core import get_model, settings
from currensee.utils.db_utils import create_pg_engine
from currensee.workflows.sql_workflow.utils import create_sql_workflow
from currensee.workflows.workflow_descriptions import \
    outlook_table_description_mapping

load_dotenv()

# === Model ===
model = get_model(settings.DEFAULT_MODEL)


# === DB Connection ===
DB_NAME = "crm_outlook"
engine = create_pg_engine(db_name=DB_NAME)

# sql_workflow = create_sql_workflow(
#     source_db = DB_NAME,
#     table_description_mapping=outlook_table_description_mapping,
#     synthesize_response=False
# )


# async def find_last_meeting_date(all_client_emails) -> dict:

#     query_str = f"When was the date of the last meeting that was conducted with any of the following emails: {all_client_emails}?"

#     result = await sql_workflow.run(query=query_str)

#     return result.response


def find_last_meeting_date(all_client_emails: list[str]) -> dict:
    """
    Find the last meeting date that was held with any of the
    client emails listed above.
    """

    query_str = f"""
        SELECT  meeting_timestamp
        FROM  meeting_data
        WHERE  invitee_emails ~* '{'|'.join(all_client_emails)}'
        ORDER BY meeting_timestamp DESC
        LIMIT 1;

    """

    last_meeting = pd.read_sql(query_str, con=engine)

    return last_meeting["meeting_timestamp"][0]


def produce_client_email_summary(state: SupervisorState) -> dict:
    """
    Produce a client email summary from the most recent and
    relevant emails based on the email description.
    """
    client_company = state["client_company"]
    all_client_emails = state["all_client_emails"]
    meeting_timestamp = state["meeting_timestamp"]
    meeting_description = state["meeting_description"]

    last_meeting_date = find_last_meeting_date(all_client_emails=all_client_emails)

    ## NOTE: I currently removed the meeting timestamp restrictions, because
    ## it wasn't returning any emails.

    query_str = f"""
        SELECT email_body
        FROM email_data
        WHERE
        -- email_timestamp <= '{meeting_timestamp}' AND email_timestamp >= '{last_meeting_date}'
        -- AND
        (
            to_emails ~* '{'|'.join(all_client_emails)}'
            OR
            from_email ~* '{'|'.join(all_client_emails)}'
        )
    """

    result = pd.read_sql(query_str, con=engine)

    recent_emails = list(result["email_body"])

    recent_email_str = "\n".join(recent_emails)

    ###### SUMMARIZE HERE #########

    summary_prompt = f"""
        PROMPT

        Produce a summary of past emails, listed below, between {client_company} and Bankwell Financial that will provide context most relevant to a meeting
        discussing {meeting_description}. In the description, cite information from specific emails usingthe name of the client involved in the conversation
        and, if available, the date of the email. Do not include the date or a reference to the date if the date is not specified.

        Emails:

        {recent_email_str}


    """

    # Create the messages to pass to the model
    messages = [HumanMessage(content=summary_prompt)]

    # Use the 'invoke' method for summarization
    email_summary = model.invoke(messages)

    ############# Return the new state ###############

    new_state = state.copy()
    new_state["last_meeting_timestamp"] = last_meeting_date
    new_state["email_summary"] = email_summary.content

    return new_state


def produce_recent_client_email_summary(state: SupervisorState) -> dict:
    """
    Produce a client email summary from the most recent emails based on date recieved.
    """
    client_company = state["client_company"]
    all_client_emails = state["all_client_emails"]
    meeting_timestamp = state["meeting_timestamp"]
    meeting_description = state["meeting_description"]

    last_meeting_date = find_last_meeting_date(all_client_emails=all_client_emails)

    query_str = f"""
        SELECT email_body
        FROM email_data
        WHERE
        (
            to_emails ~* '{'|'.join(all_client_emails)}'
            OR
            from_email ~* '{'|'.join(all_client_emails)}'
        )
        order by email_timestamp desc
        limit 5
    """

    result = pd.read_sql(query_str, con=engine)

    recent_emails = list(result["email_body"])

    recent_email_str = "\n".join(recent_emails)

    ###### SUMMARIZE HERE #########
    summary_prompt = f"""
    PROMPT

    You are reviewing a series of past emails exchanged between {client_company} and Bankwell Financial.

    Please complete the following task:

    1. Make a bullet point list of the main topics discussed in the emails.
        - Exclude any content related to scheduling, logistics, or meeting arrangements.
        - Focus only on business-related updates, decisions, issues, and key discussion points.
        - Present this summary as a bullet-point list. Use complete sentences in the bullet points.

    Format your response like this:

    Recent Email Bullet Points:
    • [Summary point 1]
    • [Summary point 2]
    • [Summary point 3]
    ...

    Email Thread to Analyze:
    {recent_email_str}

    """

    # Create the messages to pass to the model
    messages = [HumanMessage(content=summary_prompt)]

    # Use the 'invoke' method for summarization
    recent_email_summary = model.invoke(messages)

    ############# Return the new state ###############

    new_state = state.copy()
    new_state["last_meeting_timestamp"] = last_meeting_date
    new_state["recent_email_summary"] = recent_email_summary.content

    return new_state


def produce_recent_client_questions(state: SupervisorState) -> dict:
    """
    Produce a the recent client questions from the most recent emails based on date recieved.
    """
    client_company = state["client_company"]
    all_client_emails = state["all_client_emails"]
    meeting_timestamp = state["meeting_timestamp"]
    meeting_description = state["meeting_description"]

    last_meeting_date = find_last_meeting_date(all_client_emails=all_client_emails)

    query_str = f"""
        SELECT email_body
        FROM email_data
        WHERE
        (
            to_emails ~* '{'|'.join(all_client_emails)}'
            OR
            from_email ~* '{'|'.join(all_client_emails)}'
        )
        order by email_timestamp desc
        limit 5
    """

    result = pd.read_sql(query_str, con=engine)

    recent_emails = list(result["email_body"])

    recent_email_str = "\n".join(recent_emails)

    ###### SUMMARIZE HERE #########
    summary_prompt = f"""
    PROMPT

    You are reviewing a series of past emails exchanged between the client {client_company} and Bankwell Financial to identify client questions.

    Extract any questions asked by {client_company} or their representatives.
        - Do not include questions about availability, meeting times, or scheduling logistics.
        - Only include questions asked by {client_company} or its representative, not by the Bankwell Financial Employee.
        - Use verbatim quotes from the emails where possible. You may lightly paraphrase for clarity.
        - Present this as a numbered list.

    Format your response like this:

    Client Questions:
    1. "[Exact client question]"
    2. "[Exact client question]"
    3. "[Paraphrased question if needed]"
    ...

    Email Thread to Analyze:
    {recent_email_str}

    """

    # Create the messages to pass to the model
    messages = [HumanMessage(content=summary_prompt)]

    # Use the 'invoke' method for summarization
    recent_client_questions = model.invoke(messages)

    ############# Return the new state ###############

    new_state = state.copy()
    new_state["last_meeting_timestamp"] = last_meeting_date
    new_state["recent_client_questions"] = recent_client_questions.content

    return new_state
