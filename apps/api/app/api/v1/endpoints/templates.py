from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.core.db import get_session
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.template import TemplateCreate, TemplateRead, TemplateUpdate, TemplateSectionRead
from app.services import template_service

router = APIRouter()

@router.get("/", response_model=list[TemplateRead])
def read_templates(
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    subject: str | None = Query(None, description="学科过滤"),
    grade: str | None = Query(None, description="年级过滤"),
    is_public: bool | None = Query(None, description="是否公开"),
) -> list[TemplateRead]:
    return template_service.get_templates(
        session=session, skip=skip, limit=limit, subject=subject, grade=grade, is_public=is_public
    )

@router.post("/", response_model=TemplateRead, status_code=status.HTTP_201_CREATED)
def create_template(
    *,
    session: Session = Depends(get_session),
    template_in: TemplateCreate,
    current_user: User = Depends(get_current_user),
) -> TemplateRead:
    return template_service.create_template(session=session, template_in=template_in)

@router.get("/{template_id}", response_model=TemplateRead)
def read_template(
    template_id: str,
    session: Session = Depends(get_session),
) -> TemplateRead:
    template = template_service.get_template(session=session, template_id=template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )
    return template

@router.patch("/{template_id}", response_model=TemplateRead)
def update_template(
    template_id: str,
    template_in: TemplateUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> TemplateRead:
    template = template_service.get_template(session=session, template_id=template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )
    return template_service.update_template(session=session, db_template=template, template_in=template_in)

@router.get("/{template_id}/sections", response_model=list[TemplateSectionRead])
def read_template_sections(
    template_id: str,
    session: Session = Depends(get_session),
) -> list[TemplateSectionRead]:
    template = template_service.get_template(session=session, template_id=template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template_service.get_template_sections(session=session, template_id=template_id)
