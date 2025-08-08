"""
Feedback Processing Tool for LLM Analysis

This tool processes user feedback from the dynamic HTML thumbs up/down system
and uses LLM to determine user preferences for future report generation.
"""

import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

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


def analyze_feedback_with_llm(
    section_id: str, 
    is_positive: bool, 
    feedback_text: str,
    user_email: str,
    report_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Analyze user feedback using LLM to determine preference changes.
    
    Args:
        section_id: ID of the section being reviewed (e.g., 'client-news', 'recent-email')
        is_positive: True if thumbs up, False if thumbs down
        feedback_text: User's detailed feedback text
        user_email: Email of the user providing feedback
        report_context: Optional context about the current report structure
        
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
    
    prompt = f"""
    You are analyzing user feedback for a financial reporting system. The user has provided {sentiment} feedback about the "{section_id.replace('-', ' ')}" section of their report.

    User Email: {user_email}
    Section: {section_id}
    Feedback Sentiment: {'👍 Positive' if is_positive else '👎 Negative'}
    User Feedback Text: "{feedback_text}"

    Based on this feedback, analyze what the user wants and determine if any preference changes should be made.

    The system has these preference levels for each section:
    - "none": Don't include this section
    - "low": Minimal content 
    - "medium": Standard content
    - "high": Detailed content

    Current section maps to database column: {preference_column}

    Please analyze the feedback and provide:
    1. What specifically the user liked or disliked
    2. Whether they want MORE content, LESS content, DIFFERENT content, or NO CHANGE
    3. Recommended preference level change (if any)
    4. Specific content recommendations based on their feedback

    Respond in this JSON format:
    {{
        "analysis_summary": "Brief summary of what user wants",
        "content_preference": "MORE|LESS|DIFFERENT|NO_CHANGE",
        "recommended_level": "none|low|medium|high",
        "specific_recommendations": ["list", "of", "specific", "recommendations"],
        "confidence_score": 0.8
    }}
    """
    
    try:
        # Send to LLM for analysis
        message = HumanMessage(content=prompt)
        response = model.invoke([message])
        
        # Parse response (you may need to add JSON parsing here)
        analysis_result = {
            "section_id": section_id,
            "preference_column": preference_column,
            "user_email": user_email,
            "feedback_text": feedback_text,
            "is_positive": is_positive,
            "llm_response": response.content,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"✅ Feedback analyzed for user {user_email}, section {section_id}")
        return analysis_result
        
    except Exception as e:
        logger.error(f"❌ Error analyzing feedback: {str(e)}")
        return {"error": str(e)}


def store_feedback_analysis(analysis_result: Dict[str, Any]) -> bool:
    """
    Store the feedback analysis results in the database.
    
    Args:
        analysis_result: Results from analyze_feedback_with_llm
        
    Returns:
        Boolean indicating success
    """
    try:
        # TODO: Create a new table for feedback analysis storage
        # Example schema:
        """
        CREATE TABLE user_feedback_analysis (
            id SERIAL PRIMARY KEY,
            user_email VARCHAR(255),
            section_id VARCHAR(100),
            preference_column VARCHAR(100),
            is_positive BOOLEAN,
            feedback_text TEXT,
            llm_analysis JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # For now, just log the analysis
        logger.info(f"📊 Storing feedback analysis: {analysis_result}")
        
        # In a real implementation, you would:
        # 1. Insert the analysis into user_feedback_analysis table
        # 2. Potentially update the user's preferences in the preferences table
        # 3. Track patterns across multiple feedback submissions
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error storing feedback analysis: {str(e)}")
        return False


def update_user_preferences_from_feedback(
    user_email: str,
    preference_changes: Dict[str, str]
) -> bool:
    """
    Update user preferences based on feedback analysis.
    
    Args:
        user_email: Email of the user
        preference_changes: Dictionary mapping preference columns to new values
        
    Returns:
        Boolean indicating success
    """
    try:
        # TODO: Implement preference update logic
        # This would involve:
        # 1. Getting current user preferences
        # 2. Applying the recommended changes
        # 3. Creating a new preference record with updated timestamp
        
        logger.info(f"🔄 Updating preferences for {user_email}: {preference_changes}")
        
        # Example implementation:
        """
        current_time = datetime.now()
        
        # Get current preferences
        current_prefs = get_current_user_preferences(user_email)
        
        # Apply changes
        for column, new_value in preference_changes.items():
            current_prefs[column] = new_value
        
        # Insert new preference record
        insert_new_preference_record(user_email, current_prefs, current_time)
        """
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error updating user preferences: {str(e)}")
        return False


# Integration function to be called from the frontend
def process_user_feedback(
    section_id: str,
    is_positive: bool, 
    feedback_text: str,
    user_email: str,
    meeting_timestamp: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main function to process user feedback from the HTML form submission.
    
    This is the function that should be called from your web backend when
    the user submits feedback through the thumbs up/down interface.
    
    Args:
        section_id: Section being rated
        is_positive: Thumbs up (True) or thumbs down (False)
        feedback_text: User's detailed feedback
        user_email: User's email address
        meeting_timestamp: Optional timestamp of the meeting/report
        
    Returns:
        Processing results
    """
    
    logger.info(f"🔄 Processing feedback from {user_email} for section {section_id}")
    
    # Step 1: Analyze feedback with LLM
    analysis = analyze_feedback_with_llm(
        section_id=section_id,
        is_positive=is_positive,
        feedback_text=feedback_text,
        user_email=user_email
    )
    
    if "error" in analysis:
        return {"success": False, "error": analysis["error"]}
    
    # Step 2: Store the analysis
    stored = store_feedback_analysis(analysis)
    
    if not stored:
        return {"success": False, "error": "Failed to store analysis"}
    
    # Step 3: Apply preference changes if recommended
    # TODO: Parse LLM response to extract preference changes
    # preference_changes = extract_preference_changes_from_analysis(analysis)
    # if preference_changes:
    #     update_user_preferences_from_feedback(user_email, preference_changes)
    
    return {
        "success": True,
        "message": "Feedback processed successfully",
        "analysis_summary": analysis.get("analysis_summary", "Feedback analyzed"),
        "section_id": section_id
    }


# Example usage in a web endpoint:
"""
@app.route('/api/submit-feedback', methods=['POST'])
def submit_feedback():
    data = request.json
    
    result = process_user_feedback(
        section_id=data['section_id'],
        is_positive=data['is_positive'],
        feedback_text=data['feedback_text'],
        user_email=data['user_email']
    )
    
    return jsonify(result)
"""
