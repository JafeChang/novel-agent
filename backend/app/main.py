import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, FileResponse
from app.core.config import settings
from app.api import auth, projects, chapters, skills, files, system, spa, plans

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    description="AI Novel Writing Platform with Custom Skills Support"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(chapters.router)
app.include_router(skills.router)
app.include_router(files.router)
app.include_router(system.router)
# Billing/entitlements + SPA fallback routers (kept together intentionally).
app.include_router(plans.router)
app.include_router(spa.router)

# Serve frontend static files
# Try multiple possible locations for different runtime layouts.
BASE_DIR = os.path.dirname(__file__)
possible_paths = [
    "/app/dist",
    "/app/frontend/dist",
    os.path.join(BASE_DIR, "../../../frontend/dist"),
    os.path.join(BASE_DIR, "../../frontend/dist"),
    os.path.join(BASE_DIR, "../../dist"),
    os.path.join(BASE_DIR, "../dist"),
]
frontend_dist = None
for p in possible_paths:
    if os.path.exists(os.path.join(p, "index.html")):
        frontend_dist = p
        break

print(f"Frontend dist path: {frontend_dist}")

if frontend_dist:
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")


@app.get("/favicon.svg")
async def favicon():
    if frontend_dist:
        favicon_path = os.path.join(frontend_dist, "favicon.svg")
        if os.path.exists(favicon_path):
            return FileResponse(favicon_path)
    raise HTTPException(status_code=404, detail="Not Found")


@app.get("/icons.svg")
async def icons():
    if frontend_dist:
        icons_path = os.path.join(frontend_dist, "icons.svg")
        if os.path.exists(icons_path):
            return FileResponse(icons_path)
    raise HTTPException(status_code=404, detail="Not Found")
    
@app.get("/")
async def root():
    """Serve frontend or redirect to docs if not built"""
    if frontend_dist:
        index_path = os.path.join(frontend_dist, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
    return RedirectResponse(url="/docs")


@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    from app.core.database import engine, Base
    # Ensure model modules are loaded before create_all.
    from app.models import user, project, chapter, skill, user_plan  # noqa: F401
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Warning: Could not create database tables: {e}")

    if frontend_dist:
        checks = {
            "index.html": os.path.exists(os.path.join(frontend_dist, "index.html")),
            "assets/": os.path.exists(os.path.join(frontend_dist, "assets")),
            "favicon.svg": os.path.exists(os.path.join(frontend_dist, "favicon.svg")),
            "icons.svg": os.path.exists(os.path.join(frontend_dist, "icons.svg")),
        }
        logger.info("Frontend static healthcheck | dist=%s | files=%s", frontend_dist, checks)
    else:
        logger.warning("Frontend static healthcheck | dist not found; '/' will redirect to /docs")


@app.get("/health")
def health_check():
    return {"status": "healthy", "app": settings.APP_NAME}


@app.get("/{full_path:path}")
async def spa_fallback(full_path: str):
    """
    Serve frontend routes for client-side routing.
    Keep API/docs/static routes untouched and return 404 for them when missing.
    """
    reserved_prefixes = ("api/", "docs", "openapi.json", "redoc", "assets/", "health")
    if full_path.startswith(reserved_prefixes):
        raise HTTPException(status_code=404, detail="Not Found")

    if frontend_dist:
        index_path = os.path.join(frontend_dist, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)

    raise HTTPException(status_code=404, detail="Not Found")
