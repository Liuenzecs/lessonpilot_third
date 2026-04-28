from __future__ import annotations

from sqlmodel import Session, select

from app.models import TeacherStyleProfile
from app.models.base import utcnow
from app.schemas.style_profile import TeacherStyleProfileRead, TeacherStyleProfileUpdate


def get_style_profile(session: Session, user_id: str) -> TeacherStyleProfile | None:
    return session.exec(select(TeacherStyleProfile).where(TeacherStyleProfile.user_id == user_id)).first()


def serialize_style_profile(profile: TeacherStyleProfile | None) -> TeacherStyleProfileRead:
    if profile is None:
        return TeacherStyleProfileRead()
    return TeacherStyleProfileRead(
        id=profile.id,
        enabled=profile.enabled,
        objective_style=profile.objective_style,
        process_style=profile.process_style,
        school_wording=profile.school_wording,
        activity_preferences=profile.activity_preferences,
        avoid_phrases=profile.avoid_phrases,
        sample_count=profile.sample_count,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


def update_style_profile(
    session: Session,
    user_id: str,
    payload: TeacherStyleProfileUpdate,
) -> TeacherStyleProfile:
    profile = get_style_profile(session, user_id)
    if profile is None:
        profile = TeacherStyleProfile(user_id=user_id)
    profile.enabled = payload.enabled
    profile.objective_style = payload.objective_style.strip()
    profile.process_style = payload.process_style.strip()
    profile.school_wording = payload.school_wording.strip()
    profile.activity_preferences = payload.activity_preferences.strip()
    profile.avoid_phrases = payload.avoid_phrases.strip()
    profile.updated_at = utcnow()
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


def format_teacher_style_context(profile: TeacherStyleProfile | None) -> str:
    if profile is None or not profile.enabled:
        return ""
    parts = [
        ("教学目标写法", profile.objective_style),
        ("教学过程风格", profile.process_style),
        ("学校提交措辞", profile.school_wording),
        ("常用课堂活动", profile.activity_preferences),
        ("避免套话", profile.avoid_phrases),
    ]
    lines = [f"- {label}：{value.strip()}" for label, value in parts if value.strip()]
    if not lines:
        return ""
    return "\n".join(
        [
            "【老师个人风格记忆】",
            "以下内容只影响表达方式和活动组织偏好，不得覆盖结构化 JSON、教学质量规则、引用事实或学校模板要求。",
            *lines,
        ]
    )


def get_teacher_style_context(session: Session, user_id: str) -> str:
    return format_teacher_style_context(get_style_profile(session, user_id))
