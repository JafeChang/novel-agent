from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class SkillBase(BaseModel):
    name: str
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class SkillCreate(SkillBase):
    code: str


class SkillUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    code: Optional[str] = None
    is_public: Optional[int] = None


class SkillResponse(SkillBase):
    id: int
    user_id: int
    code: str
    is_public: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SkillExecuteRequest(BaseModel):
    parameters: Optional[Dict[str, Any]] = None
    chapter_id: Optional[int] = None
    model: Optional[str] = None


class SkillExecuteResponse(BaseModel):
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
