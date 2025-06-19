from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph

from currensee.agents.agent_utils import summarize_all_outputs
from currensee.agents.tools.base import SupervisorState
from currensee.agents.tools.crm_tools import retrieve_client_metadata
from currensee.agents.tools.finance_tools import (
    retrieve_client_industry_news, retrieve_holdings_news, retrieve_macro_news,
    summarize_finance_outputs)
from currensee.agents.tools.outlook_tools import (
    produce_client_email_summary, produce_recent_client_email_summary,
    produce_recent_client_questions)
from currensee.core import get_model, settings
from currensee.utils.sourcing_utils import get_fin_linked_summary

load_dotenv()

import asyncio

# === Model ===
model = get_model(settings.DEFAULT_MODEL)


# === Build the Graph ===


# Define the multi-agent supervisor graph
complete_graph = StateGraph(SupervisorState)

complete_graph.add_node("retrieve_client_metadata", retrieve_client_metadata)
complete_graph.add_node("produce_outlook_summary", produce_client_email_summary)
complete_graph.add_node(
    "produce_recent_outlook_summary", produce_recent_client_email_summary
)
complete_graph.add_node(
    "produce_recent_client_questions", produce_recent_client_questions
)

complete_graph.add_node("run_client_holdings_agent", retrieve_holdings_news)
complete_graph.add_node("run_client_industry_agent", retrieve_client_industry_news)
complete_graph.add_node("run_macro_finnews_agent", retrieve_macro_news)
complete_graph.add_node("finance_summarizer_agent", summarize_finance_outputs)
complete_graph.add_node("final_summarizer_agent", summarize_all_outputs)
complete_graph.add_node("add_sourcing_agent", get_fin_linked_summary)

complete_graph.add_edge(START, "retrieve_client_metadata")
complete_graph.add_edge("retrieve_client_metadata", "produce_outlook_summary")
complete_graph.add_edge("produce_outlook_summary", "produce_recent_outlook_summary")
complete_graph.add_edge(
    "produce_recent_outlook_summary", "produce_recent_client_questions"
)
complete_graph.add_edge("produce_recent_client_questions", "run_macro_finnews_agent")
complete_graph.add_edge("run_macro_finnews_agent", "run_client_industry_agent")
complete_graph.add_edge("run_client_industry_agent", "run_client_holdings_agent")
complete_graph.add_edge("run_client_holdings_agent", "finance_summarizer_agent")
complete_graph.add_edge("finance_summarizer_agent", "final_summarizer_agent")
complete_graph.add_edge("final_summarizer_agent", "add_sourcing_agent")
complete_graph.add_edge("add_sourcing_agent", END)
# complete_graph.add_edge("final_summarizer_agent", END)

compiled_graph = complete_graph.compile()


def main():
    # Example demonstrating different report lengths
    # You can specify 'short', 'medium', or 'long' (default is 'long' if not specified)
    init_state = {
        "client_name": "Adam Clay",
        "client_email": "adam.clay@compass.com",
        "meeting_timestamp": "2024-03-26 11:00:00",
        "meeting_description": "Compass - Annual Credit Facility Review Meeting",
        "report_length": "long",  # Set to 'short', 'medium', or 'long'
    }

    # print(f"\n=== INITIALIZING GRAPH WITH REPORT LENGTH: {init_state.get('report_length', 'long')} ===")

    result = compiled_graph.invoke(init_state)

    # print(result['final_summary'])
    print(result["final_summary_sourced"])


if __name__ == "__main__":
    main()
