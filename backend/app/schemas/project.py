from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.chapter import ChapterResponse


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class ProjectResponse(ProjectBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    chapters: List[ChapterResponse] = []
    
    class Config:
        from_attributes = True
