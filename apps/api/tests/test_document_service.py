"""单元测试：services/document_service.py"""

from __future__ import annotations

import pytest
from fastapi import HTTPException
from sqlmodel import Session, SQLModel, create_engine, select

from app.models import Document, DocumentSnapshot, Task, User
from app.schemas.content import (
    LessonPlanContent,
    StudyGuideContent,
    create_empty_lesson_plan,
    create_empty_study_guide,
)
from app.schemas.document import DocumentUpdatePayload
from app.services import document_service


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        yield s
    engine.dispose()


def _make_user(session: Session) -> User:
    user = User(email="teacher@example.com", name="Teacher", password_hash="hash")
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def _make_task(session: Session, user_id: str) -> Task:
    task = Task(
        user_id=user_id,
        title="《春》教案",
        subject="语文",
        grade="七年级",
        topic="春",
        scene="public_school",
        lesson_type="lesson_plan",
        class_hour=1,
        lesson_category="new",
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def _make_document(session: Session, task_id: str, user_id: str, doc_type: str = "lesson_plan") -> Document:
    if doc_type == "lesson_plan":
        content = create_empty_lesson_plan(subject="语文", grade="七年级", topic="春")
    else:
        content = create_empty_study_guide(subject="语文", grade="七年级", topic="春")
    doc = Document(
        task_id=task_id,
        user_id=user_id,
        doc_type=doc_type,
        title="《春》教案",
        content=content.model_dump(by_alias=True),
    )
    session.add(doc)
    session.commit()
    session.refresh(doc)
    return doc


# --- load_content ---


def test_load_content_lesson_plan(session):
    user = _make_user(session)
    task = _make_task(session, user.id)
    doc = _make_document(session, task.id, user.id, "lesson_plan")
    content = document_service.load_content(doc)
    assert isinstance(content, LessonPlanContent)
    assert content.doc_type == "lesson_plan"


def test_load_content_study_guide(session):
    user = _make_user(session)
    task = _make_task(session, user.id)
    doc = _make_document(session, task.id, user.id, "study_guide")
    content = document_service.load_content(doc)
    assert isinstance(content, StudyGuideContent)
    assert content.doc_type == "study_guide"


# --- get_owned_document ---


def test_get_owned_document_raises_for_wrong_user(session):
    user = _make_user(session)
    task = _make_task(session, user.id)
    doc = _make_document(session, task.id, user.id)
    with pytest.raises(HTTPException) as exc_info:
        document_service.get_owned_document(session, doc.id, "wrong-user-id")
    assert exc_info.value.status_code == 404


# --- save_document ---


def test_save_document_bumps_version(session):
    user = _make_user(session)
    task = _make_task(session, user.id)
    doc = _make_document(session, task.id, user.id)
    assert doc.version == 1

    content = document_service.load_content(doc)
    content.objectives_status = "confirmed"
    updated = document_service.save_document(session, doc, content, snapshot_source="save")

    assert updated.version == 2


def test_save_document_creates_snapshot(session):
    user = _make_user(session)
    task = _make_task(session, user.id)
    doc = _make_document(session, task.id, user.id)

    content = document_service.load_content(doc)
    document_service.save_document(session, doc, content, snapshot_source="save")

    snapshots = session.exec(
        select(DocumentSnapshot).where(DocumentSnapshot.document_id == doc.id)
    ).all()
    assert len(snapshots) == 1
    assert snapshots[0].source == "save"


def test_save_document_without_snapshot(session):
    user = _make_user(session)
    task = _make_task(session, user.id)
    doc = _make_document(session, task.id, user.id)

    content = document_service.load_content(doc)
    document_service.save_document(session, doc, content)

    snapshots = session.exec(
        select(DocumentSnapshot).where(DocumentSnapshot.document_id == doc.id)
    ).all()
    assert len(snapshots) == 0


# --- update_document (conflict) ---


def test_update_document_conflict_detection(session):
    user = _make_user(session)
    task = _make_task(session, user.id)
    doc = _make_document(session, task.id, user.id)

    content = document_service.load_content(doc)
    wrong_version = doc.version + 999
    with pytest.raises(HTTPException) as exc_info:
        document_service.update_document(
            session, doc, DocumentUpdatePayload(version=wrong_version, content=content),
        )
    assert exc_info.value.status_code == 409


# --- restore_document_snapshot ---


def test_restore_snapshot_increments_version(session):
    user = _make_user(session)
    task = _make_task(session, user.id)
    doc = _make_document(session, task.id, user.id)
    original_version = doc.version

    content = document_service.load_content(doc)
    content.objectives_status = "confirmed"
    doc = document_service.save_document(session, doc, content, snapshot_source="save")
    assert doc.version == original_version + 1

    snapshots = document_service.list_document_history(session, doc)
    assert len(snapshots) == 1

    restored = document_service.restore_document_snapshot(session, doc, snapshots[0])
    assert restored.version == original_version + 2


# --- list_document_history trimming ---


def test_history_trims_to_limit(session):
    user = _make_user(session)
    task = _make_task(session, user.id)
    doc = _make_document(session, task.id, user.id)

    for i in range(15):
        content = document_service.load_content(doc)
        content.board_design = f"版本 {i}"
        doc = document_service.save_document(session, doc, content, snapshot_source="save")

    snapshots = document_service.list_document_history(session, doc)
    assert len(snapshots) <= 10  # SNAPSHOT_LIMIT


# --- serialize_document ---


def test_serialize_document(session):
    user = _make_user(session)
    task = _make_task(session, user.id)
    doc = _make_document(session, task.id, user.id)
    serialized = document_service.serialize_document(doc)
    assert serialized.id == doc.id
    assert serialized.doc_type == "lesson_plan"
    assert serialized.content is not None
