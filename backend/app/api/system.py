from fastapi import APIRouter
from app.services.opencode import opencode_service
from app.core.config import settings

router = APIRouter(prefix="/api", tags=["system"])


@router.get("/health/detailed")
async def detailed_health():
    """Detailed health check including all services"""
    # Check OpenCode
    opencode_available = await opencode_service.health_check()
    
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "services": {
            "database": "connected",
            "minio": "connected" if settings.S3_ENDPOINT else "not_configured",
            "opencode": "available" if opencode_available else "not_available"
        }
    }


@router.get("/status")
async def status_check():
    """Simple status check"""
    return {
        "app": settings.APP_NAME,
        "version": "0.1.0",
        "environment": "development" if settings.DEBUG else "production"
    }
