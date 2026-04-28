"""学期备课包服务 — 单元管理 + 整学期批量生成。"""

from __future__ import annotations

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.semester import LessonScheduleEntry, Semester, WeekSchedule
from app.models.task import Task
from app.models.teaching_unit import TeachingUnit
from app.schemas.teaching_unit import (
    SemesterPackageRequest,
    TeachingUnitCreate,
    TeachingUnitUpdate,
)


def _serialize_unit(u: TeachingUnit) -> dict:
    return {
        "id": u.id,
        "semester_id": u.semester_id,
        "name": u.name,
        "order": u.order,
        "topic_overview": u.topic_overview,
        "created_at": u.created_at,
        "updated_at": u.updated_at,
    }


def create_unit(
    session: Session, semester_id: str, user_id: str, payload: TeachingUnitCreate
) -> dict:
    _verify_semester_owner(session, semester_id, user_id)
    u = TeachingUnit(
        semester_id=semester_id,
        name=payload.name,
        order=payload.order,
        topic_overview=payload.topic_overview,
    )
    session.add(u)
    session.commit()
    session.refresh(u)
    return _serialize_unit(u)


def list_units(session: Session, semester_id: str, user_id: str) -> list[dict]:
    _verify_semester_owner(session, semester_id, user_id)
    stmt = (
        select(TeachingUnit)
        .where(TeachingUnit.semester_id == semester_id)
        .order_by(TeachingUnit.order)
    )
    rows = session.exec(stmt).all()
    return [_serialize_unit(r) for r in rows]


def update_unit(
    session: Session, unit_id: str, user_id: str, payload: TeachingUnitUpdate
) -> dict:
    u = session.get(TeachingUnit, unit_id)
    if not u:
        raise HTTPException(status_code=404, detail="教学单元不存在。")
    _verify_semester_owner(session, u.semester_id, user_id)
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(u, key, value)
    session.add(u)
    session.commit()
    session.refresh(u)
    return _serialize_unit(u)


def delete_unit(session: Session, unit_id: str, user_id: str) -> None:
    u = session.get(TeachingUnit, unit_id)
    if not u:
        raise HTTPException(status_code=404, detail="教学单元不存在。")
    _verify_semester_owner(session, u.semester_id, user_id)
    session.delete(u)
    session.commit()


def generate_semester_package(
    session: Session, semester_id: str, user_id: str, payload: SemesterPackageRequest
) -> dict:
    """为整个学期创建 Task 草稿（不启动生成，由前端逐个触发）。"""
    semester = _verify_semester_owner(session, semester_id, user_id)

    # Gather all schedule entries for this semester
    stmt = (
        select(LessonScheduleEntry)
        .join(WeekSchedule, WeekSchedule.id == LessonScheduleEntry.week_schedule_id)
        .where(WeekSchedule.semester_id == semester_id)
        .order_by(WeekSchedule.week_number, LessonScheduleEntry.day_of_week)
    )
    entries = session.exec(stmt).all()

    if not entries:
        raise HTTPException(status_code=400, detail="学期中没有排课条目，请先在日历中安排课程。")

    unit_map: dict[str, TeachingUnit] = {}
    if semester_id:
        units = session.exec(
            select(TeachingUnit).where(TeachingUnit.semester_id == semester_id)
        ).all()
        unit_map = {u.id: u for u in units}

    created_tasks: list[dict] = []
    seen_topics: set[str] = set()

    for entry in entries:
        task = session.get(Task, entry.task_id)
        if not task or task.user_id != user_id:
            continue

        topic_key = f"{task.topic}_{entry.class_group_id or ''}"
        if topic_key in seen_topics:
            continue
        seen_topics.add(topic_key)

        for doc_type in payload.doc_types:
            existing = session.exec(
                select(Task).where(
                    Task.base_task_id == task.id,
                    Task.class_group_id == entry.class_group_id,
                )
            ).first()
            if existing:
                continue

            class_group_id = entry.class_group_id or payload.class_group_id
            variant_title = task.title
            if class_group_id:
                from app.models.class_group import ClassGroup
                cg = session.get(ClassGroup, class_group_id)
                if cg:
                    variant_title = f"{task.title}（{cg.name}）"

            new_task = Task(
                user_id=user_id,
                title=variant_title,
                subject=task.subject,
                grade=task.grade,
                topic=task.topic,
                requirements=task.requirements,
                status="draft",
                scene=payload.scene or task.scene,
                lesson_type=doc_type if doc_type in ("lesson_plan", "study_guide") else task.lesson_type,
                class_hour=task.class_hour,
                lesson_category=task.lesson_category,
                template_id=payload.template_id or task.template_id,
                base_task_id=task.id,
                class_group_id=class_group_id,
            )
            session.add(new_task)
            created_tasks.append({
                "id": new_task.id,
                "title": new_task.title,
                "topic": new_task.topic,
                "doc_type": doc_type,
                "status": "draft",
            })

    session.commit()
    return {
        "total": len(created_tasks),
        "tasks": created_tasks,
    }


def _verify_semester_owner(session: Session, semester_id: str, user_id: str) -> Semester:
    semester = session.get(Semester, semester_id)
    if not semester or semester.user_id != user_id:
        raise HTTPException(status_code=404, detail="学期不存在。")
    return semester
