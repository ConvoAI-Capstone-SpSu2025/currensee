"""
Secure Graph Wrapper - Protected execution of CurrenSee's compiled_graph with input guardrails

This module provides a secure wrapper for compiled_graph.invoke() that enforces
input validation and security guardrails for notebook and CLI usage.
"""

import logging
import time
from typing import Dict, Any

from currensee.agents.complete_graph import compiled_graph
from currensee.core.input_guardrails import CurrenSeeInputGuardrails
from currensee.utils.security_utils import (
    SecurityEventLogger, 
    process_validation_results,
    get_sanitized_inputs,
    log_security_metrics
)

logger = logging.getLogger(__name__)
security_logger = SecurityEventLogger()


def secure_graph_invoke(init_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Secure wrapper for compiled_graph.invoke() with comprehensive input guardrails.
    
    This function enforces the same security validation as the FastAPI endpoint
    for notebook and CLI usage of the CurrenSee multi-agent graph.
    
    Args:
        init_state: Dictionary containing:
            - user_email: Email of the investment banker (required)  
            - client_name: Name of the client (required)
            - client_email: Email address of the client (required)
            - meeting_timestamp: Timestamp in format "YYYY-MM-DD HH:MM:SS" (required)
            - meeting_description: Description of the meeting (required)
            - report_length: Optional, defaults to "long"
    
    Returns:
        Graph execution results from compiled_graph.invoke()
        
    Raises:
        ValueError: If required fields are missing or validation fails
        SecurityError: If input fails security validation
    """
    start_time = time.time()
    
    # Validate required fields
    required_fields = ["user_email", "client_name", "client_email", "meeting_timestamp", "meeting_description"]
    missing_fields = [field for field in required_fields if field not in init_state or not init_state[field]]
    
    if missing_fields:
        error_msg = f"Missing required fields: {missing_fields}"
        logger.error(error_msg)
        security_logger.log_validation_failure(
            "missing_fields", 
            init_state.get("user_email", "unknown"), 
            [f"Missing: {', '.join(missing_fields)}"], 
            "high"
        )
        raise ValueError(error_msg)
    
    logger.info(f"Starting secure graph execution for user: {init_state['user_email']}, client: {init_state['client_name']}")
    
    try:
        # Run comprehensive security validation
        guardrails = CurrenSeeInputGuardrails()
        validation_results = guardrails.validate_comprehensive(
            user_email=init_state["user_email"],
            client_name=init_state["client_name"],
            client_email=init_state["client_email"],
            meeting_timestamp=init_state["meeting_timestamp"],
            meeting_description=init_state["meeting_description"]
        )
        
        # Log security metrics
        validation_time_ms = (time.time() - start_time) * 1000
        log_security_metrics(validation_results, validation_time_ms)
        
        # Process validation results (raises exception if validation fails)
        try:
            process_validation_results(validation_results, init_state["client_email"])
        except Exception as e:
            # Log security failure and re-raise
            security_logger.log_validation_failure(
                "comprehensive_validation", 
                init_state["user_email"], 
                [str(e)], 
                validation_results.get("risk_level", "high")
            )
            raise e
        
        # Get sanitized inputs for safe processing
        sanitized_inputs = get_sanitized_inputs(validation_results)
        
        # Prepare secure state for graph execution
        secure_state = {
            "user_email": init_state["user_email"],  # User email kept as-is (already validated)
            "client_name": sanitized_inputs.get("client_name", init_state["client_name"]),
            "client_email": init_state["client_email"],  # Email format already validated
            "meeting_timestamp": init_state["meeting_timestamp"],  # Timestamp format already validated
            "meeting_description": sanitized_inputs.get("meeting_description", init_state["meeting_description"]),
            "report_length": init_state.get("report_length", "long")
        }
        
        # Execute the compiled graph with sanitized inputs
        logger.info(f"Executing graph with validated inputs for client: {init_state['client_name']}")
        result = compiled_graph.invoke(secure_state)
        
        execution_time = time.time() - start_time
        logger.info(f"Secure graph execution completed in {execution_time:.2f}s for user: {init_state['user_email']}")
        
        # Log successful execution
        security_logger.log_validation_success(init_state["user_email"], execution_time)
        
        return result
        
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Secure graph execution failed after {execution_time:.2f}s: {str(e)}")
        
        # Log security event for failed execution
        security_logger.log_validation_failure(
            "graph_execution", 
            init_state.get("user_email", "unknown"), 
            [str(e)], 
            "high"
        )
        raise


def validate_init_state_format(init_state: Dict[str, Any]) -> None:
    """
    Validate the format and structure of init_state before processing.
    
    Args:
        init_state: Dictionary to validate
        
    Raises:
        ValueError: If init_state format is invalid
    """
    if not isinstance(init_state, dict):
        raise ValueError("init_state must be a dictionary")
    
    # Check for common mistakes in field names
    field_corrections = {
        "user": "user_email",
        "banker_email": "user_email", 
        "client": "client_name",
        "email": "client_email",
        "timestamp": "meeting_timestamp",
        "description": "meeting_description"
    }
    
    suggestions = []
    for wrong_field, correct_field in field_corrections.items():
        if wrong_field in init_state and correct_field not in init_state:
            suggestions.append(f"Did you mean '{correct_field}' instead of '{wrong_field}'?")
    
    if suggestions:
        raise ValueError(f"Field name issues detected: {'; '.join(suggestions)}")


# Convenience function for backwards compatibility
def protected_graph_invoke(init_state: Dict[str, Any]) -> Dict[str, Any]:
    """Alias for secure_graph_invoke for backwards compatibility"""
    return secure_graph_invoke(init_state)
