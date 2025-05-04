import pandas as pd
import numpy as np
from currensee.utils.db_utils import create_pg_engine
from sqlalchemy import text
from currensee.workflows.sql_workflow.utils import create_sql_workflow
from currensee.workflows.workflow_descriptions import crm_table_description_mapping

from currensee.agents.tools.base import SupervisorState


DB_NAME = 'crm'
# engine = create_pg_engine(
#    db_name=DB_NAME
# )


sql_workflow = create_sql_workflow(
    source_db = DB_NAME,
    table_description_mapping=crm_table_description_mapping,
    synthesize_response=False
)


async def retrieve_client_industry(client_company: str) -> str:

    query_str = f"What industry does {client_company} operate in?"

    result = await sql_workflow.run(query=query_str)

    return result.response

async def retrieve_client_holdings(client_company: str) -> list[str]:

    query_str = f"What are the ticker symbols of the 5 largest stocks owned by {client_company}?"

    result = await sql_workflow.run(query=query_str)

    return result.response

async def retrieve_client_company_from_email(client_email: str) -> str:

    query_str = f"What company does the person with the email {client_email} work for?"

    result = await sql_workflow.run(query=query_str)

    return result.response


async def retrieve_all_client_emails_for_company(client_company: str) -> str:

    query_str = f"What are the emails for all of the client contacts that work for {client_company}?"

    result = await sql_workflow.run(query=query_str)

    return result.response


async def retrieve_client_metadata(state: SupervisorState) -> dict:

    print(state)

    client_email = state['client_email']

    client_company = await retrieve_client_company_from_email(client_email=client_email)

    client_holdings = await retrieve_client_holdings(client_company=client_company)

    client_industry = await retrieve_client_industry(client_company=client_company)

    all_client_emails = await retrieve_all_client_emails_for_company(client_company=client_company)

    new_state = state.copy()
    new_state['client_company'] = client_company
    new_state['client_holdings'] = client_holdings
    new_state['client_industry'] = client_industry
    new_state['all_client_emails'] = all_client_emails

    return new_state

