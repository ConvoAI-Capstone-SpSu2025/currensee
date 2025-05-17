from dataclasses import dataclass

from langchain_core.messages import HumanMessage
from langgraph.graph.state import CompiledStateGraph

from currensee.schema import AgentInfo
from currensee.core import get_model, settings
from currensee.agents.tools.base import SupervisorState

from dotenv import load_dotenv
load_dotenv()

model = get_model(settings.DEFAULT_MODEL)


@dataclass
class Agent:
    description: str
    graph: CompiledStateGraph


## Graph-specific utils

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
    company_name = state['client_company']
    client_name = state['client_name']
    meeting_description = state['meeting_description']
    recent_email_summary = state["recent_email_summary"]
    recent_client_questions = state['recent_client_questions']

    # Combine all outputs into a formatted prompt
    combined_prompt = f"""
        You are a skilled financial advisor with an upcoming meeting with {client_name} who works for {company_name}. Below are summaries of email past correspondence with that client, recent email topics, recent client questions, and the relevant financial data regarding the recent company's industry performance, the performance of their holdings, and the performance of the overall economy.

        Combine these summaries into one document that will help prepare other meeting attendees for the meeting with all of the relevant data, keeping in mind that the topic of the meeting is {meeting_description}. 
        
        Format into multiple parts with separate sections (with headings) for the past meeting/email summary, most recent email summary, and the financial news data. Format the financial news summary and email summary as a paragraphs. Format the recent email summary as bullet points. 
        
    Format the recent client questions as a numbered list. DO NOT include any questions or summary points about logistics, meeting times, proposed times, or scheduling. If no questions are provided in the {recent_client_questions}, DO NOT say anything about client questions and omit the section.

       Past email summary : {email_summary}
       
       Recent email summary: {recent_email_summary}
       
       Recent client questions: {recent_client_questions}

       Financial news summary: {finance_summary}

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

