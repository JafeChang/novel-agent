from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.chapter import ChapterStatus


class ChapterBase(BaseModel):
    title: str
    content: Optional[str] = None


class ChapterCreate(ChapterBase):
    order: Optional[int] = 0


class ChapterUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    order: Optional[int] = None
    status: Optional[ChapterStatus] = None


class ChapterResponse(ChapterBase):
    id: int
    project_id: int
    order: int
    status: ChapterStatus
    word_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
