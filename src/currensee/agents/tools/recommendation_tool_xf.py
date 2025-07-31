from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import silhouette_score
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import re

#


def produce_recommendations(state):
    if not ENABLE_RECOMMENDATION:
        # Defualt Recommendation disabled
        return state
    
    # Convert report length to score
    section_level_to_score = {
        "none": 0.0,
        "short": 0.5,
        "full": 1.0
    }
    post_click_adjustment = {
        "more": 0.3,
        "less": -0.3
    }

    historical = state.get("report_type_preferences", {})
    post_feedback = state.get("click_feedback", {})

    content_accuracy = state.get("content_matching_metric", 1.0)
    contact_accuracy = state.get("contact_matching_metric", 1.0)
    accuracy_weight = (content_accuracy + contact_accuracy) / 2


    meeting_cat = state.get("meeting_category", None)
    
    # Scoring based on saved user preferences, past clicks and past accuracy in report_type selection
    scores = {}
    for section, level in historical.items():
        base_score = section_level_to_score.get(level, 0)
        adjustment = post_click_adjustment.get(post_feedback.get(section, ""), 0)
        adjusted_score = base_score + adjustment * accuracy_weight
        scores[section] = min(max(adjusted_score, 0), 1)


    # Assign cluster profiles per meeting category 
    cluster_profiles = {
        "Finance": {
            "finance_pref": 0.9,
            "client_news_detail": 0.4,
            "macro_news_detail": 0.3,
            "past_meeting_detail": 0.7
        },
        "Customer Relationship": {
            "finance_pref": 0.3,
            "client_news_detail": 0.8,
            "macro_news_detail": 0.7,
            "past_meeting_detail": 0.4
        },
        "Annual Review": {
            "finance_pref": 0.7,
            "client_news_detail": 0.5,
            "macro_news_detail": 0.6,
            "past_meeting_detail": 0.8
        },
        "Regulatory": {
            "finance_pref": 0.2,
            "client_news_detail": 0.2,
            "macro_news_detail": 0.4,
            "past_meeting_detail": 0.3
        }
    }

    # Weight of cluster profile blending (tune POST implementation)
    cluster_weight = 0.3

    # Blend in cluster profile if category found
    if meeting_cat and meeting_cat in cluster_profiles:
        cluster_scores = cluster_profiles[meeting_cat]
        for section, cluster_score in cluster_scores.items():
            old_score = scores.get(section, 0)
            blended_score = (1 - cluster_weight) * old_score + cluster_weight * cluster_score
            scores[section] = min(max(blended_score, 0), 1)

    # Return new state with final scores and recommended levels
    new_state = state.copy()
    new_state["section_preferences"] = scores
    new_state["recommended_levels"] = {sec: score_to_level(sc) for sec, sc in scores.items()}

    return new_state
