from dataclasses import dataclass
import logging

from langchain_core.messages import HumanMessage
from langgraph.graph.state import CompiledStateGraph

from currensee.schema import AgentInfo
from currensee.core import get_model, settings
from currensee.agents.tools.base import SupervisorState

from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)
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
    - state: SupervisorState containing all tool outputs and configurations
    
    Returns:
    - A modified state with the final summary added
    """

    finance_summary = state["finnews_summary"]
    email_summary = state["email_summary"]
    company_name = state['client_company']
    client_name = state['client_name']
    meeting_description = state['meeting_description']
    recent_email_summary = state["recent_email_summary"]
    recent_client_questions = state['recent_client_questions']
    
    # Get report_length from state, default to 'long' if not specified
    report_length = state.get('report_length', 'long')
    
    # Log the report length being used
    print(f"\n===============================")
    print(f"Generating report with length: {report_length}")
    print(f"===============================\n")

    # Define different report formats based on length
    report_formats = {
        'short': f"""PROMPT

You are a skilled financial advisor preparing for an upcoming meeting with {client_name}, who works at {company_name}. The meeting will focus on: {meeting_description}.

Important Instructions:
1. DO NOT use any section headings or titles
2. DO NOT return a multi-section report
3. ONLY return a single flat list of 5-7 bullet points total
4. Each bullet point should begin with a • or - symbol
5. DO NOT number your points
6. Keep each bullet to 1-2 sentences maximum

Your response should ONLY contain bullets covering the most critical points from these categories. List bullet points in the order below:
- Past email key information
- Recent communication highlights
- Any critical client questions (If there were no questions provided in {recent_client_questions}, then do not state whether client questions were asked and skip this point)
- Most relevant financial data

Combine all information into JUST ONE bullet list with NO section headers or other text.

Inputs:
Past email summary: {email_summary}
Recent email summary: {recent_email_summary}
Recent client questions: {recent_client_questions}
Financial summary: {finance_summary}
""",
        
        'medium': f"""PROMPT

You are a skilled financial advisor preparing for an upcoming meeting with {client_name}, who works at {company_name}. The meeting will focus on: {meeting_description}.

Your task:
Create a condensed briefing document (about 2 paragraphs total) for internal use, covering only the most relevant points.

Format the report into two main sections:

1. Client Communication Summary
 - Combine past and recent email topics into one concise paragraph
 - Include any critical client questions (excluding logistics questions). If there were no questions provided in {recent_client_questions}, then do not state whether client questions were asked.

2. Financial Overview
 - Write a concise paragraph summarizing the most important financial data points

Keep each paragraph focused and brief.

Inputs:
Past email summary: {email_summary}
Recent email summary: {recent_email_summary}
Recent client questions: {recent_client_questions}
Financial summary: {finance_summary}
""",
        
        'long': f"""PROMPT

You are a skilled financial advisor preparing for an upcoming meeting with {client_name}, who works at {company_name}. The meeting will focus on the following topic: {meeting_description}.

Below is compiled input from multiple sources:
- Past email summaries
- Recent email discussion points
- Recent client questions
- Relevant financial data (industry performance, client holdings, overall economic conditions)

Your task:
Create a comprehensive briefing document for internal use, to help prepare the meeting attendees. The briefing should include only relevant content and exclude any discussion about scheduling, availability, or meeting logistics.

Format the report using the following structure:

1. Past Email Summary
 - Write a concise paragraph summarizing earlier correspondence from {email_summary}.

2. Recent Email Topics
 - Present the content of {recent_email_summary} as a bullet-point list, focusing on key updates and discussion items.

3. Recent Client Questions
 - Use the list in {recent_client_questions}.
 - Present as a numbered list.
 - Exclude any questions related to logistics, availability, or scheduling.
 - If there were no questions provided in {recent_client_questions}, then omit this section. If no client questions were asked, then skip the section and do not state whether client questions were asked.

4. Financial Overview
 Use {finance_summary} to write a paragraph summarizing relevant financial data, including:
 - Industry trends
 - Performance of the client's holdings
 - Broader economic indicators

Inputs:

Past email summary: {email_summary}

Recent email summary: {recent_email_summary}

Recent client questions: {recent_client_questions}

Financial summary: {finance_summary}
"""
    }
    
    # Select the appropriate prompt based on report_length
    combined_prompt = report_formats.get(report_length.lower(), report_formats['long'])

    
   
    
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

