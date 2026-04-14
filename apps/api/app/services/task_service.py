from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlmodel import Session, select

from app.models import Document, DocumentSnapshot, Task
from app.models.base import utcnow
from app.schemas.content import (
    create_empty_lesson_plan,
    create_empty_study_guide,
)
from app.schemas.task import TaskCreatePayload, TaskUpdatePayload


def list_tasks(session: Session, user_id: str, page: int, page_size: int) -> tuple[list[Task], int]:
    total = session.exec(select(func.count()).select_from(Task).where(Task.user_id == user_id)).one()
    tasks = session.exec(
        select(Task)
        .where(Task.user_id == user_id)
        .order_by(Task.updated_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return tasks, int(total)


def get_owned_task(session: Session, task_id: str, user_id: str) -> Task:
    task = session.exec(select(Task).where(Task.id == task_id, Task.user_id == user_id)).first()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


def create_task(session: Session, user_id: str, payload: TaskCreatePayload) -> Task:
    task = Task(
        user_id=user_id,
        title=(payload.title or payload.topic).strip(),
        subject=payload.subject.strip(),
        grade=payload.grade.strip(),
        topic=payload.topic.strip(),
        requirements=payload.requirements.strip() if payload.requirements else None,
        status="draft",
        scene=payload.scene,
        lesson_type=payload.lesson_type,
        class_hour=payload.class_hour,
        lesson_category=payload.lesson_category,
    )
    session.add(task)
    session.flush()

    # 根据 lesson_type 创建对应的 document(s)
    doc_types: list[str] = []
    if payload.lesson_type in ("lesson_plan", "both"):
        doc_types.append("lesson_plan")
    if payload.lesson_type in ("study_guide", "both"):
        doc_types.append("study_guide")

    for doc_type in doc_types:
        if doc_type == "lesson_plan":
            content = create_empty_lesson_plan(
                subject=task.subject,
                grade=task.grade,
                topic=task.topic,
                class_hour=task.class_hour,
                lesson_category=task.lesson_category,
            )
        else:
            content = create_empty_study_guide(
                subject=task.subject,
                grade=task.grade,
                topic=task.topic,
            )
        document = Document(
            task_id=task.id,
            user_id=user_id,
            doc_type=doc_type,
            title=task.title,
            content=content.model_dump(by_alias=True),
        )
        session.add(document)

    session.commit()
    session.refresh(task)
    return task


def duplicate_task(session: Session, source_task: Task) -> Task:
    """复制 task 及其所有关联 documents。"""
    duplicated_task = Task(
        user_id=source_task.user_id,
        title=f"{source_task.title}（副本）",
        subject=source_task.subject,
        grade=source_task.grade,
        topic=source_task.topic,
        requirements=source_task.requirements,
        status="draft",
        scene=source_task.scene,
        lesson_type=source_task.lesson_type,
        class_hour=source_task.class_hour,
        lesson_category=source_task.lesson_category,
    )
    session.add(duplicated_task)
    session.flush()

    # 复制所有关联 documents
    source_docs = session.exec(
        select(Document).where(Document.task_id == source_task.id)
    ).all()
    for source_doc in source_docs:
        dup_doc = Document(
            task_id=duplicated_task.id,
            user_id=source_task.user_id,
            doc_type=source_doc.doc_type,
            title=duplicated_task.title,
            content=source_doc.content,  # JSON 直接复制
        )
        session.add(dup_doc)

    session.commit()
    session.refresh(duplicated_task)
    return duplicated_task


def update_task(session: Session, task: Task, payload: TaskUpdatePayload) -> Task:
    changed = False
    if payload.title is not None:
        task.title = payload.title.strip()
        changed = True
    if payload.requirements is not None:
        task.requirements = payload.requirements.strip() if payload.requirements else None
        changed = True
    if payload.status is not None:
        task.status = payload.status
        changed = True
    if changed:
        task.updated_at = utcnow()
        session.add(task)
        session.commit()
        session.refresh(task)
    return task


def delete_task(session: Session, task: Task, *, commit: bool = True) -> None:
    # 删除所有关联 documents 的 snapshots
    docs = session.exec(
        select(Document).where(Document.task_id == task.id)
    ).all()
    for doc in docs:
        snapshots = session.exec(
            select(DocumentSnapshot).where(DocumentSnapshot.document_id == doc.id)
        ).all()
        for snapshot in snapshots:
            session.delete(snapshot)
        session.delete(doc)
    session.delete(task)
    if commit:
        session.commit()
