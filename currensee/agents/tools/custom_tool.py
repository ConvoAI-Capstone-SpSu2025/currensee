from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

import os
import requests
from langchain.tools import tool
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool


class FinancialDatasetsToolInput(BaseModel):
    """Input schema for FinanciatlDatasetsTool."""
    client_name: str = Field(..., description="The name of the client we are searching for financial data about.")

class FinancialDatasetsTool(BaseTool):
    name: str = "Financial Datasets Tool"
    description: str = (
        "This tool is useful for finding open source market data about a company."
    )
    args_schema: Type[BaseModel] = MyCustomToolInput

    def _run(self, argument: str) -> str:
        # Implementation goes here
        return "this is an example of a tool output, ignore it and move along."
