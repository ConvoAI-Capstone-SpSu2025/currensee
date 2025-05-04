from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END

from currensee.core import get_model, settings


from currensee.agents.tools.finance_tools import retrieve_client_industry_news, retrieve_holdings_news, retrieve_macro_news, FinNewsState

from dotenv import load_dotenv
load_dotenv()

# === Model ===
model = get_model(settings.DEFAULT_MODEL)


# === 


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
financial_graph = StateGraph(FinNewsState)

financial_graph.add_node("run_client_holdings_agent", retrieve_holdings_news)
financial_graph.add_node("run_client_industry_agent", retrieve_client_industry_news)
financial_graph.add_node("run_macro_finnews_agent", retrieve_macro_news)
financial_graph.add_node("summarizer_agent", summarize_outputs)

financial_graph.add_edge(START, "run_macro_finnews_agent")
financial_graph.add_edge("run_macro_finnews_agent", "run_client_industry_agent")
financial_graph.add_edge("run_client_industry_agent", "run_client_holdings_agent")
financial_graph.add_edge("run_client_holdings_agent", "summarizer_agent")
financial_graph.add_edge("summarizer_agent", END)

compiled_graph = financial_graph.compile()




if __name__ == "__main__":
    init_state = {
        'client_name': 'Walmart',
        'start_date': '1/31/2025',
        'end_date': '4/30/2025',
        'client_industry': 'retail',
        'client_holdings': ['Amazon.com Inc', 'Meta Platforms Inc', 'Microsoft Corp']

    }

    result = compiled_graph.invoke(init_state)

    print(result)