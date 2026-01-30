"""
Cross-Stitch Tracker - Main Application
"""

from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app import auth
from app.routers import auth as auth_router

app = FastAPI(title="Cross-Stitch Tracker", version="0.1.0")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Configure templates
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(auth_router.router)


@app.get("/", response_class=HTMLResponse)
async def root(
    request: Request,
    user=Depends(auth.get_current_user_optional),
):
    """Homepage"""
    return templates.TemplateResponse(request, "index.html", {"user": user})


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
