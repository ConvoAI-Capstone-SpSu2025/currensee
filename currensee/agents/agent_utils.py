from dataclasses import dataclass

from langgraph.graph.state import CompiledStateGraph

from currensee.agents.chatbot import chatbot
from currensee.agents.supervisor_agent import supervisor_agent
from currensee.schema import AgentInfo

DEFAULT_AGENT = "supervisor-agent"


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