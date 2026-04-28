"""班级组服务 — CRUD + 同课变体创建。"""

from __future__ import annotations

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.class_group import ClassGroup
from app.models.document import Document
from app.models.task import Task
from app.schemas.class_group import ClassGroupCreate, ClassGroupUpdate


def _serialize_class_group(cg: ClassGroup) -> dict:
    return {
        "id": cg.id,
        "user_id": cg.user_id,
        "name": cg.name,
        "level": cg.level,
        "notes": cg.notes,
        "created_at": cg.created_at,
        "updated_at": cg.updated_at,
    }


def create_class_group(
    session: Session, user_id: str, payload: ClassGroupCreate
) -> dict:
    cg = ClassGroup(
        user_id=user_id,
        name=payload.name,
        level=payload.level,
        notes=payload.notes,
    )
    session.add(cg)
    session.commit()
    session.refresh(cg)
    return _serialize_class_group(cg)


def list_class_groups(session: Session, user_id: str) -> list[dict]:
    stmt = (
        select(ClassGroup)
        .where(ClassGroup.user_id == user_id)
        .order_by(ClassGroup.created_at.desc())
    )
    rows = session.exec(stmt).all()
    return [_serialize_class_group(r) for r in rows]


def get_class_group(session: Session, class_group_id: str, user_id: str) -> ClassGroup:
    cg = session.get(ClassGroup, class_group_id)
    if not cg or cg.user_id != user_id:
        raise HTTPException(status_code=404, detail="班级组不存在。")
    return cg


def update_class_group(
    session: Session, class_group_id: str, user_id: str, payload: ClassGroupUpdate
) -> dict:
    cg = get_class_group(session, class_group_id, user_id)
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(cg, key, value)
    session.add(cg)
    session.commit()
    session.refresh(cg)
    return _serialize_class_group(cg)


def delete_class_group(
    session: Session, class_group_id: str, user_id: str
) -> None:
    cg = get_class_group(session, class_group_id, user_id)
    session.delete(cg)
    session.commit()


def create_variant(
    session: Session,
    base_task_id: str,
    user_id: str,
    class_group_id: str,
    differentiation_level: str,
) -> Task:
    """基于已有 task 创建班级变体。"""
    base_task = session.get(Task, base_task_id)
    if not base_task or base_task.user_id != user_id:
        raise HTTPException(status_code=404, detail="原备课任务不存在。")

    cg = get_class_group(session, class_group_id, user_id)

    variant_title = f"{base_task.title}（{cg.name}）"
    variant_task = Task(
        user_id=user_id,
        title=variant_title,
        subject=base_task.subject,
        grade=base_task.grade,
        topic=base_task.topic,
        requirements=base_task.requirements,
        status="draft",
        scene=base_task.scene,
        lesson_type=base_task.lesson_type,
        class_hour=base_task.class_hour,
        lesson_category=base_task.lesson_category,
        template_id=base_task.template_id,
        base_task_id=base_task_id,
        class_group_id=class_group_id,
    )
    session.add(variant_task)
    session.flush()

    # Copy documents from base task
    base_docs = session.exec(
        select(Document).where(Document.task_id == base_task_id)
    ).all()
    for doc in base_docs:
        variant_doc = Document(
            task_id=variant_task.id,
            user_id=user_id,
            doc_type=doc.doc_type,
            title=f"{variant_title}_{'学案' if doc.doc_type == 'study_guide' else '教案'}",
            content=doc.content,
            version=1,
        )
        session.add(variant_doc)

    session.commit()
    session.refresh(variant_task)
    return variant_task


def list_variants(
    session: Session, base_task_id: str, user_id: str
) -> list[dict]:
    """列出某个基础 task 的所有变体 task。"""
    base_task = session.get(Task, base_task_id)
    if not base_task or base_task.user_id != user_id:
        raise HTTPException(status_code=404, detail="原备课任务不存在。")

    stmt = (
        select(Task)
        .where(Task.base_task_id == base_task_id, Task.user_id == user_id)
        .order_by(Task.created_at.desc())
    )
    rows = session.exec(stmt).all()
    return [_serialize_variant_task(r) for r in rows]


def _serialize_variant_task(task: Task) -> dict:
    return {
        "id": task.id,
        "title": task.title,
        "status": task.status,
        "class_group_id": task.class_group_id,
        "base_task_id": task.base_task_id,
        "subject": task.subject,
        "grade": task.grade,
        "topic": task.topic,
        "lesson_type": task.lesson_type,
        "class_hour": task.class_hour,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
    }
