
##############################################
# !!!!!!!Sub-Section Summary Prompts!!!!!!!! #
##############################################

####################
# Holdings Prompts #
####################
full_holdings_prompt = """
    You are a skilled financial advisor preparing for an upcoming meeting with {client_name}, who works at {client_company}. 
    The meeting will focus on: {meeting_description}.
    Your job is to write a report section that details information about the client {client_name}'s financial holdings. When possible, highlight information on {news_focus}.
        
     Use {finnews_summary} to write a paragraph summarizing relevant financial data, including:
     - Performance of {client_holdings}, which are the client's holdings.
     - If there is news about about {client_holdings} on the topic of {news_focus} in the provided context, then highlight it, otherwise do not comment about {news_focus}. If there was no news about {news_focus}, the DO NOT comment about it.
   
    
    Important Instructions:
    1. DO NOT use any section headings or titles
    2. DO NOT return a multi-section report
        
    Inputs:
        Client Holdings: {client_holdings}
        Financial summary: {finnews_summary}
        Summary focus: {news_focus}

"""
#3. If there is no news in the provided context about {news_focus}, then report other news about client's holdings. 
short_holdings_prompt = """ 
     You are a skilled financial advisor preparing for an upcoming meeting with {client_name}, who works at {client_company}. 
    The meeting will focus on: {meeting_description}. 
    Your job is to write a report section that details information about the client {client_name}'s financial holdings. When possible, highlight information on {news_focus}. 
    
    Use {finnews_summary} to write a bullet point list of relevant financial data, including:
     - Performance of {client_holdings}, which are the client's holdings.
     - If there is news about about {client_holdings} on the topic of {news_focus} in the provided context, then highlight it, otherwise do not comment about {news_focus}. If there was no news about {news_focus}, the DO NOT comment about it.
      
      Important Instructions:
    1. DO NOT use any section headings or titles
    2. DO NOT return a multi-section report
    3. Return a single flat list of 3-4 bullet points total
    4. Each bullet point should begin with a • or - symbol
    5. DO NOT number your points
    
    
    Inputs:
    Client Holdings: {client_holdings}
    Financial summary: {finnews_summary}
    Summary focus: {news_focus}
 """

#DO NOT comment on whether you could find news about {news_focus}.  6. If there is no news in the provided context about {news_focus}, then report other news about client's holdings.

holdings_prompts = {
    'full': full_holdings_prompt,
    'short': short_holdings_prompt,
    'none': None
}


################
# News Prompts #
################
full_news_prompt = """

    You are a skilled financial advisor preparing for an upcoming meeting with {client_name}, who works at {client_company}. Your job is to write a report section that summarizes recent news about {client_company}. The meeting will focus on: {meeting_description}. When possible, highlight information on {news_focus} that you can find in Client News.

    Use {client_industry_sources} to write a paragraph summarizing relevant news, including:
     - News about {client_company}
     - If there is information about news about {news_focus} then highlight it, otherwise do not comment about {news_focus}. If there was no news about {news_focus}, the DO NOT comment about it.
     - Industry trends 

 If there is no relevant news, then write nothing. 

    Inputs:
    Client News:  {client_industry_sources}
    Summary focus: {news_focus}

"""


news_prompts = {
    'full': full_news_prompt,
    'none': None
}


################
# Comms Prompts #
################
full_comms_prompt = """

    You are a skilled financial advisor preparing for an upcoming meeting with {client_name}, who works at {client_company}. The meeting will focus on the following topic: {meeting_description}. 
    
    Below is compiled input from multiple sources:
    - Past email summaries
    - Recent email discussion points
    - Recent client questions
    
    Your task:
    Create a comprehensive briefing document for internal use, to help prepare the meeting attendees. The briefing should include only relevant content and exclude any discussion about scheduling, availability, or meeting logistics. When possible, focus on communications about {meeting_category}.
    
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
"""


short_comms_prompt = """ 
    You are a skilled financial advisor preparing for an upcoming meeting with {client_name}, who works at {client_company}. The meeting will focus on: {meeting_description}.
        
        Your task: Write a bullet point list of key discussion topics from recent client emails. Your response should ONLY contain bullets covering the most critical points from these categories. When possible, focus on communications about {meeting_category}.
        
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


comms_prompts = {
    'full': full_comms_prompt,
    'short': short_comms_prompt,
    'none': None
}






