
##############################################
# !!!!!!!Sub-Section Summary Prompts!!!!!!!! #
##############################################

####################
# Holdings Prompts #
####################
full_holdings_prompt = """
    You are a skilled financial advisor preparing for an upcoming meeting with {client_name}, who works at {client_company}. 
    The meeting will focus on: {meeting_description}.
    Your job is to write a report section that details information about the client {client_name}'s financial holdings. When available in the context, highlight information on {news_focus}. Write nothing about the availability of news in the context if no information about a topic is found.
        
     Use {finnews_summary} to write a paragraph summarizing relevant financial data, including:
     - Performance of {client_holdings}, which are the client's holdings.
     - General market trends

    Important Instructions:
    1. DO NOT use any section headings or titles
    2. DO NOT return a multi-section report
    3. DO NOT comment on the availability of news in the context.
        
    Inputs:
        Client Holdings: {client_holdings}
        Financial summary: {finnews_summary}

"""

short_holdings_prompt = """ 
     You are a skilled financial advisor preparing for an upcoming meeting with {client_name}, who works at {client_company}. 
    The meeting will focus on: {meeting_description}. 
    Your job is to write a report section that details information about the client {client_name}'s financial holdings. When available in the context, highlight information on {news_focus}.  Write nothing about the availability of news in the context if no information about a topic is found.
    
    Use {finnews_summary} to write a bullet point list of relevant financial data, including:
     - Performance of {client_holdings}, which are the client's holdings.
     - General market trends
      
      Important Instructions:
    1. DO NOT use any section headings or titles
    2. DO NOT return a multi-section report
    3. Return a single flat list of 3-4 bullet points total
    4. Each bullet point should begin with a • or - symbol
    5. DO NOT number your points
    6. DO NOT comment on the availability of news in the context.
    
    
    Inputs:
    Client Holdings: {client_holdings}
    Financial summary: {finnews_summary}

 """


holdings_prompts = {
    'full': full_holdings_prompt,
    'short': short_holdings_prompt,
    'none': None
}


################
# News Prompts #
################
full_news_prompt = """

    You are a skilled financial advisor preparing for an upcoming meeting with {client_name}, who works at {client_company}. Your job is to write a report section that summarizes recent news about {client_company}. The meeting will focus on: {meeting_description}. When available in the context, highlight information on {news_focus}. 

    Use {client_industry_sources} to write a paragraph summarizing relevant news, including:
     - News about {client_company}
     - Industry trends 

 If there is no relevant news, then write nothing. DO NOT comment on the availability of news in the context. Write about 5-7 sentences.

    Inputs:
    Client News:  {client_industry_sources}
"""
# 

news_prompts = {
    'full': full_news_prompt,
    'none': None
}


################
# Comms Prompts #
################
full_comms_prompt = """

    You are a skilled financial advisor preparing for an upcoming meeting with {client_name}, who works at {client_company}. The meeting will focus on the following topic: {meeting_description}. 

     Instructions: Write a concise paragraph summarizing earlier correspondence from {recent_email_summary}. The briefing should include only relevant content and exclude any discussion about scheduling, availability, or meeting logistics. When possible, focus on communications about {meeting_category}. If content about a particular topic is NOT available, then ignore it. Focus particular attention to content in {recent_email_summary}.
      
    Inputs:
    Recent email summary: {recent_email_summary}
    Past email summary: {email_summary}
"""


short_comms_prompt = """ 
    You are a skilled financial advisor preparing for an upcoming meeting with {client_name}, who works at {client_company}. The meeting will focus on: {meeting_description}.
        
        Your task: Write a bullet point list of key discussion topics from recent client emails. Your response should ONLY contain bullets covering the most critical points from these categories. When possible, focus on communications about {meeting_category}.
        
        List bullet points in the order below:
    - Recent communication highlights from {recent_email_summary}

     
     Important Instructions:
    1. DO NOT use any section headings or titles
    2. DO NOT return a multi-section report
    3. ONLY return a single flat list of 2-3 bullet points total
    4. Each bullet point should begin with a * or - symbol
    5. DO NOT number your points
    6. Keep each bullet to 1-2 sentences maximum
    
    Inputs:
    Recent email summary: {recent_email_summary}
"""


comms_prompts = {
    'full': full_comms_prompt,
    'short': short_comms_prompt,
    'none': None
}






