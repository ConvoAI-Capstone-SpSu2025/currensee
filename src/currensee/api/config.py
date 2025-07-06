"""
Configuration settings for the Currensee API
"""
import os
from typing import List

class Settings:
    """Application settings"""
    
    # API Configuration
    APP_NAME: str = "Currensee API"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "https://outlook.office.com",
        "https://outlook.live.com", 
        "https://outlook.office365.com",
        "http://localhost:3000",  # For local development
        "http://localhost:8080",  # For local development
    ]
    
    # Report Configuration
    DEFAULT_REPORT_LENGTH: str = "long"
    ALLOWED_REPORT_LENGTHS: List[str] = ["short", "medium", "long"]
    
    # PDF Configuration
    PDF_PAGE_SIZE: str = "Letter"
    
    # Rate Limiting (if needed)
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_PERIOD: int = int(os.getenv("RATE_LIMIT_PERIOD", "3600"))  # 1 hour
    
    # Timeout Configuration
    GRAPH_EXECUTION_TIMEOUT: int = int(os.getenv("GRAPH_EXECUTION_TIMEOUT", "300"))  # 5 minutes


# Global settings instance
settings = Settings()
