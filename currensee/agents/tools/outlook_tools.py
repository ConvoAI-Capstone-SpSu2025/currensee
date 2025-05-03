import pandas as pd
import numpy as np
from currensee.utils.db_utils import create_pg_engine
from sqlalchemy import text
from currensee.workflows.sql_workflow.utils import create_sql_workflow
from currensee.workflows.workflow_descriptions import outlook_table_description_mapping

from currensee.agents.tools.base import SupervisorState, CrmState


DB_NAME = 'outlook'



sql_workflow = create_sql_workflow(
    source_db = DB_NAME,
    table_description_mapping=outlook_table_description_mapping,
    synthesize_response=False
)


async def find_last_meeting_date(all_client_emails) -> dict:

    query_str = f"When was the date of the last meeting that was conducted with any of the following emails: {all_client_emails}?"

    result = await sql_workflow.run(query=query_str)

    return result.response


async def produce_client_email_summary(state: SupervisorState) -> dict:

    all_client_emails = state['all_client_emails']

    last_meeting_date = await find_last_meeting_date(all_client_emails=all_client_emails)

    query_str = f"What are all of the emails sent to or from {all_client_emails} since {last_meeting_date}?"

    result = await sql_workflow.run(query=query_str)

    new_state = state.copy()
    new_state['last_meeting_date'] = last_meeting_date

    return new_state



