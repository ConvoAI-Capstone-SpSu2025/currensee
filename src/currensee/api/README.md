# Currensee API

A FastAPI server that provides HTTP endpoints for executing the Currensee agent graph and generating PDF reports for client meetings.

## Overview

This API serves as a bridge between Outlook add-ins or other UI applications and the Currensee agent system. It executes the compiled graph from `currensee.agents.complete_graph` and can return results in JSON, HTML, or PDF format.

## Features

- **Graph Execution**: Execute the complete Currensee agent workflow
- **Multiple Output Formats**: JSON data, HTML reports, or PDF downloads
- **Report Lengths**: Support for short, medium, and long report formats
- **CORS Support**: Configured for Outlook and web applications
- **Input Validation**: Comprehensive validation of client data
- **Error Handling**: Proper error responses and logging
- **Timeout Protection**: Prevents long-running requests from hanging

## Installation

The API is part of the main Currensee project. Ensure you have the project dependencies installed:

```bash
cd /Users/gforbus/Documents/Personal/currensee
poetry install
```

## Running the Server

### Option 1: Using the startup script (recommended)
```bash
python api/server.py
```

### Option 2: Using uvicorn directly
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

uvicorn currensee.api.main:app --host 0.0.0.0 --port 8000 --reload

```

### Option 3: Environment variables
```bash
export HOST=0.0.0.0
export PORT=8000
export DEBUG=true
python api/server.py
```

The server will start on `http://localhost:8000` by default.

## API Endpoints

### Health Check
- **GET** `/` - Basic health check
- **GET** `/health` - Health status for monitoring

### Report Generation
- **POST** `/generate-report` - Execute graph and return JSON results
- **POST** `/generate-report/html` - Execute graph and return HTML report
- **POST** `/generate-report/pdf` - Execute graph and return PDF download

### Demo Endpoints (for testing)
- **GET** `/demo` - Demo with sample data (JSON)
- **GET** `/demo/html` - Demo with sample data (HTML)
- **GET** `/demo/pdf` - Demo with sample data (PDF)

### API Documentation
- **GET** `/docs` - Interactive Swagger UI
- **GET** `/redoc` - ReDoc documentation

## Request Format

All POST endpoints expect a JSON payload with the following structure:

```json
{
  "client_name": "John Doe",
  "client_email": "john.doe@company.com",
  "meeting_timestamp": "2024-03-26 11:00:00",
  "meeting_description": "Annual Credit Facility Review Meeting",
  "report_length": "long"
}
```

### Fields

- `client_name` (required): Name of the client
- `client_email` (required): Valid email address
- `meeting_timestamp` (required): Meeting time in `YYYY-MM-DD HH:MM:SS` format
- `meeting_description` (required): Description of the meeting
- `report_length` (optional): One of "short", "medium", or "long" (default: "long")

## Response Formats

### JSON Response (`/generate-report`)
```json
{
  "success": true,
  "data": {
    "client_name": "John Doe",
    "final_summary_sourced": "...",
    // ... other graph execution results
  },
  "execution_time": 45.67
}
```

### HTML Response (`/generate-report/html`)
Returns a complete HTML document with styled report content.

### PDF Response (`/generate-report/pdf`)
Returns a PDF file as a download with filename: `currensee_report_{meeting_desc}_{timestamp}.pdf`

## Configuration

Configuration is handled in `api/config.py`. Key settings include:

- `HOST`: Server host (default: "0.0.0.0")
- `PORT`: Server port (default: 8000)
- `DEBUG`: Debug mode (default: false)
- `GRAPH_EXECUTION_TIMEOUT`: Timeout for graph execution (default: 300 seconds)
- `CORS_ORIGINS`: Allowed origins for CORS

## Environment Variables

You can override configuration using environment variables:

```bash
export HOST=localhost
export PORT=8080
export DEBUG=true
export GRAPH_EXECUTION_TIMEOUT=600
```

## Error Handling

The API provides comprehensive error handling:

- **400 Bad Request**: Invalid input data or validation errors
- **422 Unprocessable Entity**: Pydantic validation errors
- **500 Internal Server Error**: Graph execution errors or server issues
- **504 Gateway Timeout**: Graph execution timeout

## Usage Examples

### Using curl

```bash
# Test the health endpoint
curl http://localhost:8000/health

# Generate a report (JSON)
curl -X POST http://localhost:8000/generate-report \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "John Doe",
    "client_email": "john.doe@company.com",
    "meeting_timestamp": "2024-03-26 11:00:00",
    "meeting_description": "Client Review Meeting",
    "report_length": "medium"
  }'

# Download PDF report
curl -X POST http://localhost:8000/generate-report/pdf \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "John Doe",
    "client_email": "john.doe@company.com",
    "meeting_timestamp": "2024-03-26 11:00:00",
    "meeting_description": "Client Review Meeting"
  }' \
  --output report.pdf
```

### Using Python requests

```python
import requests

# Client data
data = {
    "client_name": "John Doe",
    "client_email": "john.doe@company.com",
    "meeting_timestamp": "2024-03-26 11:00:00",
    "meeting_description": "Client Review Meeting",
    "report_length": "long"
}

# Generate JSON report
response = requests.post("http://localhost:8000/generate-report", json=data)
result = response.json()

# Download PDF
pdf_response = requests.post("http://localhost:8000/generate-report/pdf", json=data)
with open("report.pdf", "wb") as f:
    f.write(pdf_response.content)
```

## Integration with Outlook

The API is designed to work with Outlook add-ins. Key considerations:

1. **CORS**: Configured to allow requests from Outlook domains
2. **Authentication**: Currently no authentication - add if needed for production
3. **Rate Limiting**: Not implemented - consider adding for production use
4. **SSL/TLS**: Use HTTPS in production for security

## Logging

The API uses Python's built-in logging. In debug mode, you'll see detailed request/response information. In production, only INFO level and above are logged.

## Development

To extend the API:

1. Add new endpoints in `api/main.py`
2. Update configuration in `api/config.py`
3. Add new response models as needed
4. Update this README with new functionality

## Production Deployment

For production deployment:

1. Set `DEBUG=false`
2. Configure specific CORS origins
3. Use a production ASGI server like Gunicorn with Uvicorn workers
4. Add authentication/authorization as needed
5. Implement rate limiting
6. Use HTTPS/SSL
7. Set up proper logging and monitoring

Example production command:
```bash
gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```
