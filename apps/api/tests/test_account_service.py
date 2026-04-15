"""单元测试：services/account_service.py"""

from __future__ import annotations

import json

import pytest
from fastapi import HTTPException
from sqlmodel import Session, SQLModel, create_engine

from app.models import Task, User
from app.schemas.account import (
    AccountChangePasswordPayload,
    AccountDeletePayload,
    AccountUpdatePayload,
    FeedbackCreatePayload,
)
from app.services import account_service


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        yield s
    engine.dispose()


def _make_user(session: Session, email: str = "test@example.com") -> User:
    from app.core.security import hash_password
    user = User(email=email, name="Test User", password_hash=hash_password("Password123"))
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


# --- serialize_account ---


def test_serialize_account():
    assert callable(account_service.serialize_account)


# --- update_account_profile ---


def test_update_account_profile_changes_name(session):
    user = _make_user(session)
    updated, token = account_service.update_account_profile(
        session, user, AccountUpdatePayload(name="New Name"),
    )
    assert updated.name == "New Name"
    assert token is None  # email 未变


def test_update_account_profile_re_verifies_on_email_change(session):
    user = _make_user(session)
    user.email_verified = True
    session.add(user)
    session.commit()

    updated, token = account_service.update_account_profile(
        session, user, AccountUpdatePayload(email="new@example.com"),
    )
    assert updated.email == "new@example.com"
    assert updated.email_verified is False
    assert token is not None  # 发了新的验证 token


def test_update_account_profile_rejects_duplicate_email(session):
    _make_user(session, "existing@example.com")
    user2 = _make_user(session, "other@example.com")
    with pytest.raises(HTTPException) as exc_info:
        account_service.update_account_profile(
            session, user2, AccountUpdatePayload(email="existing@example.com"),
        )
    assert exc_info.value.status_code == 409


# --- change_account_password ---


def test_change_account_password_success(session):
    user = _make_user(session)
    account_service.change_account_password(
        session, user, AccountChangePasswordPayload(
            current_password="Password123",
            new_password="NewPassword456",
            confirm_password="NewPassword456",
        ),
    )
    from app.core.security import verify_password
    assert verify_password("NewPassword456", user.password_hash)


def test_change_account_password_rejects_wrong_current(session):
    user = _make_user(session)
    with pytest.raises(HTTPException) as exc_info:
        account_service.change_account_password(
            session, user, AccountChangePasswordPayload(
                current_password="WrongPassword1",
                new_password="NewPassword456",
                confirm_password="NewPassword456",
            ),
        )
    assert exc_info.value.status_code == 401


def test_change_account_password_rejects_same_password(session):
    user = _make_user(session)
    with pytest.raises(HTTPException) as exc_info:
        account_service.change_account_password(
            session, user, AccountChangePasswordPayload(
                current_password="Password123",
                new_password="Password123",
                confirm_password="Password123",
            ),
        )
    assert exc_info.value.status_code == 400


# --- create_feedback ---


def test_create_feedback(session):
    user = _make_user(session)
    feedback = account_service.create_feedback(
        session, user, FeedbackCreatePayload(
            mood="happy", message="Great app!", page_path="/editor",
        ),
    )
    assert feedback.user_id == user.id
    assert feedback.mood == "happy"
    assert feedback.message == "Great app!"


# --- export_account_data ---


def test_export_account_data_returns_json(session):
    user = _make_user(session)
    data = account_service.export_account_data(session, user)
    parsed = json.loads(data)
    assert "user" in parsed
    assert "tasks" in parsed
    assert "documents" in parsed
    assert parsed["user"]["email"] == "test@example.com"


def test_export_account_data_includes_tasks(session):
    user = _make_user(session)
    task = Task(user_id=user.id, title="Test Task", subject="语文", grade="七年级", topic="春")
    session.add(task)
    session.commit()
    data = account_service.export_account_data(session, user)
    parsed = json.loads(data)
    assert len(parsed["tasks"]) == 1
    assert parsed["tasks"][0]["title"] == "Test Task"


# --- delete_account ---


def test_delete_account_removes_user_and_data(session):
    user = _make_user(session)
    task = Task(user_id=user.id, title="Test", subject="语文", grade="七年级", topic="春")
    session.add(task)
    session.commit()
    task_id = task.id

    account_service.delete_account(
        session, user, AccountDeletePayload(confirm_text="DELETE"),
    )
    assert session.get(User, user.id) is None
    assert session.get(Task, task_id) is None


def test_delete_account_rejects_wrong_confirm():
    """AccountDeletePayload 的 model_validator 会在 schema 层拦截非 DELETE。"""
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        AccountDeletePayload(confirm_text="WRONG")
