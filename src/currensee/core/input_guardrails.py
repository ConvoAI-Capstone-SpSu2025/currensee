"""
CurrenSee Input Guardrails - Custom Security Validation for Investment Banking LLM Agents

This module provides security validation for CurrenSee's multi-agent system,
focusing on client boundary enforcement, input sanitization, and meeting context validation.
"""

import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Union
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class CurrenSeeInputGuardrails:
    """
    Custom input validation and security guardrails for CurrenSee.
    
    Designed specifically for investment banking client meeting preparation workflows
    with focus on preventing cross-client data access and input-based attacks.
    """
    
    def __init__(self):
        # Suspicious patterns that could indicate injection attempts
        self.sql_injection_patterns = [
            r"('|(\\x27)|(\\x2D))",  # Single quotes and hex equivalents
            r"(\"|(\\x22))",         # Double quotes and hex equivalents  
            r"(;|\\x3B)",            # Semicolons
            r"(--|#|\\x23)",         # SQL comments
            r"(union|select|insert|update|delete|drop|create|alter|exec|execute)",  # SQL keywords
            r"(script|javascript|vbscript|onload|onerror)",  # Script injection
        ]
        
        # Patterns that might indicate attempts to access multiple clients
        self.cross_client_patterns = [
            r"(client|account|customer)\s*[ids]*\s*[=:]\s*[\[\(]",  # client_id=[...] or client:(...)
            r"(all|multiple|various|several)\s+(clients?|accounts?|customers?)",
            r"(and|or|,)\s+(client|account|customer)",
            r"(union|join)\s+(client|account|customer)",
        ]
        
        # Common disposable/suspicious email domains to flag
        self.suspicious_email_domains = {
            "10minutemail.com", "tempmail.org", "tempmail.com", "guerrillamail.com", 
            "mailinator.com", "yopmail.com", "temp-mail.org", "throwaway.email",
            "maildrop.cc", "sharklasers.com", "grr.la", "dispostable.com",
            "tempail.com", "getnada.com", "emkei.cf", "fakeinbox.com"
        }
        
        # Expected business domains patterns (can be configured)
        self.trusted_domain_patterns = [
            r".*\.(com|org|edu|gov)$",  # Standard business domains
            r".*\.(investment|capital|bank|financial)\..*",  # Financial industry domains
        ]
        
        # Internal bank codes/references that shouldn't appear in client-facing data
        self.internal_code_patterns = [
            r"(INTERNAL|INT|CONFIDENTIAL|CONF)[-_]?\d+",
            r"(TRADE|TRD|DEAL)[-_]?SECRET",
            r"EMPLOYEE[-_]?ONLY",
            r"DO[-_]?NOT[-_]?SHARE",
        ]

    def validate_client_boundary(self, client_email: str, meeting_description: str, 
                               client_name: str) -> Dict[str, Any]:
        """
        Validate that the request doesn't attempt to access multiple clients or 
        breach client data boundaries.
        
        Args:
            client_email: Email address of the client
            meeting_description: Description of the meeting
            client_name: Name of the client
            
        Returns:
            Dict with validation results and details
        """
        validation_results = {
            "valid": True,
            "issues": [],
            "risk_level": "low"
        }
        
        # Check for cross-client access patterns in meeting description
        description_lower = meeting_description.lower()
        for pattern in self.cross_client_patterns:
            if re.search(pattern, description_lower, re.IGNORECASE):
                validation_results["valid"] = False
                validation_results["issues"].append(f"Cross-client access pattern detected: {pattern}")
                validation_results["risk_level"] = "high"
                logger.warning(f"Cross-client pattern detected in meeting description: {pattern}")
        
        # Validate email domain consistency 
        try:
            email_domain = client_email.split('@')[1].lower()
            if email_domain in self.suspicious_email_domains:
                validation_results["valid"] = False
                validation_results["issues"].append(f"Suspicious email domain: {email_domain}")
                validation_results["risk_level"] = "medium"
                logger.warning(f"Suspicious email domain detected: {email_domain}")
        except (IndexError, AttributeError):
            validation_results["valid"] = False
            validation_results["issues"].append("Invalid email format for domain validation")
            validation_results["risk_level"] = "medium"
        
        return validation_results

    def validate_sql_injection_safety(self, input_data: Dict[str, str]) -> Dict[str, Any]:
        """
        Check all input fields for potential SQL injection patterns.
        
        Args:
            input_data: Dictionary of input fields to validate
            
        Returns:
            Dict with validation results
        """
        validation_results = {
            "valid": True,
            "issues": [],
            "risk_level": "low"
        }
        
        for field_name, field_value in input_data.items():
            if not isinstance(field_value, str):
                continue
                
            for pattern in self.sql_injection_patterns:
                if re.search(pattern, field_value, re.IGNORECASE):
                    validation_results["valid"] = False
                    validation_results["issues"].append(
                        f"Potential SQL injection pattern in {field_name}: {pattern}"
                    )
                    validation_results["risk_level"] = "critical"
                    logger.error(f"SQL injection pattern detected in {field_name}: {pattern}")
        
        return validation_results

    def validate_meeting_context(self, meeting_description: str, 
                                meeting_timestamp: str) -> Dict[str, Any]:
        """
        Validate meeting context for business logic and security issues.
        
        Args:
            meeting_description: Description of the meeting
            meeting_timestamp: Timestamp of the meeting
            
        Returns:
            Dict with validation results
        """
        validation_results = {
            "valid": True,
            "issues": [],
            "risk_level": "low"
        }
        
        # Check for internal codes in meeting description
        for pattern in self.internal_code_patterns:
            if re.search(pattern, meeting_description, re.IGNORECASE):
                validation_results["valid"] = False
                validation_results["issues"].append(
                    f"Internal code detected in meeting description: {pattern}"
                )
                validation_results["risk_level"] = "high"
                logger.warning(f"Internal code pattern detected: {pattern}")
        
        # Validate timestamp is reasonable (not too far in past/future)
        try:
            meeting_dt = datetime.strptime(meeting_timestamp, "%Y-%m-%d %H:%M:%S")
            now = datetime.now()
            
            # Check if meeting is more than 2 years in the past or 1 year in future
            if meeting_dt < now - timedelta(days=730):
                validation_results["issues"].append("Meeting timestamp too far in the past")
                validation_results["risk_level"] = "medium"
            elif meeting_dt > now + timedelta(days=365):
                validation_results["issues"].append("Meeting timestamp too far in the future")
                validation_results["risk_level"] = "medium"
                
        except ValueError:
            validation_results["valid"] = False
            validation_results["issues"].append("Invalid timestamp format")
            validation_results["risk_level"] = "medium"
        
        return validation_results

    def sanitize_input_text(self, text: str, max_length: int = 1000) -> str:
        """
        Sanitize input text by removing potentially dangerous characters and content.
        
        Args:
            text: Input text to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized text
        """
        if not isinstance(text, str):
            return str(text)
        
        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length]
            logger.info(f"Text truncated to {max_length} characters")
        
        # Remove null bytes and control characters (except newlines and tabs)
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # Remove potentially dangerous HTML/script tags
        text = re.sub(r'<script.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'<.*?>', '', text)  # Remove HTML tags
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def validate_user_boundary(self, user_email: str, client_email: str, 
                             meeting_description: str) -> Dict[str, Any]:
        """
        Validate that user access is appropriate and prevent cross-user boundary issues.
        
        Args:
            user_email: Email of the investment banker (user)
            client_email: Email of the client
            meeting_description: Description of the meeting
                
        Returns:
            Dict with validation results and details
        """
        validation_results = {
            "valid": True,
            "issues": [],
            "risk_level": "low"
        }
        
        # Validate user email format
        if not user_email or "@" not in user_email or "." not in user_email:
            validation_results["valid"] = False
            validation_results["issues"].append("Invalid user email format")
            validation_results["risk_level"] = "high"
            logger.warning(f"Invalid user email format: {user_email}")
        
        # Check if user email is from suspicious domain
        try:
            user_domain = user_email.split('@')[1].lower()
            if user_domain in self.suspicious_email_domains:
                validation_results["valid"] = False
                validation_results["issues"].append(f"Suspicious user email domain: {user_domain}")
                validation_results["risk_level"] = "critical"
                logger.error(f"Suspicious user email domain detected: {user_domain}")
        except IndexError:
            validation_results["valid"] = False
            validation_results["issues"].append("Malformed user email")
            validation_results["risk_level"] = "high"
        
        # Check for patterns indicating user impersonation or boundary crossing
        description_lower = meeting_description.lower()
        user_impersonation_patterns = [
            r"(on behalf of|representing|acting for)\s+[\w@.]+",
            r"(user|banker|advisor)\s*[=:]\s*[\w@.]+",
            r"(switch|change|impersonate)\s+(user|account|banker)"
        ]
        
        for pattern in user_impersonation_patterns:
            if re.search(pattern, description_lower, re.IGNORECASE):
                validation_results["valid"] = False
                validation_results["issues"].append(f"User impersonation pattern detected: {pattern}")
                validation_results["risk_level"] = "critical"
                logger.error(f"User impersonation pattern detected: {pattern}")
        
        return validation_results

    def validate_comprehensive(self, user_email: str, client_name: str, client_email: str, 
                             meeting_timestamp: str, meeting_description: str) -> Dict[str, Any]:
        """
        Run all validation checks and return comprehensive results.
        
        Args:
            user_email: Email of the investment banker (user)
            client_name: Name of the client
            client_email: Email address of the client
            meeting_timestamp: Timestamp of the meeting
            meeting_description: Description of the meeting
                
        Returns:
            Dict with all validation results and sanitized inputs
        """
        all_results = {
            "overall_valid": True,
            "validation_details": {},
            "sanitized_inputs": {},
            "risk_level": "low"
        }
        
        # Prepare input data for validation
        input_data = {
            "user_email": user_email,
            "client_name": client_name,
            "client_email": client_email,
            "meeting_timestamp": meeting_timestamp,
            "meeting_description": meeting_description
        }
        
        # Run all validation checks
        user_boundary_result = self.validate_user_boundary(
            user_email, client_email, meeting_description
        )
        client_boundary_result = self.validate_client_boundary(
            client_email, meeting_description, client_name
        )
        sql_injection_result = self.validate_sql_injection_safety(input_data)
        meeting_context_result = self.validate_meeting_context(
            meeting_description, meeting_timestamp
        )
        sanitization_result = {
            "sanitized_data": {
                "user_email": user_email,
                "client_name": self.sanitize_input_text(client_name, 100),
                "client_email": client_email,  # Email handled separately
                "meeting_description": self.sanitize_input_text(meeting_description, 500),
                "meeting_timestamp": meeting_timestamp  # Timestamp format already validated
            }
        }
        
        # Aggregate results
        all_results["validation_details"] = {
            "user_boundary": user_boundary_result,
            "client_boundary": client_boundary_result,
            "sql_injection": sql_injection_result,
            "meeting_context": meeting_context_result,
            "sanitization": sanitization_result
        }
        
        # Determine overall validity and risk level
        if (not user_boundary_result["valid"] or not client_boundary_result["valid"] or 
            not sql_injection_result["valid"] or not meeting_context_result["valid"]):
            all_results["overall_valid"] = False
            
        # Set highest risk level
        risk_levels = ["low", "medium", "high", "critical"]
        max_risk = "low"
        for result in [user_boundary_result, client_boundary_result, sql_injection_result, meeting_context_result]:
            if result["risk_level"] in risk_levels:
                if risk_levels.index(result["risk_level"]) > risk_levels.index(max_risk):
                    max_risk = result["risk_level"]
        all_results["risk_level"] = max_risk
        
        # Include sanitized inputs
        all_results["sanitized_inputs"] = sanitization_result["sanitized_data"]
        
        return all_results
