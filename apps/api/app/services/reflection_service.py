"""教学反思服务 — CRUD + 反思上下文检索用于下次备课。"""

from __future__ import annotations

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.task import Task
from app.models.teaching_reflection import TeachingReflection
from app.schemas.teaching_reflection import TeachingReflectionCreate


def _serialize_reflection(r: TeachingReflection) -> dict:
    return {
        "id": r.id,
        "task_id": r.task_id,
        "user_id": r.user_id,
        "goal_achievement": r.goal_achievement,
        "difficulty_handling": r.difficulty_handling,
        "student_response": r.student_response,
        "time_feedback": r.time_feedback,
        "improvement_notes": r.improvement_notes,
        "free_text": r.free_text,
        "created_at": r.created_at,
        "updated_at": r.updated_at,
    }


def create_reflection(
    session: Session, task_id: str, user_id: str, payload: TeachingReflectionCreate
) -> dict:
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="备课任务不存在。")

    r = TeachingReflection(
        task_id=task_id,
        user_id=user_id,
        goal_achievement=payload.goal_achievement,
        difficulty_handling=payload.difficulty_handling,
        student_response=payload.student_response,
        time_feedback=payload.time_feedback,
        improvement_notes=payload.improvement_notes,
        free_text=payload.free_text,
    )
    session.add(r)
    session.commit()
    session.refresh(r)
    return _serialize_reflection(r)


def list_reflections(session: Session, task_id: str, user_id: str) -> list[dict]:
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="备课任务不存在。")

    stmt = (
        select(TeachingReflection)
        .where(TeachingReflection.task_id == task_id)
        .order_by(TeachingReflection.created_at.desc())
    )
    rows = session.exec(stmt).all()
    return [_serialize_reflection(r) for r in rows]


def get_reflection_context(session: Session, user_id: str, subject: str, grade: str) -> str:
    """检索教师该学科/年级的历史反思改进建议，用于下次备课注入。"""
    stmt = (
        select(TeachingReflection)
        .where(TeachingReflection.user_id == user_id)
        .order_by(TeachingReflection.created_at.desc())
        .limit(5)
    )
    rows = session.exec(stmt).all()
    if not rows:
        return ""

    relevant_notes: list[str] = []
    for r in rows:
        if r.improvement_notes and r.improvement_notes.strip():
            relevant_notes.append(r.improvement_notes.strip())

    if not relevant_notes:
        return ""

    return (
        "【历史教学反思参考】\n"
        + "\n".join(f"- {note}" for note in relevant_notes[:3])
    )
