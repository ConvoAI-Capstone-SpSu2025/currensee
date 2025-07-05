import logging
from dataclasses import dataclass

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.graph.state import CompiledStateGraph

from currensee.agents.tools.base import SupervisorState
from currensee.core import get_model, settings
from currensee.schema import AgentInfo

load_dotenv()

logger = logging.getLogger(__name__)
model = get_model(settings.DEFAULT_MODEL)


@dataclass
class Agent:
    description: str
    graph: CompiledStateGraph


# # Graph-specific utils


def summarize_all_outputs(state: SupervisorState) -> str:
    """
    Summarizes the outputs from all provided tools into one coherent summary.

    Parameters:
    - state: SupervisorState containing all tool outputs and configurations

    Returns:
    - A modified state with the final summary added
    """

    finance_summary = state["finnews_summary"]
    client_industry_sources = state["client_industry_sources"]
    client_holdings = state["client_holdings"]
    email_summary = state["email_summary"]
    company_name = state["client_company"]
    client_name = state["client_name"]
    meeting_description = state["meeting_description"]
    recent_email_summary = state["recent_email_summary"]
    recent_client_questions = state["recent_client_questions"]
    finance_detail = new_state["finance_detail"] 
    news_detail = new_state["news_detail"]
    macro_news_detail = new_state["macro_news_detail"]
    past_meeting_detail = new_state["past_meeting_detail"]



    # Log the report length being used
    print(f"\n===============================")
    print(f"Generating report with the following preferences: ")
    print(f" Finance Detail: {finance_detail} ")
    print(f" News Detail: {news_detail} ")
    print(f" Macro News Detail: {macro_news_detail}")
    print(f" Past Meeting Detail: {past_meeting_detail}")
    print(f"===============================\n")
    
    finance_holdings_formats = {
    "full" : f"""
        You are a skilled financial advisor preparing for an upcoming meeting with {client_name}, who works at {company_name}. The meeting will focus on: {meeting_description}. Your job is to write a report section that details information about the client {client_name}'s financial holdings.
        
     Use {finance_summary} to write a paragraph summarizing relevant financial data, including:
     - Performance of the client's holdings
     - Broader economic indicators
    
     Important Instructions:
    1. DO NOT use any section headings or titles
    2. DO NOT return a multi-section report
    
    Inputs:
        Client Holdings: {client_holdings}
        Financial summary: {finance_summary}

        """,
     "short" : f""" You are a skilled financial advisor preparing for an upcoming meeting with {client_name}, who works at {company_name}. Your job is to write a formatted list of the client {client_name}'s financial holdings.
    
    Write a list bullet point list of the holdings in {client_holdings}.
      
      Important Instructions:
    1. DO NOT use any section headings or titles
    2. DO NOT return a multi-section report
    3. Return a single flat list of 5-7 bullet points total
    4. Each bullet point should begin with a • or - symbol
    5. DO NOT number your points
    
    Inputs:
    Client Holdings: {client_holdings}
     """,
    "none": f"""  """      
    }
    
    finance_news_formats = {
        "full": f"""You are a skilled financial advisor preparing for an upcoming meeting with {client_name}, who works at {company_name}. Your job is to write a report section that summarizes recent news about {company_name}. The meeting will focus on: {meeting_description}.

    Use {client_industry_sources} to write a paragraph summarizing relevant news, including:
     - News about {company_name}
     - Industry trends 

     If there is no relevant news, then write nothing.

     Inputs:
    Client News:  {client_industry_sources}

         """
        , 
        "none": f"""  """    
    }

    client_comm_formats = {
        "full": f"""PROMPT

    You are a skilled financial advisor preparing for an upcoming meeting with {client_name}, who works at {company_name}. The meeting will focus on the following topic: {meeting_description}.
    
    Below is compiled input from multiple sources:
    - Past email summaries
    - Recent email discussion points
    - Recent client questions
    
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
     - Exclude any questions asked by Bankwell Financial
     - If there were no questions provided in {recent_client_questions}, then omit this section. If no client questions were asked, then skip the section and do not state whether client questions were asked.
    
    Inputs:
    Past email summary: {email_summary}
    Recent email summary: {recent_email_summary}
    Recent client questions: {recent_client_questions}
    """ ,
        "short": f""" You are a skilled financial advisor preparing for an upcoming meeting with {client_name}, who works at {company_name}. The meeting will focus on: {meeting_description}.
        
        Your task: Write a bullet point list of key discussion topics from recent client emails. Your response should ONLY contain bullets covering the most critical points from these categories. 
        
        List bullet points in the order below:
    - Recent communication highlights from {recent_email_summary}
    - Any critical client questions (If there were no questions provided in {recent_client_questions}, then do not state whether client questions were asked and skip this point). Exclude any questions asked by Bankwell Financial.
     
     Important Instructions:
    1. DO NOT use any section headings or titles
    2. DO NOT return a multi-section report
    3. ONLY return a single flat list of 3-5 bullet points total
    4. Each bullet point should begin with a • or - symbol
    5. DO NOT number your points
    6. Keep each bullet to 1-2 sentences maximum
    
    Inputs:
    Recent email summary: {recent_email_summary}
    Recent client questions: {recent_client_questions}
    """
    ,
  "none": f"""  """       
    }
    

    # Select the appropriate prompts based on preferences
    finance_holdings_prompt = finance_holdings_formats.get(finance_detail.lower(), finance_holdings_formats["full"])
    client_news_prompt = finance_news_formats.get(news_detail.lower(), finance_news_formats["full"])
    client_comm_prompt = client_comm_formats.get(past_meeting_detail.lower(), client_comm_formats["full"])

    
    # Create the messages to pass to the model
    messages_fin_hold = [HumanMessage(content=finance_holdings_prompt)]
    messages_client_news = [HumanMessage(content=client_news_prompt)]
    messages_client_coms = [HumanMessage(content=client_comm_prompt)]

    # Use the 'invoke' method for summarization
    summary_fin_hold = model.invoke(messages_fin_hold)
    summary_client_news = model.invoke(messages_client_news)
    summary_client_comms = model.invoke(messages_client_coms)

    new_state = state.copy()
    new_state["summary_fin_hold"] = summary_fin_hold.content
    new_state["summary_client_news"] = summary_client_news.content
    new_state["summary_client_comms"] = summary_client_comms.content
    # Access the message content correctly
    return new_state
