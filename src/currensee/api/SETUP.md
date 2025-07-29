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

## Pre-Setup

### 1. Configure the Poetry Environment

Follow the instructions here:
[Currensee README.md](https://github.com/ConvoAI-Capstone-SpSu2025/currensee/blob/main/README.md)


### 2. Set Up the Cloud SQL Connection

#### Step 1: Find the External IP of Your JupyterLab VM

- Go to [VM Instances](https://console.cloud.google.com/compute/instances?project=adsp-34002-on02-sopho-scribe&authuser=1)
- Locate your **JupyterLab VM**
- Copy the **External IP address** (e.g., `34.91.100.45`)

#### Step 2: Add the IP to Cloud SQL Authorized Networks

- Visit [Cloud SQL Networking](https://console.cloud.google.com/sql/instances/currensee-sql/connections/networking?authuser=1&project=adsp-34002-on02-sopho-scribe)
- Select your SQL instance
- Click **Connections** in the left sidebar
- Scroll to **Authorized networks** and click **Add network**
  - **Name**: e.g., `jupyterlab-vm`
  - **Network**: paste the IP with `/32` suffix (e.g., `34.91.100.45/32`)
- The `/32` ensures only that single IP is allowed
- Click **Save**

### Step 3: Install `gcloud` on your local machine

- Follow the instructions here to set up [gcloud](https://cloud.google.com/sdk/docs/install)
- I recommend untaring the file it prompts you to downloaded into your home directory (if it's in downloads you will need to move it to the home folder)
- During setup it will ask you to sign in (use your uchicago email)
- During setup it will ask for the project-id, paste in adsp-34002-on02-sopho-scribe
- On your local terminal ensure gcloud is properly installed in the home directory. To test type 'gcloud version' to make sure you don't get an error message.
- If the gcloud comand isnt found/you get an error - you may need to manually update the path in the .zshrc file:
```bash
sudo vi ~/.zshrc
#paste into the file this line:
export PATH=$HOME/google-cloud-sdk/bin:$PATH
```


## Running the Server

### Option 1: Using the startup script (recommended)
```bash
python src/currensee/api/server.py
```
Make sure this script is entered at (currensee-py3.11) (base) jupyter@vertex-workbench-cpu:~/(your initial)_currensee/currensee$

### Option 2: Using uvicorn directly
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

```

### Option 3: Environment variables
```bash
export HOST=0.0.0.0
export PORT=8000
export DEBUG=true
python api/server.py
```

The server will start on `http://localhost:8000` by default.

## SSH Port Forwarding (Optional)

It lets you access FastAPI server, which is running on localhost of a remote VM — as if it were running on your own local machine.

In your **local terminal**, run
```bash
gcloud compute ssh vertex-workbench-cpu -- -L 8000:localhost:8000
```

### Health Check
Open http://localhost:8000/health to do the connection health check

If connected, it will show as message similar to this {"status":"healthy","service":"currensee-api","timestamp":"2025-06-28T16:17:25.457157"}

### Open the landing page in your localhost
Open http://localhost:8000 on your local browser to access Outlook UI page.

### Error Check
If you see "Error: Cannot read properties of null (reading 'document')", make sure your local browser allow popups from about:blank

## Shut Down Server
Press ctrl+c to shut down server


## Request Format

All POST endpoints expect a JSON payload with the following structure:

```json
{
    "user_email" : "jane.moneypenny@bankwell.com",
    "client_name": "Adam Clay",
    "client_email": "adam.clay@compass.com",
    "meeting_timestamp": "2024-03-26 11:00:00",
    "meeting_description": "Compass - Annual Credit Facility Review Meeting",
}
```

### Fields

- `client_name` (required): Name of the client
- `client_email` (required): Valid email address
- `meeting_timestamp` (required): Meeting time in `YYYY-MM-DD HH:MM:SS` format
- `meeting_description` (required): Description of the meeting
- `report_length` (optional): One of "short", "medium", or "long" (default: "long")

## Key Features Implemented

### 1. **Core API Endpoints**
- **POST** `/generate-report` - Execute graph and return JSON results
- **POST** `/generate-report/html` - Execute graph and return HTML report
- **POST** `/generate-report/pdf` - Execute graph and return PDF download
- **GET** `/health` - Health check for monitoring
- **GET** `/` - Basic health check

### 2. **Demo Endpoints for Testing**
- **GET** `/demo` - Demo with sample data (JSON)
- **GET** `/demo/html` - Demo with sample data (HTML)
- **GET** `/demo/pdf` - Demo with sample data (PDF)

### 3. **Input Validation & Error Handling**
- Comprehensive Pydantic models for request validation
- Email format validation
- Timestamp format validation (YYYY-MM-DD HH:MM:SS)
- Report length validation (short/medium/long)
- Proper HTTP status codes and error messages
- Timeout protection for long-running graph executions

### 4. **Multiple Output Formats**
- **JSON**: Raw graph execution results with metadata
- **HTML**: Styled reports using existing `output_utils` functions
- **PDF**: Downloadable PDF reports with proper filenames

### 5. **Configuration Management**
- Environment variable support
- CORS configuration for Outlook integration
- Configurable timeouts and rate limits
- Debug/production mode settings

### 6. **Security & Production Features**
- CORS middleware configured for Outlook domains
- Input sanitization and validation
- Comprehensive logging
- Error handling without information leakage
- Timeout protection

## Technical Implementation Details

### FastAPI Application (`main.py`)
- Uses async/await for non-blocking operations
- Implements graph execution with timeout protection using `asyncio.wait_for`
- Leverages existing `output_utils` for HTML/PDF generation
- Provides comprehensive error handling and logging

### Configuration System (`config.py`)
- Centralized settings management
- Environment variable override support
- Production-ready defaults
- CORS origins configured for Outlook integration

### Input/Output Models
```python
class ClientRequest(BaseModel):
    client_name: str
    client_email: str  # Validated
    meeting_timestamp: str  # Format validated
    meeting_description: str
    report_length: Optional[str] = "long"  # Validated against allowed values

class GraphResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
```

### Integration with Existing Codebase
The API seamlessly integrates with the existing Currensee codebase:
- Imports `compiled_graph` from `currensee.agents.complete_graph`
- Uses `generate_long_report`, `generate_med_report`, `generate_short_report` from `currensee.utils.output_utils`
- Maintains the same state structure as defined in `SupervisorState`

## How to Use

### 1. **Start the Server**
```bash
# Option 1: Use the startup script (recommended)
python api/server.py

# Option 2: Use uvicorn directly
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Option 3: With environment variables
export HOST=localhost PORT=8080 DEBUG=true
python api/server.py
```

### 2. **Test with the Browser Client**
Open `api/test_client.html` in a web browser to test all functionality interactively.

### 3. **API Request Example**
```bash
curl -X POST http://localhost:8000/generate-report/pdf \
  -H "Content-Type: application/json" \
  -d '{
    "user_email" : "jane.moneypenny@bankwell.com",
    "client_name": "Adam Clay",
    "client_email": "adam.clay@compass.com",
    "meeting_timestamp": "2024-03-26 11:00:00",
    "meeting_description": "Compass - Annual Credit Facility Review Meeting",
  }' \
  --output report.pdf
```

### 4. **Integration with Outlook Add-in**
The API is designed to work with Outlook add-ins:
- CORS configured for Outlook domains
- JSON/HTML/PDF output formats
- Proper error handling for UI consumption
- Timeout protection for user experience

## Testing

### Automated Tests (`test_api.py`)
- Health check validation
- Input validation testing
- Demo endpoint verification
- Error handling verification

### Interactive Testing (`test_client.html`)
- Web-based test interface
- Real-time API connectivity testing
- All output formats supported
- Pre-filled with sample data

### Manual Testing
```bash
# Run the test suite
python api/test_api.py

# Test specific endpoints
curl http://localhost:8000/health
curl http://localhost:8000/demo/html
```

## Production Considerations

### Security
- Currently no authentication (add as needed)
- CORS configured for specific domains
- Input validation and sanitization
- Error messages don't leak sensitive information

### Performance
- Async operation support
- Configurable timeouts (default: 5 minutes)
- Efficient PDF generation
- Proper memory management for large reports

### Monitoring
- Health check endpoints
- Comprehensive logging
- Execution time tracking
- Error tracking and reporting

### Deployment
- Environment variable configuration
- Production-ready defaults
- Support for Gunicorn with Uvicorn workers
- SSL/HTTPS ready

## Benefits for Outlook Integration

1. **Multiple Output Formats**: UI can choose JSON for processing, HTML for preview, or PDF for download
2. **CORS Support**: Configured to work with Outlook domains out of the box
3. **Error Handling**: Proper HTTP status codes and error messages for UI consumption
4. **Timeout Protection**: Prevents UI from hanging on long-running operations
5. **Validation**: Client-side validation errors are clearly communicated
6. **Demo Endpoints**: Easy testing and development support

## Next Steps

1. **Authentication**: Add OAuth or API key authentication if needed
2. **Rate Limiting**: Implement rate limiting for production use
3. **Caching**: Add caching for frequently generated reports
4. **Monitoring**: Add application performance monitoring
5. **SSL/HTTPS**: Configure SSL certificates for production
6. **Database**: Add database logging for audit trails
7. **Webhooks**: Add webhook support for async processing

The API is ready for immediate use and can be easily extended with additional features as needed.
