import os
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

from langchain_community.agent_toolkits.financial_datasets.toolkit import (
    FinancialDatasetsToolkit,
)
from langchain_community.utilities.financial_datasets import FinancialDatasetsAPIWrapper

from currensee.utils.str_utils import get_ticker

from dotenv import load_dotenv
load_dotenv()

api_wrapper = FinancialDatasetsAPIWrapper(
    financial_datasets_api_key=os.environ["FINANCIAL_DATASETS_API_KEY"]
)
toolkit = FinancialDatasetsToolkit(api_wrapper=api_wrapper)


financial_tools = toolkit.get_tools()


class BalanceSheetsToolInput(BaseModel):
    """Input schema for BalanceSheetsTool."""
    client_name: str = Field(description="The name of the client we are searching for financial data about.")

class BalanceSheetsTool(BaseTool):
    name: str = "Balance Sheets Tool"
    description: str = (
        "This tool is useful for finding balance sheets data about a company."
    )
    args_schema: Type[BaseModel] = BalanceSheetsToolInput

    def _run(self, client_name: str) -> str:
        client_ticker = get_ticker(client_name)
        balance_sheet_tool = financial_tools[0]
        response = balance_sheet_tool.invoke(client_name)
        print(response)
        # Implementation goes here
        return str(response)


print(type(BalanceSheetsTool))