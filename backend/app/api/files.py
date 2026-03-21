from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.s3 import s3_service

router = APIRouter(prefix="/api/files", tags=["files"])


def get_s3():
    if s3_service is None:
        raise HTTPException(status_code=503, detail="S3 storage is not configured")
    return s3_service


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload a file to S3"""
    try:
        contents = await file.read()
        object_name = get_s3().upload_file(
            contents,
            file.filename,
            file.content_type or "application/octet-stream"
        )
        return {"key": object_name, "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{object_name}")
async def download_file(
    object_name: str,
    current_user: User = Depends(get_current_user)
):
    """Download a file from S3"""
    try:
        contents = get_s3().download_file(object_name)
        return Response(content=contents, media_type="application/octet-stream")
    except Exception as e:
        raise HTTPException(status_code=404, detail="File not found")


@router.delete("/{object_name}")
async def delete_file(
    object_name: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a file from S3"""
    try:
        get_s3().delete_file(object_name)
        return {"message": "File deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{object_name}/url")
async def get_file_url(
    object_name: str,
    current_user: User = Depends(get_current_user)
):
    """Get a presigned URL for the file"""
    try:
        url = get_s3().get_presigned_url(object_name)
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
