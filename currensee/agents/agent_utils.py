from dataclasses import dataclass

from langchain_core.messages import HumanMessage
from langgraph.graph.state import CompiledStateGraph

from currensee.agents.chatbot import chatbot
from currensee.agents.supervisor_agent import supervisor_agent
from currensee.schema import AgentInfo

DEFAULT_AGENT = "chatbot"


@dataclass
class Agent:
    description: str
    graph: CompiledStateGraph


agents: dict[str, Agent] = {
    "chatbot": Agent(description="A simple chatbot.", graph=chatbot),
    "supervisor-agent": Agent(
        description="A langgraph supervisor agent", graph=supervisor_agent
    ),
}


def get_agent(agent_id: str) -> CompiledStateGraph:
    return agents[agent_id].graph


def get_all_agent_info() -> list[AgentInfo]:
    return [
        AgentInfo(key=agent_id, description=agent.description) for agent_id, agent in agents.items()
    ]



# Function to summarize the outputs from any number of tools
def summarize_outputs(tool_outputs: list) -> str:
    """
    Summarizes the outputs from all provided tools into one coherent summary.
    
    Parameters:
    - tool_outputs: A list of strings (outputs from different tools)
    
    Returns:
    - A summarized string with key points from all the tool outputs.
    """
    # Combine all outputs into a formatted prompt
    combined_prompt = "\n\n".join(
        [f"Tool {i+1} Output:\n{output}" for i, output in enumerate(tool_outputs)]
    )
    combined_prompt += "\n\nPlease summarize the key points from all the outputs into one concise, long summary. Include specific numbers where applicable."
    
    # Create the messages to pass to the model
    messages = [
        HumanMessage(content=combined_prompt)
    ]
    
    # Use the 'invoke' method for summarization
    summary = model.invoke(messages)
    
    # Access the message content correctly
    return summary.content  # Return the content of the AIMessage

# Function for a generic tool to retrieve information
def query_tool(query: str, tool_func) -> str:
    """Generic function to query a tool and retrieve the output."""
    return tool_func(query)