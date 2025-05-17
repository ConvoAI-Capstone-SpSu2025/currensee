from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END

from currensee.core import get_model, settings
#from currensee.agents.agent_utils import summarize_outputs, ReturnAsyncValue
#from currensee.agents.agent_utils import summarize_all_outputs
from currensee.agents.tools.base import SupervisorState

from currensee.agents.tools.crm_tools import retrieve_client_metadata
from currensee.agents.tools.outlook_tools import produce_client_email_summary
from currensee.agents.tools.outlook_tools_lc import produce_recent_client_email_summary
from currensee.agents.tools.finance_tools import retrieve_client_industry_news, retrieve_holdings_news, retrieve_macro_news, summarize_finance_outputs

from dotenv import load_dotenv
load_dotenv()

import asyncio


from dotenv import load_dotenv
load_dotenv()

import asyncio

# === Model ===
model = get_model(settings.DEFAULT_MODEL)


# === Summary ===

def summarize_all_outputs(state: SupervisorState) -> str:
    """
    Summarizes the outputs from all provided tools into one coherent summary.
    
    Parameters:
    - tool_outputs: A list of strings (outputs from different tools)
    
    Returns:
    - A summarized string with key points from all the tool outputs.
    """

    finance_summary = state["finnews_summary"]
    email_summary = state["email_summary"]
    recent_email_summary = state["recent_email_summary"]
    company_name = state['client_company']
    client_name = state['client_name']
    meeting_description = state['meeting_description']

    # Combine all outputs into a formatted prompt
    combined_prompt = f"""
        You are a skilled financial advisor with an upcoming meeting with {client_name} who works for {company_name}. Below are summaries of email correspondence with that client and the relevant financial data regarding the recent company's industry performance, the performance of their stock holdings, and the performance of the overall economy.

        Combine these summaries into one document that will help prepare other meeting attendees for the meeting with all of the relevant data, keeping in mind that the topic of the meeting is {meeting_description}. Format into multiple parts with separate sections (with headings) for the past meeting/email summary, most recent email summary, and the financial news data.  Format the financial news summary and email summary as a paragraphs. Use bullet points to format the recent email summary results.

        email summary : {email_summary}

        recent email summary : {recent_email_summary}

        financial news summary: {finance_summary}


    """
    
    # Create the messages to pass to the model
    messages = [
        HumanMessage(content=combined_prompt)
    ]
    
    # Use the 'invoke' method for summarization
    summary = model.invoke(messages)

    new_state = state.copy()
    new_state["final_summary"] = summary.content
    
    # Access the message content correctly
    return new_state

# === Build the Graph ===


# Define the multi-agent supervisor graph
complete_graph = StateGraph(SupervisorState)

complete_graph.add_node("retrieve_client_metadata", retrieve_client_metadata)
complete_graph.add_node("produce_outlook_summary", produce_client_email_summary)
complete_graph.add_node("produce_recent_outlook_summary", produce_recent_client_email_summary)


complete_graph.add_node("run_client_holdings_agent", retrieve_holdings_news)
complete_graph.add_node("run_client_industry_agent", retrieve_client_industry_news)
complete_graph.add_node("run_macro_finnews_agent", retrieve_macro_news)
complete_graph.add_node("finance_summarizer_agent", summarize_finance_outputs)
complete_graph.add_node("final_summarizer_agent", summarize_all_outputs)

complete_graph.add_edge(START, "retrieve_client_metadata")
complete_graph.add_edge("retrieve_client_metadata", "produce_outlook_summary")
complete_graph.add_edge("produce_outlook_summary", "produce_recent_outlook_summary")
complete_graph.add_edge("produce_recent_outlook_summary", "run_macro_finnews_agent")
complete_graph.add_edge("run_macro_finnews_agent", "run_client_industry_agent")
complete_graph.add_edge("run_client_industry_agent", "run_client_holdings_agent")
complete_graph.add_edge("run_client_holdings_agent", "finance_summarizer_agent")
complete_graph.add_edge("finance_summarizer_agent", "final_summarizer_agent")
complete_graph.add_edge("final_summarizer_agent", END)

compiled_graph = complete_graph.compile()

def main():
    init_state = {
        'client_name': 'Adam Clay',
        'client_email': 'adam.clay@compass.com',
        'meeting_timestamp': '2024-03-26 11:00:00',
        'meeting_description': 'Compass - Annual Credit Facility Review Meeting'

    }

    result = compiled_graph.invoke(init_state)

    print(result['finnews_summary'])

if __name__ == "__main__":
    main()
