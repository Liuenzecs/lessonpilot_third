from __future__ import annotations

from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlmodel import Session, select

from app.models import Document, DocumentSnapshot, Task
from app.models.base import utcnow
from app.schemas.content import ContentDocument, SectionBlock
from app.schemas.task import TaskCreatePayload, TaskUpdatePayload

DEFAULT_SECTION_TITLES = [
    "教学目标",
    "教学重难点",
    "导入环节",
    "新授环节",
    "练习巩固",
    "课堂小结",
]


def _build_empty_document() -> ContentDocument:
    return ContentDocument(
        version=1,
        blocks=[
            SectionBlock(
                id=str(uuid4()),
                title=title,
                status="confirmed",
                source="human",
                children=[],
            )
            for title in DEFAULT_SECTION_TITLES
        ],
    )


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
    )
    session.add(task)
    session.flush()

    content = _build_empty_document()
    document = Document(
        task_id=task.id,
        user_id=user_id,
        title=task.title,
        content=content.model_dump(mode="json", by_alias=True),
        version=content.version,
    )
    session.add(document)
    session.commit()
    session.refresh(task)
    return task


def duplicate_task(session: Session, source_task: Task, source_document: Document) -> Task:
    duplicated_task = Task(
        user_id=source_task.user_id,
        title=f"{source_task.title}（副本）",
        subject=source_task.subject,
        grade=source_task.grade,
        topic=source_task.topic,
        requirements=source_task.requirements,
        status="draft",
    )
    session.add(duplicated_task)
    session.flush()

    duplicated_content = ContentDocument.model_validate(source_document.content)
    duplicated_content.version = 1
    duplicated_document = Document(
        task_id=duplicated_task.id,
        user_id=source_task.user_id,
        title=duplicated_task.title,
        content=duplicated_content.model_dump(mode="json", by_alias=True),
        version=1,
    )
    session.add(duplicated_document)
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
    document = session.exec(select(Document).where(Document.task_id == task.id)).first()
    if document is not None:
        snapshots = session.exec(
            select(DocumentSnapshot).where(DocumentSnapshot.document_id == document.id)
        ).all()
        for snapshot in snapshots:
            session.delete(snapshot)
        session.delete(document)
    session.delete(task)
    if commit:
        session.commit()
