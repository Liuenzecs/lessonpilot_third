"""单元测试：services/auth_service.py"""

from __future__ import annotations

import pytest
from fastapi import HTTPException
from sqlmodel import Session, SQLModel, create_engine, select

from app.core.security import verify_password
from app.models import AuthToken, User
from app.schemas.auth import LoginPayload, RegisterPayload, ResetPasswordPayload
from app.services.auth_service import (
    authenticate_user,
    issue_verification_token,
    register_user,
    request_password_reset,
    reset_password_with_token,
    validate_password_strength,
    verify_email_token,
)


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        yield s
    engine.dispose()


def _make_user(session: Session, email: str = "test@example.com") -> User:
    user = User(email=email, name="Test", password_hash="hash")
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


# --- validate_password_strength ---


def test_validate_password_strength_rejects_short():
    with pytest.raises(HTTPException) as exc_info:
        validate_password_strength("Ab1")
    assert exc_info.value.status_code == 400


def test_validate_password_strength_rejects_no_digit():
    with pytest.raises(HTTPException) as exc_info:
        validate_password_strength("abcdefgh")
    assert exc_info.value.status_code == 400


def test_validate_password_strength_rejects_no_letter():
    with pytest.raises(HTTPException) as exc_info:
        validate_password_strength("12345678")
    assert exc_info.value.status_code == 400


def test_validate_password_strength_accepts_strong():
    validate_password_strength("Password123")  # should not raise


# --- register_user ---


def test_register_user_creates_user(session, monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "fake")
    user = register_user(session, RegisterPayload(
        email="new@example.com", name="New User", password="Password123",
    ))
    assert user.email == "new@example.com"
    assert user.name == "New User"
    assert user.password_hash != "Password123"
    assert verify_password("Password123", user.password_hash)


def test_register_user_rejects_duplicate_email(session, monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "fake")
    register_user(session, RegisterPayload(
        email="dup@example.com", name="First", password="Password123",
    ))
    with pytest.raises(HTTPException) as exc_info:
        register_user(session, RegisterPayload(
            email="dup@example.com", name="Second", password="Password123",
        ))
    assert exc_info.value.status_code == 409


# --- authenticate_user ---


def test_authenticate_user_succeeds(session, monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "fake")
    register_user(session, RegisterPayload(
        email="auth@example.com", name="Auth", password="Password123",
    ))
    user = authenticate_user(session, LoginPayload(
        email="auth@example.com", password="Password123",
    ))
    assert user.email == "auth@example.com"


def test_authenticate_user_rejects_wrong_password(session, monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "fake")
    register_user(session, RegisterPayload(
        email="auth2@example.com", name="Auth2", password="Password123",
    ))
    with pytest.raises(HTTPException) as exc_info:
        authenticate_user(session, LoginPayload(
            email="auth2@example.com", password="WrongPass1",
        ))
    assert exc_info.value.status_code == 401


# --- issue_verification_token ---


def test_issue_verification_token_creates_token(session, monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "fake")
    user = _make_user(session, "verify@example.com")
    token = issue_verification_token(session, user)
    assert token is not None
    assert isinstance(token, str)
    # 数据库应有对应 AuthToken
    db_token = session.exec(select(AuthToken).where(AuthToken.user_id == user.id)).first()
    assert db_token is not None
    assert db_token.token_type == "verify_email"


def test_issue_verification_token_returns_none_if_verified(session):
    user = _make_user(session, "verified@example.com")
    user.email_verified = True
    session.add(user)
    session.commit()
    result = issue_verification_token(session, user)
    assert result is None


# --- verify_email_token ---


def test_verify_email_token_marks_verified(session, monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "fake")
    user = _make_user(session, "verify2@example.com")
    raw_token = issue_verification_token(session, user)
    updated_user = verify_email_token(session, raw_token)
    assert updated_user.email_verified is True
    assert updated_user.email_verified_at is not None


# --- request_password_reset ---


def test_request_password_reset_returns_token(session, monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "fake")
    register_user(session, RegisterPayload(
        email="reset@example.com", name="Reset", password="Password123",
    ))
    user, token = request_password_reset(session, "reset@example.com")
    assert user is not None
    assert token is not None


def test_request_password_reset_returns_none_for_unknown_email(session):
    user, token = request_password_reset(session, "nonexistent@example.com")
    assert user is None
    assert token is None


# --- reset_password_with_token ---


def test_reset_password_with_token_changes_password(session, monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "fake")
    register_user(session, RegisterPayload(
        email="reset2@example.com", name="Reset2", password="OldPassword1",
    ))
    _, raw_token = request_password_reset(session, "reset2@example.com")
    reset_password_with_token(session, ResetPasswordPayload(
        token=raw_token, password="NewPassword1", confirm_password="NewPassword1",
    ))
    # 新密码能登录
    user = authenticate_user(session, LoginPayload(
        email="reset2@example.com", password="NewPassword1",
    ))
    assert user is not None


def test_reset_password_rejects_reused_token(session, monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "fake")
    register_user(session, RegisterPayload(
        email="reset3@example.com", name="Reset3", password="OldPassword1",
    ))
    _, raw_token = request_password_reset(session, "reset3@example.com")
    reset_password_with_token(session, ResetPasswordPayload(
        token=raw_token, password="NewPassword1", confirm_password="NewPassword1",
    ))
    with pytest.raises(HTTPException):
        reset_password_with_token(session, ResetPasswordPayload(
            token=raw_token, password="AnotherPass1", confirm_password="AnotherPass1",
        ))
