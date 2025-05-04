from dataclasses import dataclass

from langchain_core.messages import HumanMessage
from langgraph.graph.state import CompiledStateGraph

from currensee.agents.chatbot import chatbot
from currensee.schema import AgentInfo
from currensee.agents.tools.base import SupervisorState

DEFAULT_AGENT = "chatbot"


@dataclass
class Agent:
    description: str
    graph: CompiledStateGraph


agents: dict[str, Agent] = {
    "chatbot": Agent(description="A simple chatbot.", graph=chatbot),
    # "supervisor-agent": Agent(
    #     description="A langgraph supervisor agent", graph=supervisor_agent
    # ),
}


class ReturnAsyncValue: 

    def __init__(self, function):
        self.function = function

    def __call__(self, state: SupervisorState, **kwargs) -> any:
        new_state = self.sync_wrapper(state)
        return new_state
    
    def sync_wrapper(self, state:SupervisorState) -> str:
        # Running the async API call in a synchronous context
        import asyncio
        return asyncio.run(self.function(state))

    

def summarize_outputs(state: SupervisorState) -> str:
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


def get_agent(agent_id: str) -> CompiledStateGraph:
    return agents[agent_id].graph


def get_all_agent_info() -> list[AgentInfo]:
    return [
        AgentInfo(key=agent_id, description=agent.description) for agent_id, agent in agents.items()
    ]
