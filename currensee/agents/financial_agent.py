from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import create_react_agent, ToolNode
from langchain_core.runnables import RunnableLambda, RunnableConfig
from langchain.tools import tool

from currensee.core import get_model, settings
from currensee.agents.agent_utils import summarize_outputs
from currensee.agents.tools.finance_tools import client_and_industry, macro_news, holdings_news
from currensee.agents.tools.graph_tools import create_handoff_tool

# === Model ===
model = get_model(settings.DEFAULT_MODEL)

# === Agents ===

client_finnews_agent = create_react_agent(
model=model,
    tools=[client_and_industry, holdings_news],
    name="client_finnews_expert",
    prompt="You are a world-class researcher with special skills in researching the financial news within the industry and about the financial holdings of a specific client.",
).with_config(tags=["skip_stream"])

def run_client_finnews_agent(state: MessagesState):
    messages = state["messages"]
    result = math_agent.invoke({"messages": messages})
    return {"messages": messages + [result]}
    

macro_finnews_agent = create_react_agent(
    model=model,
    tools=[macro_news],
    name="macro_finnews_expert",
    prompt="You are a world-class researcher with a particular interest in macroeconomic news.",
).with_config(tags=["skip_stream"])

def run_macro_finnews_agent(state: MessagesState) -> dict:
    messages = state["messages"]
    result = research_agent.invoke({"messages": messages})
    return {"messages": messages + [result]}


# Handoffs
assign_to_macro_finnews_agent = create_handoff_tool(
    agent_name="macro_finnews_agent",
    description="Assign task to a macro finnews agent. The format of the task should be 'Find news about {client_name} and about {industry} industry'",
)

assign_to_client_finnews_agent = create_handoff_tool(
    agent_name="client_finnews_agent",
    description="Assign task to a client finnews agent. The format of the task should be ",
)


supervisor_agent = create_react_agent(
    model=model,
    tools=[assign_to_macro_finnews_agent, assign_to_client_finnews_agent],
    prompt=(
        "You are a supervisor managing two agents:\n"
        "- a macro finnews agent. Assign research-related tasks to this agent\n"
        "- a client_finnews_agent. Assign math-related tasks to this agent\n"
        "Assign work to one agent at a time, do not call agents in parallel.\n"
        "Do not do any work yourself."
    ),
    name="supervisor",
)


# === Summary ===

def model_summary(state):
    messages = state['messages'][1]['messages']
    user_msg = next((m.content for m in reversed(messages) if isinstance(m, HumanMessage)), "")
    agent_response = next((m.content for m in reversed(messages) if isinstance(m, AIMessage)), "")

    

    return {"messages": state["messages"] + [AIMessage(content=summary_text)]}

# === Build the Graph ===


# Define the multi-agent supervisor graph
supervisor = (
    StateGraph(MessagesState)
    # NOTE: `destinations` is only needed for visualization and doesn't affect runtime behavior
    .add_node(supervisor_agent, destinations=("macro_finnews_agent", "client_finnews_agent", END))
    .add_node(macro_finnews_agent)
    .add_node(client_finnews_agent)
    .add_edge(START, "supervisor")
    # always return back to the supervisor
    .add_edge("macro_finnews_agent", "supervisor")
    .add_edge("client_finnews_agent", "supervisor")
    .compile()
)