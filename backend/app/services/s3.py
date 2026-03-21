from minio import Minio
from minio.error import S3Error
from app.core.config import settings
import io
import uuid


class S3Service:
    def __init__(self):
        # Strip protocol prefix if present (Minio doesn't accept http://)
        endpoint = settings.S3_ENDPOINT.replace("http://", "").replace("https://", "")
        self.client = Minio(
            endpoint,
            access_key=settings.S3_ACCESS_KEY,
            secret_key=settings.S3_SECRET_KEY,
            secure=settings.S3_ENDPOINT.startswith("https")
        )
        self.bucket = settings.S3_BUCKET
        self._ensure_bucket()
    
    def _ensure_bucket(self):
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
        except S3Error as e:
            print(f"Error ensuring bucket: {e}")
    
    def upload_file(self, file_data: bytes, filename: str, content_type: str = "application/octet-stream") -> str:
        """Upload file and return the object key"""
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
        try:
            self.client.remove_object(self.bucket, object_name)
        except S3Error as e:
            raise Exception(f"Delete failed: {e}")
    
    def get_presigned_url(self, object_name: str, expires: int = 3600) -> str:
        """Get a presigned URL for temporary access"""
        try:
            return self.client.presigned_get_object(self.bucket, object_name, expires)
        except S3Error as e:
            raise Exception(f"Presigned URL failed: {e}")


# Singleton instance - lazy initialization
_s3_service = None

def get_s3_service():
    global _s3_service
    if _s3_service is None:
        _s3_service = S3Service()
    return _s3_service
