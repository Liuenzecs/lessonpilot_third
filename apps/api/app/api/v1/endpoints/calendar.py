"""教学日历 API 端点。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.core.db import get_session
from app.core.security import get_current_user
from app.models import User
from app.schemas.calendar import (
    LessonScheduleEntryCreate,
    LessonScheduleEntryRead,
    LessonScheduleEntryUpdate,
    SemesterCreate,
    SemesterDetailRead,
    SemesterRead,
    SemesterUpdate,
    WeekScheduleRead,
    WeekScheduleUpdate,
)
from app.services.calendar_service import (
    add_entry,
    create_semester,
    delete_entry,
    delete_semester,
    get_semester_detail,
    list_semesters,
    update_entry,
    update_semester,
    update_week,
)

router = APIRouter(prefix="/calendar", tags=["calendar"])


@router.post("/semesters", response_model=SemesterRead, status_code=201)
def create_semester_endpoint(
    payload: SemesterCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> SemesterRead:
    return create_semester(session, current_user.id, payload)


@router.get("/semesters", response_model=list[SemesterRead])
def list_semesters_endpoint(
    grade: str | None = Query(None),
    subject: str | None = Query(None),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> list[SemesterRead]:
    return list_semesters(session, current_user.id, grade=grade, subject=subject)


@router.get("/semesters/{semester_id}", response_model=SemesterDetailRead)
def get_semester_endpoint(
    semester_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> SemesterDetailRead:
    return get_semester_detail(session, semester_id, current_user.id)


@router.patch("/semesters/{semester_id}", response_model=SemesterRead)
def update_semester_endpoint(
    semester_id: str,
    payload: SemesterUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> SemesterRead:
    return update_semester(session, semester_id, current_user.id, payload)


@router.delete("/semesters/{semester_id}", status_code=204)
def delete_semester_endpoint(
    semester_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> None:
    delete_semester(session, semester_id, current_user.id)


@router.patch("/weeks/{week_id}", response_model=WeekScheduleRead)
def update_week_endpoint(
    week_id: str,
    payload: WeekScheduleUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> WeekScheduleRead:
    return update_week(session, week_id, current_user.id, payload)


@router.post("/weeks/{week_id}/entries", response_model=LessonScheduleEntryRead, status_code=201)
def add_entry_endpoint(
    week_id: str,
    payload: LessonScheduleEntryCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> LessonScheduleEntryRead:
    return add_entry(session, week_id, current_user.id, payload)


@router.patch("/entries/{entry_id}", response_model=LessonScheduleEntryRead)
def update_entry_endpoint(
    entry_id: str,
    payload: LessonScheduleEntryUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> LessonScheduleEntryRead:
    return update_entry(session, entry_id, current_user.id, payload)


@router.delete("/entries/{entry_id}", status_code=204)
def delete_entry_endpoint(
    entry_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> None:
    delete_entry(session, entry_id, current_user.id)
