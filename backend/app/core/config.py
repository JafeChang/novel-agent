from pydantic import Field
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Novel Agent"
    DEBUG: bool = True

    # Database — reads DATABASE_URL from the environment (set automatically by
    # Railway's Postgres service); falls back to localhost for local development.
    DATABASE_URL: str = Field(
        default="postgresql://novel:novel@localhost:5432/novel_agent",
        validation_alias="DATABASE_URL",
    )
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # MinIO / S3
    S3_ENDPOINT: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET: str = "novel-agent"
    S3_REGION: str = "us-east-1"
    
    # OpenCode
    OPENCODE_CMD: str = "opencode"
    OPENCODE_CWD: str = "/home/node/.openclaw/workspace"
    
    # E2B (alternative to local OpenCode)
    E2B_API_KEY: str = ""
    E2B_SANDBOX_ID: str = ""
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
