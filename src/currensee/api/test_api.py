#!/usr/bin/env python3
"""
Test script for the Currensee API
"""
import sys
from pathlib import Path

# Add the src directory to the Python path
# project_root = Path(__file__).parent.parent
# src_path = project_root / "src"
# sys.path.insert(0, str(src_path))

import pytest
from fastapi.testclient import TestClient
from currensee.api.main import app

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "currensee-api"

def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "timestamp" in data

def test_generate_report_validation():
    """Test input validation for generate-report endpoint"""
    # Test with missing required fields
    response = client.post("/generate-report", json={})
    assert response.status_code == 422  # Validation error
    
    # Test with invalid email
    invalid_data = {
        "client_name": "Test Client",
        "client_email": "invalid-email",
        "meeting_timestamp": "2024-03-26 11:00:00",
        "meeting_description": "Test Meeting"
    }
    response = client.post("/generate-report", json=invalid_data)
    assert response.status_code == 422
    
    # Test with invalid timestamp format
    invalid_data = {
        "client_name": "Test Client", 
        "client_email": "test@example.com",
        "meeting_timestamp": "invalid-timestamp",
        "meeting_description": "Test Meeting"
    }
    response = client.post("/generate-report", json=invalid_data)
    assert response.status_code == 422
    
    # Test with invalid report length
    invalid_data = {
        "client_name": "Test Client",
        "client_email": "test@example.com", 
        "meeting_timestamp": "2024-03-26 11:00:00",
        "meeting_description": "Test Meeting",
        "report_length": "invalid"
    }
    response = client.post("/generate-report", json=invalid_data)
    assert response.status_code == 422

def test_demo_endpoints():
    """Test demo endpoints"""
    # Test demo JSON endpoint
    response = client.get("/demo")
    assert response.status_code == 200
    
    # Test demo HTML endpoint
    response = client.get("/demo/html")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    
    # Test demo PDF endpoint
    response = client.get("/demo/pdf")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"

if __name__ == "__main__":
    print("Running API tests...")
    
    print("Testing health check...")
    test_health_check()
    print("✓ Health check passed")
    
    print("Testing root endpoint...")
    test_root_endpoint()
    print("✓ Root endpoint passed")
    
    print("Testing validation...")
    test_generate_report_validation()
    print("✓ Validation tests passed")
    
    print("Testing demo endpoints...")
    test_demo_endpoints()
    print("✓ Demo endpoints passed")
    
    print("All tests passed! 🎉")
