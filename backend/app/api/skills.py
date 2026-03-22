from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.skill import Skill
from app.models.chapter import Chapter
from app.models.project import Project
from app.schemas.skill import SkillCreate, SkillUpdate, SkillResponse, SkillExecuteRequest, SkillExecuteResponse
from app.services.opencode import opencode_service
from app.services.default_skills import ensure_default_public_novel_skill

router = APIRouter(prefix="/api/skills", tags=["skills"])


@router.get("", response_model=List[SkillResponse])
def list_skills(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all skills (user's own + public skills)"""
    ensure_default_public_novel_skill(db, current_user.id)
    skills = db.query(Skill).filter(
        (Skill.user_id == current_user.id) | (Skill.is_public == 1)
    ).all()
    return skills


@router.post("", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
def create_skill(
    skill_data: SkillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new skill"""
    skill = Skill(
        user_id=current_user.id,
        name=skill_data.name,
        description=skill_data.description,
        config=skill_data.config,
        code=skill_data.code
    )
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill


@router.get("/{skill_id}", response_model=SkillResponse)
def get_skill(
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific skill"""
    skill = db.query(Skill).filter(
        Skill.id == skill_id,
        (Skill.user_id == current_user.id) | (Skill.is_public == 1)
    ).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


@router.put("/{skill_id}", response_model=SkillResponse)
def update_skill(
    skill_id: int,
    skill_data: SkillUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a skill (only owner can update)"""
    skill = db.query(Skill).filter(
        Skill.id == skill_id,
        Skill.user_id == current_user.id
    ).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found or not owned by you")
    
    if skill_data.name is not None:
        skill.name = skill_data.name
    if skill_data.description is not None:
        skill.description = skill_data.description
    if skill_data.config is not None:
        skill.config = skill_data.config
    if skill_data.code is not None:
        skill.code = skill_data.code
    if skill_data.is_public is not None:
        skill.is_public = skill_data.is_public
    
    db.commit()
    db.refresh(skill)
    return skill


@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_skill(
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a skill (only owner can delete)"""
    skill = db.query(Skill).filter(
        Skill.id == skill_id,
        Skill.user_id == current_user.id
    ).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found or not owned by you")
    
    db.delete(skill)
    db.commit()


@router.post("/{skill_id}/execute", response_model=SkillExecuteResponse)
async def execute_skill(
    skill_id: int,
    request: SkillExecuteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Execute a skill using OpenCode"""
    # Get the skill
    skill = db.query(Skill).filter(
        Skill.id == skill_id,
        (Skill.user_id == current_user.id) | (Skill.is_public == 1)
    ).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    # Build execution context
    context = {}
    parameters = request.parameters or {}
    
    # If chapter_id provided, get chapter content for context
    if request.chapter_id:
        chapter = db.query(Chapter).join(Project).filter(
            Chapter.id == request.chapter_id,
            Project.user_id == current_user.id
        ).first()
        if chapter:
            context["chapter_content"] = chapter.content or ""
    
    # Add config parameters
    if skill.config:
        context["parameters"] = parameters
        if "style" in skill.config:
            context["style"] = skill.config["style"]
    
    # Build the prompt from skill code
    prompt = f"""## Skill: {skill.name}

{skill.description or ''}

### Skill Code:
{skill.code}

---
Please execute this skill according to the code above."""

    # Execute via OpenCode
    result = await opencode_service.execute_skill(prompt, context)
    
    return SkillExecuteResponse(
        success=result["success"],
        output=result.get("output"),
        error=result.get("error")
    )


@router.get("/{skill_id}/preview")
async def preview_skill(
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Preview skill configuration and code"""
    skill = db.query(Skill).filter(
        Skill.id == skill_id,
        (Skill.user_id == current_user.id) | (Skill.is_public == 1)
    ).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    return {
        "id": skill.id,
        "name": skill.name,
        "description": skill.description,
        "config": skill.config,
        "code": skill.code,
        "is_public": skill.is_public,
        "config_preview": skill.config or {}
    }
