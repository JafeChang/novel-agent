import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(tags=["spa"])


def _find_frontend_dist() -> str | None:
    possible_paths = [
        "/app/dist",
        "/app/frontend/dist",
        os.path.join(os.path.dirname(__file__), "../../../dist"),
        os.path.join(os.path.dirname(__file__), "../../dist"),
    ]
    for p in possible_paths:
        if os.path.exists(os.path.join(p, "index.html")):
            return p
    return None


@router.get("/{full_path:path}")
async def spa_fallback(full_path: str):
    """
    Serve frontend routes for client-side routing.
    Keep API/docs/static routes untouched and return 404 for them when missing.
    """
    reserved_prefixes = ("api/", "docs", "openapi.json", "redoc", "assets/", "health")
    if full_path.startswith(reserved_prefixes):
        raise HTTPException(status_code=404, detail="Not Found")

    frontend_dist = _find_frontend_dist()
    if frontend_dist:
        index_path = os.path.join(frontend_dist, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)

    raise HTTPException(status_code=404, detail="Not Found")
