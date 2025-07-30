"""
CurrenSee Output Guardrails - Custom Lightweight Validation for Investment Banking Reports

This module provides fast, lightweight output validation for CurrenSee's investment banking 
reports using custom regex patterns and rule-based validation. Designed to match the 
proven architecture of input_guardrails.py.

Features:
- PII detection and redaction (emails, phones, account numbers)
- Financial compliance validation (SEC/FINRA requirements)  
- Professional tone validation (banking language standards)
- Content structure validation
- Zero external dependencies for maximum performance and reliability
"""

import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Set, Any, Union
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PIIDetectionResult:
    """Result of PII detection analysis."""
    field_name: str
    pii_found: List[Dict[str, Any]]
    redacted_text: str
    risk_score: float


@dataclass
class ComplianceIssue:
    """Financial compliance issue detected."""
    field_name: str
    issue_type: str
    description: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    suggested_action: str


@dataclass
class ValidationResult:
    """Complete validation result for output guardrails."""
    validation_passed: bool
    pii_results: List[PIIDetectionResult]
    compliance_issues: List[ComplianceIssue]
    tone_issues: List[Dict[str, str]]
    sanitized_report: Dict[str, Any]
    processing_time_ms: float
    validation_summary: str


class CurrenSeeOutputGuardrails:
    """
    Custom output validation and security guardrails for CurrenSee investment banking reports.
    
    Designed for high performance and zero dependencies, following the proven pattern
    of input_guardrails.py. Provides comprehensive validation for:
    - PII detection and redaction
    - Financial compliance (SEC/FINRA) 
    - Professional tone validation
    - Content structure validation
    """
    
    def __init__(self):
        """Initialize output guardrails with investment banking specific patterns."""
        
        # PII detection patterns (investment banking specific)
        self.pii_patterns = {
            "email": {
                "pattern": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                "replacement": "[EMAIL_REDACTED]",
                "risk_weight": 0.8
            },
            "phone": {
                "pattern": r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',
                "replacement": "[PHONE_REDACTED]", 
                "risk_weight": 0.7
            },
            "ssn": {
                "pattern": r'\b\d{3}-\d{2}-\d{4}\b',
                "replacement": "[SSN_REDACTED]",
                "risk_weight": 1.0
            },
            "account_number": {
                "pattern": r'\b\d{8,16}\b',
                "replacement": "[ACCOUNT_REDACTED]",
                "risk_weight": 0.9
            },
            "credit_card": {
                "pattern": r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
                "replacement": "[CARD_REDACTED]",
                "risk_weight": 1.0
            },
            "routing_number": {
                "pattern": r'\b\d{9}\b',
                "replacement": "[ROUTING_REDACTED]",
                "risk_weight": 0.8
            }
        }
        
        # Financial compliance patterns (SEC/FINRA requirements)
        self.compliance_checks = {
            "investment_advice": {
                "triggers": [
                    r"\b(should|must|recommend|advise).*\b(buy|sell|invest|purchase|divest)\b",
                    r"\b(guaranteed|risk-free|always profitable|certain return)\b",
                    r"\b(best investment|top pick|sure thing)\b"
                ],
                "required_disclaimers": [
                    "past performance", "investment risk", "may lose value", 
                    "not guaranteed", "consult advisor"
                ],
                "severity": "high"
            },
            "performance_claims": {
                "triggers": [
                    r"\b(will|going to|guaranteed to)\s*(gain|profit|increase|return)\b",
                    r"\b(outperform|beat the market|superior returns)\b",
                    r"\b\d+%\s*(return|gain|profit)\s*(guaranteed|certain)\b"
                ],
                "required_disclaimers": ["past performance", "no guarantee"],
                "severity": "critical"
            },
            "risk_disclosure": {
                "triggers": [
                    r"\b(investment|portfolio|asset|security|stock|bond)\b",
                    r"\b(credit facility|loan|financing|capital)\b"
                ],
                "required_disclaimers": ["investment risk", "potential loss"],
                "severity": "medium"
            }
        }
        
        # Professional tone validation patterns
        self.tone_issues = {
            "informal_language": {
                "patterns": [
                    r"\b(awesome|cool|amazing|super|totally|really)\b",
                    r"\b(gonna|wanna|gotta|yeah|yep|nope)\b",
                    r"\b(btw|fyi|lol|omg|tbh)\b"
                ],
                "severity": "medium",
                "suggestion": "Use formal business language"
            },
            "contractions": {
                "patterns": [
                    r"\b(can't|won't|don't|doesn't|isn't|aren't|wasn't|weren't)\b",
                    r"\b(haven't|hasn't|hadn't|wouldn't|couldn't|shouldn't)\b"
                ],
                "severity": "low", 
                "suggestion": "Expand contractions for formal tone"
            },
            "excessive_punctuation": {
                "patterns": [
                    r"[!]{2,}",
                    r"[?]{2,}",
                    r"[.]{3,}"
                ],
                "severity": "low",
                "suggestion": "Use single punctuation marks"
            },
            "inappropriate_emphasis": {
                "patterns": [
                    r"\b[A-Z]{4,}\b",  # ALL CAPS words
                    r"[*]{2,}.*[*]{2,}",  # **bold** emphasis
                ],
                "severity": "medium",
                "suggestion": "Use professional emphasis methods"
            }
        }
        
        # Content structure validation
        self.structure_requirements = {
            "email_summary": {
                "min_length": 50,
                "max_length": 2000,
                "required_elements": ["email", "summary"]
            },
            "summary_fin_hold": {
                "min_length": 100,
                "max_length": 1500,
                "required_elements": ["holdings", "financial"]
            },
            "summary_client_comms": {
                "min_length": 50,
                "max_length": 1000,
                "required_elements": ["client", "communication"]
            }
        }
        
        logger.info("CurrenSee output guardrails initialized successfully")

    def detect_pii(self, content: Dict[str, str]) -> List[PIIDetectionResult]:
        """
        Detect and catalog PII across all content fields.
        
        Args:
            content: Dictionary of field names to text content
            
        Returns:
            List of PII detection results for each field
        """
        pii_results = []
        
        for field_name, text in content.items():
            if not isinstance(text, str) or not text.strip():
                continue
                
            field_pii = []
            redacted_text = text
            total_risk = 0.0
            
            # Check each PII pattern
            for pii_type, config in self.pii_patterns.items():
                matches = list(re.finditer(config["pattern"], text, re.IGNORECASE))
                
                if matches:
                    # Record PII findings
                    field_pii.append({
                        "type": pii_type,
                        "count": len(matches),
                        "positions": [(m.start(), m.end()) for m in matches],
                        "risk_weight": config["risk_weight"]
                    })
                    
                    # Redact PII from text
                    redacted_text = re.sub(
                        config["pattern"], 
                        config["replacement"], 
                        redacted_text, 
                        flags=re.IGNORECASE
                    )
                    
                    # Calculate cumulative risk
                    total_risk += len(matches) * config["risk_weight"]
            
            # Create result for this field
            pii_results.append(PIIDetectionResult(
                field_name=field_name,
                pii_found=field_pii,
                redacted_text=redacted_text,
                risk_score=min(total_risk, 1.0)  # Cap at 1.0
            ))
            
            if field_pii:
                logger.warning(f"PII detected in field '{field_name}': {len(field_pii)} types")
        
        return pii_results

    def validate_financial_compliance(self, content: Dict[str, str]) -> List[ComplianceIssue]:
        """
        Validate content for financial compliance issues (SEC/FINRA).
        
        Args:
            content: Dictionary of field names to text content
            
        Returns:
            List of compliance issues found
        """
        compliance_issues = []
        
        for field_name, text in content.items():
            if not isinstance(text, str) or not text.strip():
                continue
                
            text_lower = text.lower()
            
            # Check each compliance category
            for check_type, config in self.compliance_checks.items():
                triggered = False
                
                # Check if any trigger patterns match
                for trigger_pattern in config["triggers"]:
                    if re.search(trigger_pattern, text_lower, re.IGNORECASE):
                        triggered = True
                        break
                
                if triggered:
                    # Check if required disclaimers are present
                    missing_disclaimers = []
                    for disclaimer in config["required_disclaimers"]:
                        if disclaimer.lower() not in text_lower:
                            missing_disclaimers.append(disclaimer)
                    
                    if missing_disclaimers:
                        compliance_issues.append(ComplianceIssue(
                            field_name=field_name,
                            issue_type=check_type,
                            description=f"Missing required disclaimers: {', '.join(missing_disclaimers)}",
                            severity=config["severity"],
                            suggested_action=f"Add disclaimers: {', '.join(missing_disclaimers)}"
                        ))
                        
                        logger.warning(f"Compliance issue in '{field_name}': {check_type}")
        
        return compliance_issues

    def validate_professional_tone(self, content: Dict[str, str]) -> List[Dict[str, str]]:
        """
        Validate content for professional tone and language.
        
        Args:
            content: Dictionary of field names to text content
            
        Returns:
            List of tone issues found
        """
        tone_issues = []
        
        for field_name, text in content.items():
            if not isinstance(text, str) or not text.strip():
                continue
            
            # Check each tone category
            for issue_type, config in self.tone_issues.items():
                for pattern in config["patterns"]:
                    matches = list(re.finditer(pattern, text, re.IGNORECASE))
                    
                    if matches:
                        tone_issues.append({
                            "field_name": field_name,
                            "issue_type": issue_type,
                            "severity": config["severity"],
                            "suggestion": config["suggestion"],
                            "match_count": len(matches),
                            "examples": [text[m.start():m.end()] for m in matches[:3]]  # First 3 examples
                        })
                        
                        logger.info(f"Tone issue in '{field_name}': {issue_type} ({len(matches)} instances)")
        
        return tone_issues

    def validate_content_structure(self, content: Dict[str, str]) -> List[Dict[str, str]]:
        """
        Validate content structure and format requirements.
        
        Args:
            content: Dictionary of field names to text content
            
        Returns:
            List of structure issues found
        """
        structure_issues = []
        
        for field_name, text in content.items():
            if field_name not in self.structure_requirements:
                continue
                
            if not isinstance(text, str):
                structure_issues.append({
                    "field_name": field_name,
                    "issue": "Non-string content",
                    "severity": "high"
                })
                continue
            
            requirements = self.structure_requirements[field_name]
            text_length = len(text.strip())
            
            # Check length requirements
            if text_length < requirements["min_length"]:
                structure_issues.append({
                    "field_name": field_name,
                    "issue": f"Content too short ({text_length} < {requirements['min_length']} chars)",
                    "severity": "medium"
                })
                
            if text_length > requirements["max_length"]:
                structure_issues.append({
                    "field_name": field_name,
                    "issue": f"Content too long ({text_length} > {requirements['max_length']} chars)",
                    "severity": "low"
                })
            
            # Check required elements
            text_lower = text.lower()
            for required_element in requirements["required_elements"]:
                if required_element.lower() not in text_lower:
                    structure_issues.append({
                        "field_name": field_name,
                        "issue": f"Missing required element: '{required_element}'",
                        "severity": "medium"
                    })
        
        return structure_issues

    def create_sanitized_report(self, original_report: Dict[str, Any], 
                              pii_results: List[PIIDetectionResult]) -> Dict[str, Any]:
        """
        Create a sanitized version of the report with PII redacted.
        
        Args:
            original_report: Original report data
            pii_results: PII detection results with redacted content
            
        Returns:
            Sanitized report with PII redacted
        """
        sanitized_report = original_report.copy()
        
        # Replace content with redacted versions
        for pii_result in pii_results:
            if pii_result.field_name in sanitized_report:
                sanitized_report[pii_result.field_name] = pii_result.redacted_text
        
        # Add sanitization metadata
        sanitized_report["__sanitization_metadata__"] = {
            "timestamp": datetime.now().isoformat(),
            "pii_redacted": sum(len(result.pii_found) for result in pii_results),
            "fields_processed": len(pii_results)
        }
        
        return sanitized_report

    def validate_comprehensive(self, report_data: Dict[str, Any]) -> ValidationResult:
        """
        Run all validation checks and return comprehensive results.
        
        Args:
            report_data: Complete report data to validate
            
        Returns:
            ValidationResult with all validation findings
        """
        start_time = datetime.now()
        
        # Extract text content for validation
        text_content = {}
        for key, value in report_data.items():
            if isinstance(value, str) and value.strip():
                text_content[key] = value
        
        if not text_content:
            logger.warning("No text content found for validation")
            return ValidationResult(
                validation_passed=True,
                pii_results=[],
                compliance_issues=[],
                tone_issues=[],
                sanitized_report=report_data,
                processing_time_ms=0.0,
                validation_summary="No text content to validate"
            )
        
        # Run all validation checks
        pii_results = self.detect_pii(text_content)
        compliance_issues = self.validate_financial_compliance(text_content)
        tone_issues = self.validate_professional_tone(text_content)
        structure_issues = self.validate_content_structure(text_content)
        
        # Create sanitized report
        sanitized_report = self.create_sanitized_report(report_data, pii_results)
        
        # Determine overall validation status
        critical_issues = [
            issue for issue in compliance_issues 
            if issue.severity == "critical"
        ]
        
        high_risk_pii = [
            result for result in pii_results 
            if result.risk_score > 0.7
        ]
        
        validation_passed = len(critical_issues) == 0 and len(high_risk_pii) == 0
        
        # Calculate processing time
        processing_time_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        # Generate validation summary
        validation_summary = self._generate_validation_summary(
            pii_results, compliance_issues, tone_issues, structure_issues, validation_passed
        )
        
        result = ValidationResult(
            validation_passed=validation_passed,
            pii_results=pii_results,
            compliance_issues=compliance_issues,
            tone_issues=tone_issues,
            sanitized_report=sanitized_report,
            processing_time_ms=processing_time_ms,
            validation_summary=validation_summary
        )
        
        logger.info(f"Output validation completed in {processing_time_ms:.1f}ms - {'PASSED' if validation_passed else 'FAILED'}")
        return result

    def _generate_validation_summary(self, pii_results: List[PIIDetectionResult], 
                                   compliance_issues: List[ComplianceIssue],
                                   tone_issues: List[Dict[str, str]], 
                                   structure_issues: List[Dict[str, str]],
                                   validation_passed: bool) -> str:
        """Generate human-readable validation summary."""
        
        total_pii = sum(len(result.pii_found) for result in pii_results)
        critical_compliance = len([i for i in compliance_issues if i.severity == "critical"])
        high_compliance = len([i for i in compliance_issues if i.severity == "high"])
        
        if validation_passed:
            summary = "✅ OUTPUT VALIDATION PASSED\n"
        else:
            summary = "❌ OUTPUT VALIDATION FAILED\n"
        
        summary += f"🛡️ PII Detection: {total_pii} instances found and redacted\n"
        summary += f"⚖️ Compliance Issues: {len(compliance_issues)} total ({critical_compliance} critical, {high_compliance} high)\n"
        summary += f"📝 Tone Issues: {len(tone_issues)} suggestions\n"
        summary += f"📋 Structure Issues: {len(structure_issues)} format issues\n"
        
        if critical_compliance > 0:
            summary += "\n🚨 CRITICAL COMPLIANCE ISSUES:\n"
            for issue in compliance_issues:
                if issue.severity == "critical":
                    summary += f"  - {issue.field_name}: {issue.description}\n"
        
        if total_pii > 0:
            summary += f"\n🔒 PII REDACTED: {total_pii} instances across {len(pii_results)} fields\n"
        
        return summary


