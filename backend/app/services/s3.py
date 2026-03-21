from minio import Minio
from minio.error import S3Error
from app.core.config import settings
import io
import uuid
import re


class S3Service:
    def __init__(self):
        endpoint = settings.S3_ENDPOINT
        # Remove protocol prefix if present (e.g., http:// or https://)
        endpoint = re.sub(r'^https?://', '', endpoint)
        # Remove trailing slashes
        endpoint = endpoint.rstrip('/')
        
        self.client = Minio(
            endpoint,
            access_key=settings.S3_ACCESS_KEY,
            secret_key=settings.S3_SECRET_KEY,
            secure=settings.S3_ENDPOINT.startswith('https')
        )
        self.bucket = settings.S3_BUCKET
        self._enabled = True
        try:
            self._ensure_bucket()
        except Exception as e:
            print(f"S3 not available: {e}. File uploads will be disabled.")
            self._enabled = False
    
    def _ensure_bucket(self):
        if not self._enabled:
            return
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
        except S3Error as e:
            print(f"Error ensuring bucket: {e}")
    
    def upload_file(self, file_data: bytes, filename: str, content_type: str = "application/octet-stream") -> str:
        """Upload file and return the object key"""
        if not self._enabled:
            raise Exception("S3 is not configured")
        object_name = f"{uuid.uuid4()}_{filename}"
        try:
            self.client.put_object(
                self.bucket,
                object_name,
                io.BytesIO(file_data),
                len(file_data),
                content_type=content_type
            )
            return object_name
        except S3Error as e:
            raise Exception(f"Upload failed: {e}")
    
    def download_file(self, object_name: str) -> bytes:
        """Download file and return bytes"""
        if not self._enabled:
            raise Exception("S3 is not configured")
        try:
            response = self.client.get_object(self.bucket, object_name)
            return response.read()
        except S3Error as e:
            raise Exception(f"Download failed: {e}")
        finally:
            response.close()
            response.release_conn()
    
    def delete_file(self, object_name: str):
        """Delete a file"""
        if not self._enabled:
            return
        try:
            self.client.remove_object(self.bucket, object_name)
        except S3Error as e:
            raise Exception(f"Delete failed: {e}")
    
    def get_presigned_url(self, object_name: str, expires: int = 3600) -> str:
        """Get a presigned URL for temporary access"""
        if not self._enabled:
            raise Exception("S3 is not configured")
        try:
            return self.client.presigned_get_object(self.bucket, object_name, expires)
        except S3Error as e:
            raise Exception(f"Presigned URL failed: {e}")


# Singleton instance
try:
    s3_service = S3Service()
except Exception as e:
    print(f"Failed to initialize S3 service: {e}")
    s3_service = None
