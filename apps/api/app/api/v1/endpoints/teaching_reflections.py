"""教学反思 API 端点。"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.db import get_session
from app.core.security import get_current_user
from app.models import User
from app.schemas.teaching_reflection import TeachingReflectionCreate, TeachingReflectionRead
from app.services.reflection_service import create_reflection, list_reflections

router = APIRouter(tags=["reflections"])


@router.post("/tasks/{task_id}/reflections", response_model=TeachingReflectionRead, status_code=201)
def create_reflection_endpoint(
    task_id: str,
    payload: TeachingReflectionCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    return create_reflection(session, task_id, current_user.id, payload)


@router.get("/tasks/{task_id}/reflections", response_model=list[TeachingReflectionRead])
def list_reflections_endpoint(
    task_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    return list_reflections(session, task_id, current_user.id)
