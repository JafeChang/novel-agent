from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, FileResponse
import os
from app.core.config import settings
from app.api import auth, projects, chapters, skills, files, system

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

# Serve frontend static files
# Try multiple possible locations (Docker copies frontend/ to /app, not /app/frontend/)
possible_paths = [
    "/app/dist",
    "/app/frontend/dist",
    os.path.join(os.path.dirname(__file__), "../../dist"),
    os.path.join(os.path.dirname(__file__), "../dist"),
]
frontend_dist = None
for p in possible_paths:
    if os.path.exists(os.path.join(p, "index.html")):
        frontend_dist = p
        break

print(f"Frontend dist path: {frontend_dist}")

if frontend_dist:
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")
    
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
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Warning: Could not create database tables: {e}")


@app.get("/health")
def health_check():
    return {"status": "healthy", "app": settings.APP_NAME}
