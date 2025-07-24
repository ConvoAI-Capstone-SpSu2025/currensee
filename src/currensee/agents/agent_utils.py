import logging
from dataclasses import dataclass

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.graph.state import CompiledStateGraph

from currensee.agents.tools.base import SupervisorState
from currensee.agents.prompts import comms_prompts, news_prompts, holdings_prompts
from currensee.core import get_model, settings
from currensee.schema import AgentInfo

load_dotenv()

logger = logging.getLogger(__name__)
model = get_model(settings.DEFAULT_MODEL)


@dataclass
class Agent:
    description: str
    graph: CompiledStateGraph


# # Graph-specific utils

def summarize_all_outputs(state: SupervisorState) -> str:
    """
    Summarizes the outputs from all provided tools into one coherent summary.

    Parameters:
    - state: SupervisorState containing all tool outputs and configurations

    Returns:
    - A modified state with the final summary added
    """


    holdings_detail = state["holdings_detail"] 
    client_news_detail = state["client_news_detail"]
    macro_news_detail = state["macro_news_detail"]
    past_meeting_detail = state["past_meeting_detail"]
    meeting_category = state["meeting_category"]
    news_focus = state["news_focus"]



    # Log the report length being used
    print(f"\n===============================")
    print(f"Generating report with the following preferences: ")
    print(f" Holdings Detail: {holdings_detail} ")
    print(f" Client News Detail: {client_news_detail} ")
    print(f" Macro News Detail: {macro_news_detail}")
    print(f" Past Meeting Detail: {past_meeting_detail}")
    print(f" Meeting topic: {meeting_category}")
    print(f"===============================\n")

    

    # Select the appropriate prompts based on preferences
    finance_holdings_prompt = holdings_prompts.get(holdings_detail.lower(), holdings_prompts["full"])
    client_news_prompt = news_prompts.get(client_news_detail.lower(), news_prompts["full"])
    client_comms_prompt = comms_prompts.get(past_meeting_detail.lower(), comms_prompts["full"])

    new_state = state.copy()
    
    if finance_holdings_prompt:
        # Pass the entire state to the prompt for formatting
        # It will only use the variables declared in brackets
        # in the given prompt.
        formatted_prompt = finance_holdings_prompt.format(**state)
        # Create the messages to pass to the model
        messages_fin_hold = [HumanMessage(content=formatted_prompt)]
        # Produce the summary
        summary_fin_hold = model.invoke(messages_fin_hold)
        # Assign the summary to the state
        new_state["summary_fin_hold"] = summary_fin_hold.content
    else:
        new_state["summary_fin_hold"] = ""

    if client_news_prompt:
        formatted_prompt = client_news_prompt.format(**state)
        messages_client_news = [HumanMessage(content=formatted_prompt)] 
        summary_client_news = model.invoke(messages_client_news)
        new_state["summary_client_news"] = summary_client_news.content
    else:
        new_state["summary_client_news"] = ""

    if client_comms_prompt:
        formatted_prompt = client_comms_prompt.format(**state)
        messages_client_comms = [HumanMessage(content=formatted_prompt)] 
        summary_client_comms = model.invoke(messages_client_comms)
        new_state["summary_client_comms"] = summary_client_comms.content
    else:
        new_state["summary_client_comms"] = ""

    return new_state