# Integration function for output_utils_dynamic.py
def validate_output_before_rendering(report_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main integration function to validate report data before HTML rendering.
    
    This is the primary integration point for output_utils_dynamic.py
    
    Args:
        report_data: Complete report data from the agent pipeline
        
    Returns:
        Dict containing validation results and sanitized report data
    """
    try:
        guardrails = CurrenSeeOutputGuardrails()
        validation_result = guardrails.validate_comprehensive(report_data)
        
        return {
            "validation_passed": validation_result.validation_passed,
            "sanitized_report": validation_result.sanitized_report,
            "pii_detected": len([r for r in validation_result.pii_results if r.pii_found]),
            "compliance_issues": len(validation_result.compliance_issues),
            "tone_issues": len(validation_result.tone_issues),
            "processing_time_ms": validation_result.processing_time_ms,
            "validation_summary": validation_result.validation_summary,
            "guardrails_version": "custom_v1.0"
        }
        
    except Exception as e:
        logger.error(f"Output guardrails validation error: {str(e)}")
        return {
            "validation_passed": False,
            "error": str(e),
            "sanitized_report": report_data,
            "guardrails_version": "custom_v1.0"
        }


if __name__ == "__main__":
    # Test with sample investment banking data
    sample_data = {
        "summary_fin_hold": "TSMC shows strong performance with $1 trillion market cap. Client should definitely invest immediately for guaranteed 20% returns.",
        "email_summary": "Recent communications with john.doe@compass.com about the $25M credit facility. His phone is 555-123-4567.",
        "summary_client_comms": "Meeting scheduled with Adam Clay regarding credit expansion. This is an awesome opportunity!"
    }
    
    result = validate_output_before_rendering(sample_data)
    print(result["validation_summary"])
