import asyncio
import io
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, validator

from currensee.agents.complete_graph import compiled_graph
from currensee.api.config import settings
from currensee.utils.output_utils_dynamic import (
    generate_report as generate_report_html_content,
    format_news_summary_to_html,
    format_paragraph_summary_to_html,
    save_html_to_file,
    convert_html_to_pdf,
)

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

    user_email: str = Field(...,description="Email address of the user")
    client_name: str = Field(..., description="Name of the client", min_length=1)
    client_email: str = Field(..., description="Email address of the client")
    meeting_timestamp: str = Field(
        ..., description="Timestamp of the meeting (YYYY-MM-DD HH:MM:SS)"
    )
    meeting_description: str = Field(
        ..., description="Description of the meeting", min_length=1
    )
    #report_length: Optional[str] = Field(
    #    default="long", description="Length of the report: 'short', 'medium', or 'long'"
    #)

    @validator("client_email", "user_email")
    def validate_email(cls, v):
        """Basic email validation"""
        if "@" not in v or "." not in v:
            raise ValueError("Invalid email format")
        return v

   # @validator("report_length")
   # def validate_report_length(cls, v):
   #     """Validate report length is one of allowed values"""
   #     if v and v not in settings.ALLOWED_REPORT_LENGTHS:
    #        raise ValueError(
    #            f"Report length must be one of: {settings.ALLOWED_REPORT_LENGTHS}"
    #        )
     #   return v or settings.DEFAULT_REPORT_LENGTH

    @validator("meeting_timestamp")
    def validate_timestamp(cls, v):
        """Validate timestamp format"""
        try:
            datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise ValueError("Timestamp must be in format YYYY-MM-DD HH:MM:SS")
        return v


class GraphResponse(BaseModel):
    """Response model for graph execution results"""

    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None


# Access outlook.html tempalate
BASE_DIR = Path(__file__).resolve().parents[3]
#templates = Jinja2Templates(directory=BASE_DIR / "ui" / "templates")

# Mount static files from ui folder
app.mount("/static", StaticFiles(directory=BASE_DIR / "ui"), name="static")


@app.get("/", response_class=HTMLResponse)
async def serve_notification():
    """Serve the notification HTML UI at root /"""
    notification_path = BASE_DIR / "ui" / "notification.html"
    if not notification_path.exists():
        return HTMLResponse(
            content="<h1>Notification HTML file not found</h1>", status_code=404
        )
    content = notification_path.read_text(encoding="utf-8")
    return HTMLResponse(content=content)


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "currensee-api",
        "timestamp": datetime.now().isoformat(),
    }


#@app.get("/report", response_class=HTMLResponse)
#async def serve_html_report(
#    client_name: str = Query(...),
#    client_email: str = Query(...),
#    meeting_timestamp: str = Query(...),
#    meeting_description: str = Query(...),
#    user_email: str = "placeholder@demo.com", 
#):
#    try:
#        init_state = {
#            "user_email": user_email,
#            "client_name": client_name,
#            "client_email": client_email,
#            "meeting_timestamp": meeting_timestamp,
#            "meeting_description": meeting_description,
#        }
#        result = compiled_graph.invoke(init_state)
#        html_content = generate_report(result)
#        return HTMLResponse(content=html_content)
#    except Exception as e:
#        raise HTTPException(status_code=500, detail=str(e))


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
            "user_email": request.user_email,
            "client_name": request.client_name,
            "client_email": request.client_email,
            "meeting_timestamp": request.meeting_timestamp,
            "meeting_description": request.meeting_description,
            #"report_length": request.report_length or "long",
        }

        # Execute the compiled graph with timeout
        try:
            result = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None, compiled_graph.invoke, init_state
                ),
                timeout=settings.GRAPH_EXECUTION_TIMEOUT,
            )
        except asyncio.TimeoutError:
            logger.error(f"Graph execution timeout for client: {request.client_name}")
            return GraphResponse(
                success=False,
                error=f"Graph execution timeout after {settings.GRAPH_EXECUTION_TIMEOUT} seconds",
            )

        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        logger.info(
            f"Report generation completed for client: {request.client_name} in {execution_time:.2f}s"
        )

        return GraphResponse(success=True, data=result, execution_time=execution_time)

    except Exception as e:
        logger.error(
            f"Error generating report for client {request.client_name}: {str(e)}"
        )
        return GraphResponse(success=False, error=str(e))


@app.post("/report-html")
async def generate_report_html(request: ClientRequest):
    try:
        init_state = {
            "user_email": request.user_email,
            "client_name": request.client_name,
            "client_email": request.client_email,
            "meeting_timestamp": request.meeting_timestamp,
            "meeting_description": request.meeting_description,
        }

        result = compiled_graph.invoke(init_state) 
        html_content = generate_report_html_content(result)
        print(f"html_content type: {type(html_content)}") 

        return HTMLResponse(content=html_content)

    except Exception as e:
        logger.exception("Error in generate_report_html")  # logs full traceback
        traceback_str = ''.join(traceback.format_exception(None, e, e.__traceback__))
        return JSONResponse(status_code=500, content={"detail": str(e), "trace": traceback_str})
        
        

@app.post("/generate-report/pdf")
async def generate_report_pdf(request: ClientRequest):
    """
    Generate and return PDF report for the given client meeting
    """
    try:
        # Prepare the initial state for the graph
        init_state = {
            "user_email": request.user_email,
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
        safe_meeting_desc = "".join(
            c
            for c in request.meeting_description
            if c.isalnum() or c in (" ", "-", "_")
        ).rstrip()
        safe_meeting_desc = safe_meeting_desc.replace(" ", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"currensee_report_{safe_meeting_desc}_{timestamp}.pdf"

        return StreamingResponse(
            io.BytesIO(pdf_buffer.read()),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/outlook", response_class=HTMLResponse)
async def serve_outlook():
    """Serve the Outlook HTML UI at /outlook"""
    outlook_path = BASE_DIR / "ui" / "outlook.html"
    if not outlook_path.exists():
        return HTMLResponse(
            content="<h1>Outlook HTML file not found</h1>", status_code=404
        )
    content = outlook_path.read_text(encoding="utf-8")
    return HTMLResponse(content=content)



@app.get("/demo")
async def demo_endpoint():
    """
    Demo endpoint with sample data for testing
    """
    try:
        # Sample data similar to the main() function in complete_graph.py
        demo_request = ClientRequest(
            user_email="jane.moneypenny@bankwell.com",
            client_name="Adam Clay",
            client_email="adam.clay@compass.com",
            meeting_timestamp="2024-03-26 11:00:00",
            meeting_description="Compass - Annual Credit Facility Review Meeting",
            report_length="long",
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
            user_email="jane.moneypenny@bankwell.com",
            client_name="Adam Clay",
            client_email="adam.clay@compass.com",
            meeting_timestamp="2024-03-26 11:00:00",
            meeting_description="Compass - Annual Credit Facility Review Meeting",
            report_length="long",
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
            user_email="jane.moneypenny@bankwell.com",
            client_name="Adam Clay",
            client_email="adam.clay@compass.com",
            meeting_timestamp="2024-03-26 11:00:00",
            meeting_description="Compass - Annual Credit Facility Review Meeting",
            report_length="long",
        )

        return await generate_report_pdf(demo_request)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)