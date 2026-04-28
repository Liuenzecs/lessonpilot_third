from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.db import get_session
from app.core.security import get_current_user
from app.models import User
from app.schemas.style_profile import TeacherStyleProfileRead, TeacherStyleProfileUpdate
from app.services.style_analysis_service import suggest_style_updates
from app.services.style_profile_service import (
    get_style_profile,
    serialize_style_profile,
    update_style_profile,
)

router = APIRouter(prefix="/style-profile", tags=["style-profile"])


@router.get("", response_model=TeacherStyleProfileRead)
def read_style_profile(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> TeacherStyleProfileRead:
    return serialize_style_profile(get_style_profile(session, current_user.id))


@router.put("", response_model=TeacherStyleProfileRead)
def put_style_profile(
    payload: TeacherStyleProfileUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> TeacherStyleProfileRead:
    profile = update_style_profile(session, current_user.id, payload)
    return serialize_style_profile(profile)


@router.get("/suggestions")
def get_style_suggestions(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    result = suggest_style_updates(session, current_user.id)
    if result is None:
        return {"sample_count": 0, "suggestions": "需要至少 5 次 section 确认才能开始分析你的风格。"}
    return result

