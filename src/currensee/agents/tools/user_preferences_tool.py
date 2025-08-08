"""
Combined User Preferences and Feedback Processing Tool

This tool combines functionality for:
1. Retrieving initial user preferences 
2. Processing user feedback from the dynamic HTML thumbs up/down system
3. Updating user preferences based on LLM analysis of feedback
"""

import json
import logging
import pandas as pd
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from sqlalchemy import insert

from currensee.core import get_model, settings
from currensee.agents.tools.base import SupervisorState
from currensee.utils.db_utils import create_pg_engine
from langchain_core.messages import HumanMessage

logger = logging.getLogger(__name__)

# === Model ===
model = get_model(settings.DEFAULT_MODEL)

# === DB Connection ===
DB_NAME = "crm_outlook"
engine = create_pg_engine(db_name=DB_NAME)


def retrieve_current_user_preferences(state: SupervisorState) -> dict:
    """
    Retrieve the current user preferences for report formatting and detail levels.
    
    Args:
        state: SupervisorState containing user_email and meeting_timestamp
        
    Returns:
        Updated state with user preferences
    """
    try:
        user_email = state["user_email"] if "user_email" in state else state.get("client_email", "")
        meeting_timestamp = state["meeting_timestamp"]

        # Get the most recent preferences as of the meeting timestamp
        mx_dt_df = pd.read_sql(f"""
        select coalesce(as_of_date, '2023-01-23 10:00:00') as as_of_date
        from (
        SELECT max(p.as_of_date) as as_of_date
        FROM preferences p
        where p.email = '{user_email}'
        and as_of_date <= '{meeting_timestamp}')a
        """, con=engine)
        
        max_dt = mx_dt_df['as_of_date'].iloc[0]
        
        query_str = f"""
        SELECT p.as_of_date
        , p.employee_first_name
        , p.employee_last_name
        , p.finance_detail
        , p.news_detail
        , p.macro_news_detail
        , p.past_meeting_detail 
        , p.email    
        FROM preferences p
        where p.email = '{user_email}' and p.as_of_date = '{max_dt}'
        """

        pref_df = pd.read_sql(query_str, con=engine)
        
        holdings_detail = pref_df["finance_detail"].iloc[0]
        client_news_detail = pref_df["news_detail"].iloc[0]
        macro_news_detail = pref_df["macro_news_detail"].iloc[0]
        past_meeting_detail = pref_df["past_meeting_detail"].iloc[0]

        new_state = state.copy()
        new_state["holdings_detail"] = holdings_detail
        new_state["client_news_detail"] = client_news_detail
        new_state["macro_news_detail"] = macro_news_detail
        new_state["past_meeting_detail"] = past_meeting_detail
        
        logger.info(f"✅ Retrieved preferences for user {user_email}: holdings={holdings_detail}, news={client_news_detail}, macro={macro_news_detail}, meetings={past_meeting_detail}")
        
        return new_state
        
    except Exception as e:
        logger.error(f"❌ Error retrieving user preferences: {str(e)}")
        # Return default preferences if retrieval fails
        new_state = state.copy()
        new_state["holdings_detail"] = "full"
        new_state["client_news_detail"] = "full"
        new_state["macro_news_detail"] = "full"
        new_state["past_meeting_detail"] = "full"
        return new_state


