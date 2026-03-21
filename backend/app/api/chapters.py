from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.chapter import Chapter, ChapterStatus
from app.schemas.chapter import ChapterCreate, ChapterUpdate, ChapterResponse

router = APIRouter(prefix="/api", tags=["chapters"])


def get_project_for_user(project_id: int, user_id: int, db: Session):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == user_id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("/projects/{project_id}/chapters", response_model=List[ChapterResponse])
def list_chapters(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = get_project_for_user(project_id, current_user.id, db)
    chapters = db.query(Chapter).filter(Chapter.project_id == project.id).order_by(Chapter.order).all()
    return chapters


@router.post("/projects/{project_id}/chapters", response_model=ChapterResponse, status_code=status.HTTP_201_CREATED)
def create_chapter(
    project_id: int,
    chapter_data: ChapterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = get_project_for_user(project_id, current_user.id, db)
    
    # Calculate word count
    word_count = len(chapter_data.content) if chapter_data.content else 0
    
    chapter = Chapter(
        project_id=project.id,
        title=chapter_data.title,
        content=chapter_data.content,
        order=chapter_data.order,
        word_count=word_count
    )
    db.add(chapter)
    db.commit()
    db.refresh(chapter)
    return chapter


@router.get("/chapters/{chapter_id}", response_model=ChapterResponse)
def get_chapter(
    chapter_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    chapter = db.query(Chapter).join(Project).filter(
        Chapter.id == chapter_id,
        Project.user_id == current_user.id
    ).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return chapter


@router.put("/chapters/{chapter_id}", response_model=ChapterResponse)
def update_chapter(
    chapter_id: int,
    chapter_data: ChapterUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    chapter = db.query(Chapter).join(Project).filter(
        Chapter.id == chapter_id,
        Project.user_id == current_user.id
    ).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    if chapter_data.title is not None:
        chapter.title = chapter_data.title
    if chapter_data.content is not None:
        chapter.content = chapter_data.content
        chapter.word_count = len(chapter_data.content)
    if chapter_data.order is not None:
        chapter.order = chapter_data.order
    if chapter_data.status is not None:
        chapter.status = chapter_data.status
    
    db.commit()
    db.refresh(chapter)
    return chapter


@router.delete("/chapters/{chapter_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chapter(
    chapter_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    chapter = db.query(Chapter).join(Project).filter(
        Chapter.id == chapter_id,
        Project.user_id == current_user.id
    ).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    db.delete(chapter)
    db.commit()
