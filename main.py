"""
Prompt Template Engine - FastAPI Web Application
"""
import uvicorn
import os
from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from typing import Optional

from app.database import db_manager
from app.routes.api import api_router
from app.routes.web import web_router

from dotenv import load_dotenv
load_dotenv()
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for FastAPI"""
    # Initialize database on startup
    await db_manager.init_db()
    print("Database initialized successfully")
    yield
    # Cleanup on shutdown (if needed)

# Create FastAPI application
app = FastAPI(
    title="Prompt Template Engine",
    description="A web application for managing and generating prompt templates with AI assistance",
    version="1.0.0",
    lifespan=lifespan
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(api_router, prefix="/api", tags=["API"])
app.include_router(web_router, prefix="", tags=["Web"])

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Custom 404 page"""
    return templates.TemplateResponse(
        "404.html", 
        {"request": request}, 
        status_code=404
    )

@app.exception_handler(500)
async def server_error_handler(request: Request, exc: HTTPException):
    """Custom 500 page"""
    return templates.TemplateResponse(
        "500.html", 
        {"request": request}, 
        status_code=500
    )

def main():
    """Main function to run the application"""
    print("Starting Prompt Template Engine...")
    
    # Get host and port from environment variables (for Railway deployment)
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False,  # Disable reload in production
        log_level="info"
    )

if __name__ == "__main__":
    main()
