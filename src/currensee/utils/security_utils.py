"""
Security utilities for CurrenSee input validation and logging.

This module provides utility functions for security event logging, 
validation result processing, and integration with FastAPI error handling.
"""

import logging
from datetime import datetime
from typing import Dict, Optional
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class SecurityEventLogger:
    """
    Centralized security event logging for CurrenSee guardrails.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("currensee.security")
        
    def log_validation_failure(self, validation_type: str, client_email: str, 
                             issues: list, risk_level: str, request_data: Optional[Dict] = None):
        """
        Log security validation failures with appropriate detail level.
        
        Args:
            validation_type: Type of validation that failed (e.g., 'client_boundary')
            client_email: Client email for context (will be partially masked)
            issues: List of specific issues detected
            risk_level: Risk level (low, medium, high, critical)
            request_data: Optional request data for debugging (sensitive data will be masked)
        """
        masked_email = self._mask_email(client_email)
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "validation_failure",
            "validation_type": validation_type,
            "client_email": masked_email,
            "risk_level": risk_level,
            "issues_count": len(issues),
            "issues": issues[:3]  # Log first 3 issues to avoid log spam
        }
        
        if risk_level in ["high", "critical"]:
            self.logger.error(f"Security validation failure: {log_entry}")
        elif risk_level == "medium":
            self.logger.warning(f"Security validation warning: {log_entry}")
        else:
            self.logger.info(f"Security validation info: {log_entry}")
    
    def log_validation_success(self, client_email: str, validation_types: list):
        """
        Log successful validation events.
        
        Args:
            client_email: Client email (will be masked)
            validation_types: List of validation types that passed
        """
        masked_email = self._mask_email(client_email)
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "validation_success",
            "client_email": masked_email,
            "validations_passed": validation_types
        }
        
        self.logger.info(f"Input validation successful: {log_entry}")
    
    def _mask_email(self, email: str) -> str:
        """
        Mask email address for logging (keep first 2 chars and domain).
        
        Args:
            email: Email address to mask
            
        Returns:
            Masked email address
        """
        try:
            if "@" not in email:
                return "***invalid***"
            
            local, domain = email.split("@", 1)
            if len(local) <= 2:
                masked_local = "*" * len(local)
            else:
                masked_local = local[:2] + "*" * (len(local) - 2)
            
            return f"{masked_local}@{domain}"
        except Exception:
            return "***error***"


def process_validation_results(validation_results: Dict, client_email: str) -> None:
    """
    Process validation results and raise appropriate HTTP exceptions for failures.
    
    Args:
        validation_results: Results from CurrenSeeInputGuardrails.validate_comprehensive()
        client_email: Client email for logging context
        
    Raises:
        HTTPException: If validation fails with appropriate status code
    """
    security_logger = SecurityEventLogger()
    
    if validation_results["overall_valid"]:
        # Log successful validation
        validation_types = list(validation_results["validation_details"].keys())
        security_logger.log_validation_success(client_email, validation_types)
        return
    
    # Process validation failures
    risk_level = validation_results["risk_level"]
    all_issues = []
    
    for validation_type, results in validation_results["validation_details"].items():
        if not results["valid"]:
            all_issues.extend(results["issues"])
            security_logger.log_validation_failure(
                validation_type, client_email, results["issues"], results["risk_level"]
            )
    
    # Determine HTTP status code based on risk level
    if risk_level == "critical":
        status_code = 400  # Bad Request - likely malicious
        error_message = "Request blocked due to security policy violation"
    elif risk_level == "high":
        status_code = 403  # Forbidden - policy violation
        error_message = "Request denied due to security concerns"
    elif risk_level == "medium":
        status_code = 422  # Unprocessable Entity - validation error
        error_message = "Request validation failed"
    else:
        status_code = 400  # Bad Request - general validation
        error_message = "Invalid request format"
    
    # For security reasons, don't expose detailed error messages to client
    # in production - log them but return generic message
    logger.error(f"Validation failure details: {all_issues}")
    
    raise HTTPException(
        status_code=status_code,
        detail={
            "error": error_message,
            "code": f"SECURITY_VALIDATION_{risk_level.upper()}",
            "timestamp": datetime.now().isoformat()
        }
    )


def get_sanitized_inputs(validation_results: Dict) -> Dict[str, str]:
    """
    Extract sanitized inputs from validation results.
    
    Args:
        validation_results: Results from comprehensive validation
        
    Returns:
        Dictionary of sanitized input values
    """
    return validation_results.get("sanitized_inputs", {})


def log_security_metrics(validation_results: Dict, execution_time_ms: float):
    """
    Log security validation metrics for monitoring and analysis.
    
    Args:
        validation_results: Validation results
        execution_time_ms: Time taken for validation in milliseconds
    """
    metrics_logger = logging.getLogger("currensee.security.metrics")
    
    # Fixed: Check the correct key structure
    failed_validations = []
    if "validation_details" in validation_results:
        for name, result in validation_results["validation_details"].items():
            # Some results have 'valid' key, others might have different structure
            if isinstance(result, dict):
                if "valid" in result and not result["valid"]:
                    failed_validations.append(name)
                elif "issues" in result and len(result.get("issues", [])) > 0:
                    failed_validations.append(name)
    
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "validation_time_ms": execution_time_ms,
        "overall_valid": validation_results.get("overall_valid", False),
        "risk_level": validation_results.get("risk_level", "unknown"),
        "validation_count": len(validation_results.get("validation_details", {})),
        "failed_validations": failed_validations
    }
    
    metrics_logger.info(f"Security validation metrics: {metrics}")
