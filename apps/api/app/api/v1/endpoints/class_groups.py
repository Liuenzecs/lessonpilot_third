"""班级组 + 课题变体 API 端点。"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.db import get_session
from app.core.security import get_current_user
from app.models import User
from app.schemas.class_group import (
    ClassGroupCreate,
    ClassGroupRead,
    ClassGroupUpdate,
    CreateVariantRequest,
)
from app.services.class_group_service import (
    create_class_group,
    create_variant,
    delete_class_group,
    list_class_groups,
    list_variants,
    update_class_group,
)

router = APIRouter(prefix="/class-groups", tags=["class-groups"])


@router.post("", response_model=ClassGroupRead, status_code=201)
def create_class_group_endpoint(
    payload: ClassGroupCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    return create_class_group(session, current_user.id, payload)


@router.get("", response_model=list[ClassGroupRead])
def list_class_groups_endpoint(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    return list_class_groups(session, current_user.id)


@router.patch("/{class_group_id}", response_model=ClassGroupRead)
def update_class_group_endpoint(
    class_group_id: str,
    payload: ClassGroupUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    return update_class_group(session, class_group_id, current_user.id, payload)


@router.delete("/{class_group_id}", status_code=204)
def delete_class_group_endpoint(
    class_group_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> None:
    delete_class_group(session, class_group_id, current_user.id)


# Variant endpoints — registered under class-groups for grouping,
# but operate on tasks

@router.post("/tasks/{task_id}/variants", status_code=201)
def create_variant_endpoint(
    task_id: str,
    payload: CreateVariantRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    variant = create_variant(
        session,
        task_id,
        current_user.id,
        payload.class_group_id,
        payload.differentiation_level,
    )
    return {
        "id": variant.id,
        "title": variant.title,
        "status": variant.status,
        "class_group_id": variant.class_group_id,
        "base_task_id": variant.base_task_id,
        "subject": variant.subject,
        "grade": variant.grade,
        "topic": variant.topic,
        "created_at": variant.created_at.isoformat(),
    }


@router.get("/tasks/{task_id}/variants")
def list_variants_endpoint(
    task_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    return list_variants(session, task_id, current_user.id)
