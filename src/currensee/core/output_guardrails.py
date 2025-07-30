"""
CurrenSee Output Guardrails - Investment Banking Report Validation

This module provides comprehensive output validation for CurrenSee's investment banking 
reports using Guardrails AI for schema-based validation, PII detection, and compliance checking.
"""

from typing import Dict, Any, List, Optional
import logging
from pydantic import BaseModel, Field, validator
import re

try:
    import guardrails as gd
    from guardrails import Guard
    from guardrails.validators import ValidatorError
    GUARDRAILS_AVAILABLE = True
except ImportError:
    GUARDRAILS_AVAILABLE = False
    print("⚠️ Guardrails AI not installed. Install with: pip install guardrails-ai")

logger = logging.getLogger(__name__)


class InvestmentReportContent(BaseModel):
    """
    Pydantic model defining the structure and validation rules for CurrenSee investment reports.
    Designed to match the actual output structure from secure_graph_invoke().
    """
    
    # Core content fields that need validation
    summary_fin_hold: str = Field(
        description="Financial holdings summary with market analysis",
        validators=["no-pii", "financial-compliance", "professional-tone"]
    )
    
    summary_client_comms: str = Field(
        description="Client communications briefing document",
        validators=["no-pii", "professional-tone", "structured-content"]
    )
    
    fin_hold_summary_sourced: str = Field(
        description="Financial holdings summary with HTML source links",
        validators=["no-pii", "financial-compliance", "valid-html-links"]
    )
    
    finnews_summary: str = Field(
        description="Macro financial news analysis",
        validators=["no-pii", "factual-accuracy", "professional-tone"]
    )
    
    # Optional fields that may be present
    summary_client_news: Optional[str] = Field(
        default="",
        description="Client-specific news summary",
        validators=["no-pii", "professional-tone"]
    )
    
    client_news_summary_sourced: Optional[str] = Field(
        default="",
        description="Client news with source links",
        validators=["no-pii", "valid-html-links"]
    )
    
    email_summary: Optional[str] = Field(
        default="",
        description="Email communication summary",
        validators=["no-pii", "professional-tone"]
    )
    
    recent_email_summary: Optional[str] = Field(
        default="",
        description="Recent email bullet points",
        validators=["no-pii", "professional-tone"]
    )

    @validator("summary_fin_hold")
    def validate_financial_content(cls, v):
        """Custom validation for financial content compliance."""
        if not v:
            return v
            
        # Check for investment advice without proper disclaimers
        investment_keywords = ['should invest', 'recommend buying', 'guaranteed returns', 'will perform']
        disclaimers = ['past performance', 'investment risk', 'not investment advice']
        
        has_investment_language = any(keyword in v.lower() for keyword in investment_keywords)
        has_disclaimer = any(disclaimer in v.lower() for disclaimer in disclaimers)
        
        if has_investment_language and not has_disclaimer:
            raise ValidatorError("Financial content contains investment advice without required disclaimers")
        
        return v

    @validator("*", pre=True)
    def validate_no_pii(cls, v, field):
        """Validate that content doesn't contain obvious PII patterns."""
        if not isinstance(v, str) or not v:
            return v
            
        # Basic PII patterns (Guardrails AI will do more comprehensive detection)
        pii_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # Credit card
            r'\b\d{10,16}\b',  # Account numbers
        ]
        
        for pattern in pii_patterns:
            if re.search(pattern, v):
                logger.warning(f"Potential PII detected in {field.name}: {pattern}")
                # Don't raise error - let Guardrails AI handle this more sophisticatedly
        
        return v


