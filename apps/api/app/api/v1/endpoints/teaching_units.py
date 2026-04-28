"""教学单元 + 学期备课包 API 端点。"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.db import get_session
from app.core.security import get_current_user
from app.models import User
from app.schemas.teaching_unit import (
    SemesterPackageRequest,
    TeachingUnitCreate,
    TeachingUnitRead,
    TeachingUnitUpdate,
)
from app.services.semester_package_service import (
    create_unit,
    delete_unit,
    generate_semester_package,
    list_units,
    update_unit,
)

router = APIRouter(prefix="/semesters", tags=["teaching-units"])


# Unit CRUD under a semester
@router.post("/{semester_id}/units", response_model=TeachingUnitRead, status_code=201)
def create_unit_endpoint(
    semester_id: str,
    payload: TeachingUnitCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    return create_unit(session, semester_id, current_user.id, payload)


@router.get("/{semester_id}/units", response_model=list[TeachingUnitRead])
def list_units_endpoint(
    semester_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    return list_units(session, semester_id, current_user.id)


@router.patch("/{semester_id}/units/{unit_id}", response_model=TeachingUnitRead)
def update_unit_endpoint(
    semester_id: str,
    unit_id: str,
    payload: TeachingUnitUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    return update_unit(session, unit_id, current_user.id, payload)


@router.delete("/{semester_id}/units/{unit_id}", status_code=204)
def delete_unit_endpoint(
    semester_id: str,
    unit_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> None:
    delete_unit(session, unit_id, current_user.id)


# Semester package generation
@router.post("/{semester_id}/generate-package")
def generate_package_endpoint(
    semester_id: str,
    payload: SemesterPackageRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    return generate_semester_package(session, semester_id, current_user.id, payload)