def analyze_feedback_with_llm(
    section_id: str, 
    is_positive: bool, 
    feedback_text: str,
    user_email: str,
    current_preferences: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    Analyze user feedback using LLM to determine preference changes.
    
    Args:
        section_id: ID of the section being reviewed (e.g., 'client-news', 'recent-email')
        is_positive: True if thumbs up, False if thumbs down
        feedback_text: User's detailed feedback text
        user_email: Email of the user providing feedback
        current_preferences: Current user preference settings
        
    Returns:
        Dictionary containing analysis results and recommended preference changes
    """
    
    # Map section IDs to preference columns in the database
    section_mapping = {
        'client-news': 'news_detail',
        'recent-email': 'past_meeting_detail', 
        'client-questions': 'past_meeting_detail',
        'client-interactions': 'past_meeting_detail',
        'holdings-news': 'finance_detail',
        'macro-data': 'macro_news_detail',
        'macro-news': 'macro_news_detail',
        'financial-summary': 'finance_detail'
    }
    
    preference_column = section_mapping.get(section_id)
    if not preference_column:
        logger.warning(f"Unknown section ID: {section_id}")
        return {"error": f"Unknown section ID: {section_id}"}
    
    # Create LLM prompt for feedback analysis
    sentiment = "positive" if is_positive else "negative"
    current_level = current_preferences.get(preference_column, "none") if current_preferences else "none"
    
    prompt = f"""
    You are analyzing user feedback for a financial reporting system. The user has provided {sentiment} feedback about the "{section_id.replace('-', ' ')}" section of their report.

    User Email: {user_email}
    Section: {section_id}
    Database Column: {preference_column}
    Current Preference Level: {current_level}
    Feedback Sentiment: {'👍 Positive' if is_positive else '👎 Negative'}
    User Feedback Text: "{feedback_text}"

    Based on this feedback, analyze what the user wants and determine if any preference changes should be made.

    The system has these preference levels for each section:
    - "none": Don't include this section
    - "short": Minimal content
    - "full": Detailed content with extra analysis

    Please analyze the feedback and provide:
    1. What specifically the user liked or disliked
    2. Whether they want MORE content, LESS content, DIFFERENT content, or NO CHANGE
    3. Recommended preference level change (if any)
    4. Specific content recommendations based on their feedback

    Respond in this JSON format:
    {{
        "analysis_summary": "Brief summary of what user wants",
        "content_preference": "MORE|LESS|DIFFERENT|NO_CHANGE",
        "current_level": "{current_level}",
        "recommended_level": "none|short|full",
        "specific_recommendations": ["list", "of", "specific", "recommendations"],
        "confidence_score": 0.8,
        "reasoning": "Explanation of why this change is recommended"
    }}
    """
    
    try:
        # Send to LLM for analysis
        message = HumanMessage(content=prompt)
        response = model.invoke([message])
        
        # Try to parse JSON response
        try:
            llm_analysis = json.loads(response.content.strip())
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            llm_analysis = {
                "analysis_summary": f"User provided {sentiment} feedback about {section_id}",
                "content_preference": "NO_CHANGE",
                "current_level": current_level,
                "recommended_level": current_level,
                "specific_recommendations": [],
                "confidence_score": 0.5,
                "reasoning": "Unable to parse LLM response"
            }
        
        analysis_result = {
            "section_id": section_id,
            "preference_column": preference_column,
            "user_email": user_email,
            "feedback_text": feedback_text,
            "current_level": current_level,
            "recommended_level": llm_analysis.get('recommended_level', 'unknown'),
            "raw_llm_response": response.content,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"✅ Feedback analyzed for user {user_email}, section {section_id}. Recommendation: {llm_analysis.get('recommended_level', 'unknown')}")
        return analysis_result
        
    except Exception as e:
        logger.error(f"❌ Error analyzing feedback: {str(e)}")
        return {"error": str(e)}



def update_user_preferences_from_feedback(
    preference_update_timestamp: str,
    user_email: str,
    preference_column: str,
    new_preference_level: str,
    current_preferences: dict
) -> bool:
    """
    Update user preferences based on feedback analysis.
    
    Args:
        user_email: Email of the user
        preference_column: The preference column to update
        new_preference_level: New preference level 
        current_preferences: Current preference settings
        
    Returns:
        Boolean indicating success
    """
    try:

        # Update the specific preference
        updated_preferences = current_preferences.copy()
        updated_preferences[preference_column] = new_preference_level
        
        logger.info(f"🔄 Updating {preference_column} preference for {user_email}: {current_preferences.get(preference_column)} -> {new_preference_level}")

        new_pref_record = {
            'as_of_date': preference_update_timestamp,
            'email': user_email,
            'employee_first_name': updated_preferences.get('employee_first_name'),
            'employee_last_name': updated_preferences.get('employee_last_name'),
            'finance_detail': updated_preferences.get('finance_detail'),
            'news_detail': updated_preferences.get('news_detail', 'medium'),
            'macro_news_detail': updated_preferences.get('macro_news_detail', 'medium'),
            'past_meeting_detail': updated_preferences.get('past_meeting_detail', 'medium'),
    
        }
        
        df = pd.DataFrame([new_pref_record])
        df.to_sql('preferences', engine, if_exists='append', index=False)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error updating user preferences: {str(e)}")
        return False


def process_user_feedback(
    section_id: str,
    is_positive: bool, 
    feedback_text: str,
    user_email: str,
    current_preferences: Optional[Dict[str, str]] = None,
    meeting_timestamp: Optional[str] = None,
    auto_update_preferences: bool = True
) -> Dict[str, Any]:
    """
    Main function to process user feedback from the HTML form submission.
    
    This function handles the complete feedback processing workflow:
    1. Analyze feedback with LLM
    2. Store analysis results  
    3. Optionally update user preferences
    
    Args:
        section_id: Section being rated
        is_positive: Thumbs up (True) or thumbs down (False)
        feedback_text: User's detailed feedback
        user_email: User's email address
        current_preferences: Current user preference settings
        meeting_timestamp: Optional timestamp of the meeting/report
        auto_update_preferences: Whether to automatically update preferences
        
    Returns:
        Processing results
    """
    
    logger.info(f"🔄 Processing feedback from {user_email} for section {section_id}")

    # Get the most recent preferences as of the meeting timestamp
    mx_dt_df = pd.read_sql(f"""
    select coalesce(as_of_date, '2023-01-23 10:00:00') as as_of_date
    from (
    SELECT max(p.as_of_date) as as_of_date
    FROM preferences p
    where p.email = '{user_email}'
    and as_of_date <= '{meeting_timestamp}')a
    """, con=engine)
    
    max_dt = mx_dt_df['as_of_date'].iloc[0]
    
    query_str = f"""
    SELECT p.as_of_date
    , p.employee_first_name
    , p.employee_last_name
    , p.finance_detail
    , p.news_detail
    , p.macro_news_detail
    , p.past_meeting_detail 
    , p.email    
    FROM preferences p
    where p.email = '{user_email}' and p.as_of_date = '{max_dt}'
    """
    pref_df = pd.read_sql(query_str, con=engine)
    current_preferences = pref_df.iloc[0]
    
    # Step 1: Analyze feedback with LLM
    analysis = analyze_feedback_with_llm(
        section_id=section_id,
        is_positive=is_positive,
        feedback_text=feedback_text,
        user_email=user_email,
        current_preferences=current_preferences
    )
    
    if "error" in analysis:
        return {"success": False, "error": analysis["error"]}
    
    # Step 2: Apply preference changes if recommended and auto-update is enabled
    llm_analysis = analysis.get("llm_analysis", {})
    recommended_level = llm_analysis.get("recommended_level")
    current_level = llm_analysis.get("current_level")
    confidence_score = llm_analysis.get("confidence_score", 0.0)
    
    preference_updated = False
    if (auto_update_preferences and 
        recommended_level and 
        recommended_level != current_level and 
        confidence_score >= 0.7 and  # Only update if confident
        current_preferences):
        
        preference_column = analysis.get("preference_column")
        if preference_column:
            updated = update_user_preferences_from_feedback(
                preference_update_timestamp=analysis['timestamp'],
                user_email=user_email,
                preference_column=preference_column,
                new_preference_level=recommended_level,
                current_preferences=current_preferences
            )
            preference_updated = updated
    
    return {
        "success": True,
        "message": "Feedback processed successfully",
        "analysis_summary": llm_analysis.get("analysis_summary", "Feedback analyzed"),
        "section_id": section_id,
        "preference_updated": preference_updated,
        "recommended_change": f"{current_level} -> {recommended_level}" if recommended_level != current_level else "No change recommended",
        "confidence_score": confidence_score
    }


# Example web endpoint integration:
"""
from flask import Flask, request, jsonify
from currensee.agents.tools.user_preferences_tool import process_user_feedback, retrieve_current_user_preferences

@app.route('/api/submit-feedback', methods=['POST'])
def submit_feedback():
    data = request.json
    
    # Get current user preferences for context
    user_email = data['user_email']
    meeting_timestamp = data.get('meeting_timestamp', datetime.now().isoformat())
    
    # Create minimal state for preference retrieval
    state = {'user_email': user_email, 'meeting_timestamp': meeting_timestamp}
    updated_state = retrieve_current_user_preferences(state)
    
    current_prefs = {
        'finance_detail': updated_state.get('holdings_detail', 'medium'),
        'news_detail': updated_state.get('client_news_detail', 'medium'),
        'macro_news_detail': updated_state.get('macro_news_detail', 'medium'),
        'past_meeting_detail': updated_state.get('past_meeting_detail', 'medium')
    }
    
    # Process the feedback
    result = process_user_feedback(
        section_id=data['section_id'],
        is_positive=data['is_positive'],
        feedback_text=data['feedback_text'],
        user_email=user_email,
        current_preferences=current_prefs,
        meeting_timestamp=meeting_timestamp
    )
    
    return jsonify(result)
"""
