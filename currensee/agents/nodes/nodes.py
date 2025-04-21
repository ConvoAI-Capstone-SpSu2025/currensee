from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool
from currensee.agents.tools.o365_tools import o365_tools

llm = ChatGoogleGenerativeAI('gemini-2.0-flash-lite')


#########################
# SECRETARY NODE (O365) #
#########################
secretary_prompt = """
    You are a secretary trusted with outlook data (emails, meeting schedules, etc.) 
    for a financial advisor. You are to use this information to assist with preparation
    for client meetings and drafting up email responses based on this information.
"""

secretary_agent = create_react_agent(
    llm, tools=o365_tools, prompt=secretary prompt,
)


def secretary_node(state: State) -> Command[Literal["supervisor"]]:
    result = secretary_agent.invoke(state)
    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="secretary")
            ]
        },
        goto="supervisor",
    )


#############################################
# MARKET RESEARCH NODE (Financial Datasets) #
#############################################


secretary_agent = create_react_agent(
    llm, tools=[YahooFinanceNewsTool()],
)


def secretary_node(state: State) -> Command[Literal["supervisor"]]:
    result = market_researcher_agent.invoke(state)
    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="market_researcher")
            ]
        },
        goto="supervisor",
    )



#######################################
# MARKET RESEARCH NODE (CRM Datasets) #
#######################################