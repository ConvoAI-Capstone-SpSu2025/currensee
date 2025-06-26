#!/usr/bin/env python3
"""
Startup script for the Currensee API server
"""
import sys
import os
from pathlib import Path

# Add the src directory to the Python path so we can import currensee
# project_root = Path(__file__).parent.parent
# src_path = project_root / "src"
# sys.path.insert(0, str(src_path))

import uvicorn
from currensee.api.config import settings
from currensee.api.main import app

def main():
    """Start the API server"""
    print(f"Starting {settings.APP_NAME} v{settings.VERSION}")
    print(f"Server will run on {settings.HOST}:{settings.PORT}")
    print(f"Debug mode: {settings.DEBUG}")
    
    # Load environment variables from .env file if it exists
    env_file = project_root / ".env"
    if env_file.exists():
        print(f"Loading environment from {env_file}")
    
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info"
    )

if __name__ == "__main__":
    main()
