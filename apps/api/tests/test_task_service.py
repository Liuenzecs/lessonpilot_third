"""单元测试：services/task_service.py"""

from __future__ import annotations

import pytest
from fastapi import HTTPException
from sqlmodel import Session, SQLModel, create_engine, select

from app.models import Document, Task, User
from app.schemas.task import TaskCreatePayload, TaskUpdatePayload
from app.services import task_service


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


def _default_payload(**overrides) -> TaskCreatePayload:
    defaults = {
        "subject": "语文",
        "grade": "七年级",
        "topic": "春",
        "lesson_type": "lesson_plan",
        "scene": "public_school",
        "class_hour": 1,
        "lesson_category": "new",
    }
    defaults.update(overrides)
    return TaskCreatePayload(**defaults)


# --- create_task ---


def test_create_task_with_lesson_plan_creates_one_document(session, monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "fake")
    user = _make_user(session)
    task = task_service.create_task(session, user.id, _default_payload())
    assert task.title == "春"
    assert task.user_id == user.id
    docs = session.exec(select(Document).where(Document.task_id == task.id)).all()
    assert len(docs) == 1
    assert docs[0].doc_type == "lesson_plan"


def test_create_task_with_study_guide_creates_one_document(session, monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "fake")
    user = _make_user(session)
    task = task_service.create_task(session, user.id, _default_payload(lesson_type="study_guide"))
    docs = session.exec(select(Document).where(Document.task_id == task.id)).all()
    assert len(docs) == 1
    assert docs[0].doc_type == "study_guide"


def test_create_task_with_both_creates_two_documents(session, monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "fake")
    user = _make_user(session)
    task = task_service.create_task(session, user.id, _default_payload(lesson_type="both"))
    docs = session.exec(select(Document).where(Document.task_id == task.id)).all()
    assert len(docs) == 2
    doc_types = {d.doc_type for d in docs}
    assert doc_types == {"lesson_plan", "study_guide"}


def test_create_task_stores_new_fields(session, monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "fake")
    user = _make_user(session)
    task = task_service.create_task(session, user.id, _default_payload(
        scene="tutor",
        class_hour=2,
        lesson_category="review",
    ))
    assert task.scene == "tutor"
    assert task.class_hour == 2
    assert task.lesson_category == "review"


# --- list_tasks ---


def test_list_tasks_pagination(session, monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "fake")
    user = _make_user(session)
    for i in range(5):
        task_service.create_task(session, user.id, _default_payload(topic=f"课题{i}"))
    tasks, total = task_service.list_tasks(session, user.id, page=1, page_size=3)
    assert total == 5
    assert len(tasks) == 3


# --- get_owned_task ---


def test_get_owned_task_raises_for_wrong_user(session, monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "fake")
    user = _make_user(session)
    task = task_service.create_task(session, user.id, _default_payload())
    other_user = User(email="other@example.com", name="Other", password_hash="hash")
    session.add(other_user)
    session.commit()
    with pytest.raises(HTTPException) as exc_info:
        task_service.get_owned_task(session, task.id, other_user.id)
    assert exc_info.value.status_code == 404


# --- duplicate_task ---


def test_duplicate_task_copies_documents(session, monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "fake")
    user = _make_user(session)
    task = task_service.create_task(session, user.id, _default_payload(lesson_type="both"))
    duplicated = task_service.duplicate_task(session, task)
    assert duplicated.title.endswith("（副本）")
    dup_docs = session.exec(select(Document).where(Document.task_id == duplicated.id)).all()
    assert len(dup_docs) == 2


# --- update_task ---


def test_update_task_changes_title(session, monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "fake")
    user = _make_user(session)
    task = task_service.create_task(session, user.id, _default_payload())
    updated = task_service.update_task(session, task, TaskUpdatePayload(title="新标题"))
    assert updated.title == "新标题"


# --- delete_task ---


def test_delete_task_cascades(session, monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "fake")
    user = _make_user(session)
    task = task_service.create_task(session, user.id, _default_payload())
    task_id = task.id
    doc = session.exec(select(Document).where(Document.task_id == task_id)).first()
    assert doc is not None

    task_service.delete_task(session, task)
    assert session.get(Task, task_id) is None
    remaining_docs = session.exec(select(Document).where(Document.task_id == task_id)).all()
    assert len(remaining_docs) == 0
