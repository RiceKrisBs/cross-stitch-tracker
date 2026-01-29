"""
Cross-Stitch Tracker - Main Application
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Cross-Stitch Tracker", version="0.1.0")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Configure templates
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Homepage"""
    return templates.TemplateResponse(request, "index.html")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
