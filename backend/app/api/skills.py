from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import httpx
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.user import User
from app.models.skill import Skill
from app.schemas.skill import SkillCreate, SkillUpdate, SkillResponse, SkillExecuteRequest, SkillExecuteResponse

router = APIRouter(prefix="/api/skills", tags=["skills"])


@router.get("", response_model=List[SkillResponse])
def list_skills(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    include_public: bool = False
):
    query = db.query(Skill).filter(
        (Skill.user_id == current_user.id) | (Skill.is_public == 1)
    )
    return query.all()


@router.post("", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
def create_skill(
    skill_data: SkillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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
    skill = db.query(Skill).filter(
        Skill.id == skill_id,
        (Skill.user_id == current_user.id) | (Skill.is_public == 1)
    ).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    # Build the prompt for OpenCode
    parameters = request.parameters or {}
    prompt = f"""
## Skill: {skill.name}

{skill.description or ''}

### Configuration:
```json
{skill.config or '{}'}
```

### User Parameters:
```json
{parameters}
```

### Skill Code:
{skill.code}

Please execute this skill and return the result.
"""
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{settings.OPENCODE_API_URL}/execute",
                json={"prompt": prompt}
            )
            response.raise_for_status()
            result = response.json()
            return SkillExecuteResponse(
                success=True,
                output=result.get("output")
            )
    except httpx.HTTPError as e:
        return SkillExecuteResponse(
            success=False,
            error=str(e)
        )
