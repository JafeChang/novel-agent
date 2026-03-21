from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
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


@app.get("/")
def root():
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