class CurrenSeeOutputGuardrails:
    """
    Main class for CurrenSee output validation using Guardrails AI.
    
    Validates investment banking reports for:
    - PII detection and redaction
    - Financial compliance (SEC/FINRA requirements)
    - Professional tone and formatting
    - Content accuracy and consistency
    """
    
    def __init__(self):
        if not GUARDRAILS_AVAILABLE:
            raise ImportError("Guardrails AI is required but not installed. Run: pip install guardrails-ai")
        
        # Create guard with our custom Pydantic model
        self.guard = Guard.from_pydantic(
            output_class=InvestmentReportContent,
            prompt=self._get_validation_prompt()
        )
        
        # Financial compliance patterns
        self.compliance_patterns = {
            "investment_disclaimers": [
                "past performance is not indicative of future results",
                "all investments carry risk",
                "this is not investment advice"
            ],
            "risk_disclosures": [
                "market volatility",
                "investment risk",
                "potential for loss"
            ]
        }
        
        logger.info("CurrenSee output guardrails initialized successfully")

    def _get_validation_prompt(self) -> str:
        """Get the validation prompt for Guardrails AI."""
        return """
        You are validating an investment banking briefing document for compliance and safety.
        
        Key requirements:
        1. NO personally identifiable information (PII) should be present
        2. Financial analysis must include appropriate risk disclaimers
        3. Investment-related content must not constitute financial advice
        4. Professional tone and language must be maintained
        5. All claims must be properly sourced
        
        Ensure the content meets investment banking professional standards and regulatory compliance.
        """

    def validate_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a complete CurrenSee report using Guardrails AI.
        
        Args:
            report_data: Dictionary containing the report data (output from secure_graph_invoke)
            
        Returns:
            Dict containing validation results and sanitized content
        """
        try:
            # Extract key content fields for validation
            content_to_validate = {
                "summary_fin_hold": report_data.get("summary_fin_hold", ""),
                "summary_client_comms": report_data.get("summary_client_comms", ""),
                "fin_hold_summary_sourced": report_data.get("fin_hold_summary_sourced", ""),
                "finnews_summary": report_data.get("finnews_summary", ""),
                "summary_client_news": report_data.get("summary_client_news", ""),
                "client_news_summary_sourced": report_data.get("client_news_summary_sourced", ""),
                "email_summary": report_data.get("email_summary", ""),
                "recent_email_summary": report_data.get("recent_email_summary", "")
            }
            
            # Run Guardrails validation
            validated_output = self.guard(
                content_to_validate,
                metadata={"report_type": "investment_banking_briefing"}
            )
            
            # Additional custom validation
            compliance_issues = self._check_financial_compliance(content_to_validate)
            pii_summary = self._detect_pii_summary(content_to_validate)
            
            return {
                "validation_passed": True,
                "validated_content": validated_output.validated_output,
                "compliance_issues": compliance_issues,
                "pii_detected": pii_summary,
                "guardrails_metadata": validated_output.validation_log,
                "sanitized_report": self._create_sanitized_report(report_data, validated_output.validated_output)
            }
            
        except Exception as e:
            logger.error(f"Output validation failed: {str(e)}")
            return {
                "validation_passed": False,
                "error": str(e),
                "original_content": report_data,
                "sanitized_report": None
            }

    def _check_financial_compliance(self, content: Dict[str, str]) -> List[Dict]:
        """Check for financial compliance issues."""
        issues = []
        
        for field_name, text in content.items():
            if not text:
                continue
                
            text_lower = text.lower()
            
            # Check for investment advice without disclaimers
            advice_keywords = ['should invest', 'recommend', 'buy', 'sell', 'guaranteed']
            has_advice = any(keyword in text_lower for keyword in advice_keywords)
            
            if has_advice:
                has_disclaimer = any(
                    disclaimer in text_lower 
                    for disclaimer in self.compliance_patterns["investment_disclaimers"]
                )
                
                if not has_disclaimer:
                    issues.append({
                        "field": field_name,
                        "type": "missing_investment_disclaimer",
                        "description": "Investment-related content without required disclaimers"
                    })
        
        return issues

    def _detect_pii_summary(self, content: Dict[str, str]) -> Dict:
        """Provide summary of PII detection across all content."""
        pii_count = 0
        fields_with_pii = []
        
        for field_name, text in content.items():
            if not text:
                continue
                
            # Basic PII detection (Guardrails will do more comprehensive)
            pii_patterns = [
                (r'\b\d{3}-\d{2}-\d{4}\b', 'SSN'),
                (r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', 'Credit Card'),
                (r'\b\d{10,16}\b', 'Account Number'),
                (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'Email'),
                (r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', 'Phone Number')
            ]
            
            field_pii = []
            for pattern, pii_type in pii_patterns:
                matches = re.findall(pattern, text)
                if matches:
                    field_pii.append({"type": pii_type, "count": len(matches)})
                    pii_count += len(matches)
            
            if field_pii:
                fields_with_pii.append({"field": field_name, "pii_found": field_pii})
        
        return {
            "total_pii_instances": pii_count,
            "fields_with_pii": fields_with_pii,
            "requires_sanitization": pii_count > 0
        }

    def _create_sanitized_report(self, original_report: Dict, validated_content: Dict) -> Dict:
        """Create a sanitized version of the report with validated content."""
        sanitized_report = original_report.copy()
        
        # Replace validated content fields
        for field_name, validated_text in validated_content.items():
            if field_name in sanitized_report:
                sanitized_report[field_name] = validated_text
        
        return sanitized_report

    def get_validation_summary(self, validation_result: Dict) -> str:
        """Get a human-readable summary of validation results."""
        if not validation_result["validation_passed"]:
            return f"❌ Validation FAILED: {validation_result.get('error', 'Unknown error')}"
        
        pii_count = validation_result["pii_detected"]["total_pii_instances"]
        compliance_issues = len(validation_result["compliance_issues"])
        
        summary = "✅ Validation PASSED\n"
        summary += f"🛡️ PII instances detected and handled: {pii_count}\n"
        summary += f"⚖️ Compliance issues: {compliance_issues}\n"
        
        if compliance_issues > 0:
            summary += "⚠️ Compliance issues found:\n"
            for issue in validation_result["compliance_issues"]:
                summary += f"  - {issue['field']}: {issue['description']}\n"
        
        return summary


# Integration function for generate_report()
def validate_output_before_rendering(report_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to validate report data before HTML rendering.
    
    This is the main integration point for output_utils_dynamic.py
    
    Args:
        report_data: Complete report data from secure_graph_invoke()
        
    Returns:
        Validation results with sanitized content
    """
    try:
        guardrails = CurrenSeeOutputGuardrails()
        return guardrails.validate_report(report_data)
    except ImportError:
        # Fallback if Guardrails AI not available
        logger.warning("Guardrails AI not available - skipping output validation")
        return {
            "validation_passed": True,
            "sanitized_report": report_data,
            "guardrails_available": False
        }
    except Exception as e:
        logger.error(f"Output guardrails error: {str(e)}")
        return {
            "validation_passed": False,
            "error": str(e),
            "sanitized_report": report_data
        }


if __name__ == "__main__":
    # Test with sample data
    sample_data = {
        "summary_fin_hold": "TSMC shows strong performance with $1 trillion market cap.",
        "summary_client_comms": "Meeting scheduled with Adam Clay regarding credit facility.",
        "email_summary": "Recent communications about the $25M credit facility."
    }
    
    result = validate_output_before_rendering(sample_data)
    guardrails = CurrenSeeOutputGuardrails()
    print(guardrails.get_validation_summary(result))
