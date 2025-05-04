import pandas as pd
import numpy as np
from currensee.utils.db_utils import create_pg_engine
from sqlalchemy import text
from currensee.workflows.sql_workflow.utils import create_sql_workflow
from currensee.workflows.workflow_descriptions import crm_table_description_mapping

from currensee.agents.tools.base import SupervisorState


DB_NAME = 'crm'
engine = create_pg_engine(
   db_name=DB_NAME
)


def retrieve_client_industry(client_company: str) -> str:

    query_str = f"""
        SELECT DISTINCT industry
        FROM accounts_alignment
        WHERE company = '{client_company}'
    """

    company_data = pd.read_sql(query_str, con=engine)

    client_company = company_data['industry'].iloc[0]

    return client_company


def retrieve_client_holdings(client_company: str) -> list[str]:

    query_str = f"""
        SELECT fd.position_name
        FROM fund_detail as fd join portfolio as po on fd.fund = po.symbol
        WHERE po.company = '{client_company}'
        AND po.fund_type = 'Equity Fund'
    """

    portfolio_data = pd.read_sql(query_str, con=engine)

    portfolio_positions = portfolio_data['position_name']

    return list(portfolio_positions)


def retrieve_client_company_from_email(client_email: str) -> str:

    query_str = f"""
        SELECT *
        FROM clients_contact
        WHERE email = '{client_email}'
    """

    contact_data = pd.read_sql(query_str, con=engine)


    client_company = contact_data['company'].iloc[0]

    return client_company


def retrieve_all_client_emails_for_company(client_company: str) -> str:

    query_str = f"""
        SELECT *
        FROM clients_contact
        WHERE company = '{client_company}'
    """

    all_company_contacts = pd.read_sql(query_str, con=engine)

    all_client_emails = all_company_contacts['email']

    return list(all_client_emails)


def retrieve_client_metadata(state: SupervisorState) -> dict:

    client_email = state['client_email']

    client_company = retrieve_client_company_from_email(client_email=client_email)

    client_holdings = retrieve_client_holdings(client_company=client_company)

    client_industry = retrieve_client_industry(client_company=client_company)

    all_client_emails = retrieve_all_client_emails_for_company(client_company=client_company)

    new_state = state.copy()
    new_state['client_company'] = client_company
    new_state['client_holdings'] = client_holdings
    new_state['client_industry'] = client_industry
    new_state['all_client_emails'] = all_client_emails

    return new_state

