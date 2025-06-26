import io
import asyncio
from datetime import datetime
from typing import Optional
import logging

from fastapi import FastAPI, HTTPException, Response, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel, Field, validator

from currensee.agents.complete_graph import compiled_graph
from currensee.utils.output_utils import (
    convert_html_to_pdf,
    generate_long_report,
    generate_med_report,
    generate_short_report,
)
from currensee.api.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    description="API for serving Currensee agent graph results and generating PDF reports",
    version=settings.VERSION,
    debug=settings.DEBUG,
)

# Add CORS middleware to allow requests from Outlook
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if not settings.DEBUG else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class ClientRequest(BaseModel):
    """Request model for client meeting preparation"""
    client_name: str = Field(..., description="Name of the client", min_length=1)
    client_email: str = Field(..., description="Email address of the client")
    meeting_timestamp: str = Field(..., description="Timestamp of the meeting (YYYY-MM-DD HH:MM:SS)")
    meeting_description: str = Field(..., description="Description of the meeting", min_length=1)
    report_length: Optional[str] = Field(
        default="long", 
        description="Length of the report: 'short', 'medium', or 'long'"
    )
    
    @validator('client_email')
    def validate_email(cls, v):
        """Basic email validation"""
        if '@' not in v or '.' not in v:
            raise ValueError('Invalid email format')
        return v
    
    @validator('report_length')
    def validate_report_length(cls, v):
        """Validate report length is one of allowed values"""
        if v and v not in settings.ALLOWED_REPORT_LENGTHS:
            raise ValueError(f'Report length must be one of: {settings.ALLOWED_REPORT_LENGTHS}')
        return v or settings.DEFAULT_REPORT_LENGTH
    
    @validator('meeting_timestamp')
    def validate_timestamp(cls, v):
        """Validate timestamp format"""
        try:
            datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise ValueError('Timestamp must be in format YYYY-MM-DD HH:MM:SS')
        return v


class GraphResponse(BaseModel):
    """Response model for graph execution results"""
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Currensee API is running", "timestamp": datetime.now().isoformat()}


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "service": "currensee-api"}


@app.post("/generate-report", response_model=GraphResponse)
async def generate_report(request: ClientRequest):
    """
    Execute the compiled graph with client data and return the results
    """
    try:
        start_time = datetime.now()
        logger.info(f"Starting report generation for client: {request.client_name}")
        
        # Prepare the initial state for the graph
        init_state = {
            "client_name": request.client_name,
            "client_email": request.client_email,
            "meeting_timestamp": request.meeting_timestamp,
            "meeting_description": request.meeting_description,
            "report_length": request.report_length or "long",
        }
        
        # Execute the compiled graph with timeout
        try:
            result = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None, 
                    compiled_graph.invoke, 
                    init_state
                ),
                timeout=settings.GRAPH_EXECUTION_TIMEOUT
            )
        except asyncio.TimeoutError:
            logger.error(f"Graph execution timeout for client: {request.client_name}")
            return GraphResponse(
                success=False,
                error=f"Graph execution timeout after {settings.GRAPH_EXECUTION_TIMEOUT} seconds"
            )
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        logger.info(f"Report generation completed for client: {request.client_name} in {execution_time:.2f}s")
        
        return GraphResponse(
            success=True,
            data=result,
            execution_time=execution_time
        )
        
    except Exception as e:
        logger.error(f"Error generating report for client {request.client_name}: {str(e)}")
        return GraphResponse(
            success=False,
            error=str(e)
        )


@app.post("/generate-report/html")
async def generate_report_html(request: ClientRequest):
    """
    Generate and return HTML report for the given client meeting
    """
    try:
        # Prepare the initial state for the graph
        init_state = {
            "client_name": request.client_name,
            "client_email": request.client_email,
            "meeting_timestamp": request.meeting_timestamp,
            "meeting_description": request.meeting_description,
            "report_length": request.report_length or "long",
        }
        
        # Execute the compiled graph
        result = compiled_graph.invoke(init_state)
        
        # Generate HTML based on report length
        report_length = request.report_length or "long"
        
        if report_length == "short":
            html_content = generate_short_report(result)
        elif report_length == "medium":
            html_content = generate_med_report(result)
        else:  # long
            html_content = generate_long_report(result)
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-report/pdf")
async def generate_report_pdf(request: ClientRequest):
    """
    Generate and return PDF report for the given client meeting
    """
    try:
        # Prepare the initial state for the graph
        init_state = {
            "client_name": request.client_name,
            "client_email": request.client_email,
            "meeting_timestamp": request.meeting_timestamp,
            "meeting_description": request.meeting_description,
            "report_length": request.report_length or "long",
        }
        
        # Execute the compiled graph
        result = compiled_graph.invoke(init_state)
        
        # Generate HTML based on report length
        report_length = request.report_length or "long"
        
        if report_length == "short":
            html_content = generate_short_report(result)
        elif report_length == "medium":
            html_content = generate_med_report(result)
        else:  # long
            html_content = generate_long_report(result)
        
        # Convert HTML to PDF
        pdf_buffer = io.BytesIO()
        convert_html_to_pdf(html_content, pdf_buffer)
        pdf_buffer.seek(0)
        
        # Generate filename with meeting description and timestamp
        safe_meeting_desc = "".join(c for c in request.meeting_description if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_meeting_desc = safe_meeting_desc.replace(' ', '_')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"currensee_report_{safe_meeting_desc}_{timestamp}.pdf"
        
        return StreamingResponse(
            io.BytesIO(pdf_buffer.read()),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/demo")
async def demo_endpoint():
    """
    Demo endpoint with sample data for testing
    """
    try:
        # Sample data similar to the main() function in complete_graph.py
        demo_request = ClientRequest(
            client_name="Adam Clay",
            client_email="adam.clay@compass.com",
            meeting_timestamp="2024-03-26 11:00:00",
            meeting_description="Compass - Annual Credit Facility Review Meeting",
            report_length="long"
        )
        
        return await generate_report(demo_request)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/demo/html")
async def demo_html():
    """
    Demo endpoint returning HTML report with sample data
    """
    try:
        demo_request = ClientRequest(
            client_name="Adam Clay",
            client_email="adam.clay@compass.com",
            meeting_timestamp="2024-03-26 11:00:00",
            meeting_description="Compass - Annual Credit Facility Review Meeting",
            report_length="long"
        )
        
        return await generate_report_html(demo_request)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/demo/pdf")
async def demo_pdf():
    """
    Demo endpoint returning PDF report with sample data
    """
    try:
        demo_request = ClientRequest(
            client_name="Adam Clay",
            client_email="adam.clay@compass.com",
            meeting_timestamp="2024-03-26 11:00:00",
            meeting_description="Compass - Annual Credit Facility Review Meeting",
            report_length="long"
        )
        
        return await generate_report_pdf(demo_request)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
