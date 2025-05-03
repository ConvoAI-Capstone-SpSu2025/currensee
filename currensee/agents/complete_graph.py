from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END

from currensee.core import get_model, settings
from currensee.agents.agent_utils import summarize_outputs

from currensee.agents.tools.crm_tools import retrieve_client_metadata
from currensee.agents.tools.outlook_tools import produce_client_email_summary
from currensee.agents.tools.finance_tools import retrieve_client_industry_news, retrieve_holdings_news, retrieve_macro_news, FinNewsState

from dotenv import load_dotenv
load_dotenv()

# === Model ===
model = get_model(settings.DEFAULT_MODEL)


# === Summary ===

def summarize_outputs(state: FinNewsState) -> str:
    """
    Summarizes the outputs from all provided tools into one coherent summary.
    
    Parameters:
    - tool_outputs: A list of strings (outputs from different tools)
    
    Returns:
    - A summarized string with key points from all the tool outputs.
    """

    client_industry_output = state["client_industry_summary"]
    client_holdings_output = state["client_holdings_summary"]
    macro_finnews_output = state["macro_news_summary"]

    # Combine all outputs into a formatted prompt
    combined_prompt = "\n\n".join(
        [f"Tool {i+1} Output:\n{output}" for i, output in enumerate([client_industry_output, client_holdings_output, macro_finnews_output])]
    )
    combined_prompt += "\n\nPlease summarize the key points from all the outputs into one concise, long summary. Include specific numbers where applicable."
    
    # Create the messages to pass to the model
    messages = [
        HumanMessage(content=combined_prompt)
    ]
    
    # Use the 'invoke' method for summarization
    summary = model.invoke(messages)

    new_state = state.copy()
    new_state["complete_summary"] = summary.content
    
    # Access the message content correctly
    return new_state

# === Build the Graph ===


# Define the multi-agent supervisor graph
complete_graph = StateGraph(FinNewsState)

complete_graph.add_node("retrieve_client_metadata", retrieve_client_metadata)
complete_graph.add_node("produce_outlook_summary", produce_client_email_summary)

complete_graph.add_node("run_client_holdings_agent", retrieve_holdings_news)
complete_graph.add_node("run_client_industry_agent", retrieve_client_industry_news)
complete_graph.add_node("run_macro_finnews_agent", retrieve_macro_news)
complete_graph.add_node("summarizer_agent", summarize_outputs)

complete_graph.add_edge(START, "retrieve_client_metadata")
complete_graph.add_edge("retrieve_client_metadata", "produce_outlook_summary")
complete_graph.add_edge("produce_outlook_summary", "run_macro_finnews_agent")
complete_graph.add_edge("run_macro_finnews_agent", "run_client_industry_agent")
complete_graph.add_edge("run_client_industry_agent", "run_client_holdings_agent")
complete_graph.add_edge("run_client_holdings_agent", "summarizer_agent")
complete_graph.add_edge("summarizer_agent", END)

compiled_graph = complete_graph.compile()




if __name__ == "__main__":
    init_state = {
        'client_name': 'Adam Clay',
        'client_email': 'adam.clay@compass.com',
        'meeting_timestamp': '2024-03-26 11:00:00',
        'meeting_description': 'Compass - Annual Credit Facility Review Meeting'

    }

    result = compiled_graph.invoke(init_state)

    print(result)