from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent
from langchain_core.runnables import RunnableLambda
from langchain.tools import tool

from currensee.core import get_model, settings

# === Model ===
model = get_model(settings.DEFAULT_MODEL)

# === Tool Functions ===

@tool
def add(a: float, b: float) -> float:
    """Add two float numbers"""
    return a + b

@tool
def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b

@tool
def web_search(query: str) -> str:
    """Search the web for information."""
    return (
        "Here are the headcounts for each of the FAANG companies in 2024:\n"
        "1. **Facebook (Meta)**: 67,317 employees.\n"
        "2. **Apple**: 164,000 employees.\n"
        "3. **Amazon**: 1,551,000 employees.\n"
        "4. **Netflix**: 14,000 employees.\n"
        "5. **Google (Alphabet)**: 181,269 employees."
    )

# === Agents ===

math_agent = create_react_agent(
    model=model,
    tools=[add, multiply],
    name="math_expert",
    prompt="You are a math expert. Always use one tool at a time.",
).with_config(tags=["skip_stream"])

def run_math_agent(state: dict) -> dict:
    messages = state["messages"]
    result = math_agent.invoke({"messages": messages})
    return {"messages": messages + [result]}

research_agent = create_react_agent(
    model=model,
    tools=[web_search],
    name="research_expert",
    prompt="You are a world-class researcher with access to web search. Do not do any math.",
).with_config(tags=["skip_stream"])

def run_research_agent(state: dict) -> dict:
    messages = state["messages"]
    result = research_agent.invoke({"messages": messages})
    return {"messages": messages + [result]}

# === Router Logic ===

def route(state):
    print(state)
    last_user_msg = next((m.content for m in reversed(state["messages"]) if isinstance(m, HumanMessage)), "")
    if any(word in last_user_msg.lower() for word in ["current", "netflix", "2024", "employee", "search"]):
        return "research_expert"
    return "math_expert"

# === Summary ===

def model_summary(state):
    messages = state['messages'][1]['messages']
    user_msg = next((m.content for m in reversed(messages) if isinstance(m, HumanMessage)), "")
    agent_response = next((m.content for m in reversed(messages) if isinstance(m, AIMessage)), "")

    prompt = f"""
        You are a helpful assistant. Summarize the AI's response to the following user question in 2-3 sentences.

        Be concise, highlight the most relevant information, and avoid repeating boilerplate phrases.
        Do not refer to "the AI", the underlying system, or anything related to the code used to build the system.
        If it makes sense, suggest a follow-up question the user could ask.

        --- User Question ---
        {user_msg}

        --- AI Response ---
        {agent_response}

        --- Your Summary ---

    """
    print(prompt)
    raw_output = model.invoke(prompt.strip())
    summary_text = raw_output.content if hasattr(raw_output, "content") else str(raw_output)

    return {"messages": state["messages"] + [AIMessage(content=summary_text)]}

# === Build the Graph ===

graph = StateGraph(dict)

# Just pass through the state — routing is handled below
graph.add_node("router", RunnableLambda(lambda state: state))
graph.set_entry_point("router")

graph.add_node("math_expert", RunnableLambda(run_math_agent))
graph.add_node("research_expert", RunnableLambda(run_research_agent))
graph.add_node("summarizer", RunnableLambda(model_summary))

# Use route() only for deciding the path
graph.add_conditional_edges("router", route, {
    "math_expert": "math_expert",
    "research_expert": "research_expert",
})

graph.add_edge("math_expert", "summarizer")
graph.add_edge("research_expert", "summarizer")

graph.set_finish_point("summarizer")

# Compile
supervisor_agent = graph.compile(checkpointer=MemorySaver())
