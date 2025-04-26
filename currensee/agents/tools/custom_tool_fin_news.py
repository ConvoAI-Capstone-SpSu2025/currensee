import os
os.environ['USER_AGENT'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

import os

import requests
from langchain.tools import tool
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool
import requests
import json



class CustomSerperDevTool(BaseTool):
    name: str = "Customer Serper Dev Tool"
    description: str = "Search the internet for news."


    def _run(self, query: str) -> str:
        """
        Search the internet for news.
        """

        url = "https://google.serper.dev/news"

        payload = json.dumps({
            "q": query,
            "num": 10,
            "tbs": "qdr:d"
        })
        headers = {
        'X-API-KEY': '4369e38ae59aff075549b44c923813da127c06ef',
        'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        # Parse the JSON response
        response_data = response.json()
        
        # Extract only the news proporty
        news_data = response_data.get("news", [])
        
        return "this is an example of a tool output."
        # Convert the news data back to a JSON string
        return json.dumps(news_data, indent =2)

        
