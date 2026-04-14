from __future__ import annotations

import pytest
from pydantic import ValidationError
from sqlmodel import Session, select

from app.core.config import get_settings
from app.core.db import get_engine
from app.main import create_app
from app.models import AuthToken, User
from app.services.auth_service import issue_reset_password_token, issue_verification_token


def test_register_login_me_and_logout(client):
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "teacher@example.com",
            "name": "Teacher",
            "password": "Password123",
        },
    )
    assert register_response.status_code == 201
    register_body = register_response.json()
    assert register_body["user"]["email"] == "teacher@example.com"
    assert register_body["user"]["email_verified"] is False
    token = register_body["access_token"]

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "teacher@example.com", "password": "Password123"},
    )
    assert login_response.status_code == 200

    headers = {"Authorization": f"Bearer {token}"}
    me_response = client.get("/api/v1/auth/me", headers=headers)
    assert me_response.status_code == 200
    assert me_response.json()["name"] == "Teacher"
    assert me_response.json()["email_verified"] is False

    logout_response = client.post("/api/v1/auth/logout", headers=headers)
    assert logout_response.status_code == 204


def test_duplicate_register_rejected(client):
    payload = {
        "email": "teacher@example.com",
        "name": "Teacher",
        "password": "Password123",
    }
    assert client.post("/api/v1/auth/register", json=payload).status_code == 201
    duplicate_response = client.post("/api/v1/auth/register", json=payload)
    assert duplicate_response.status_code == 409


def test_email_verification_flow(client, auth_headers):
    resend_response = client.post("/api/v1/auth/resend-verification", headers=auth_headers)
    assert resend_response.status_code == 202

    with Session(get_engine()) as session:
        user = session.exec(select(User).where(User.email == "teacher@example.com")).one()
        token = issue_verification_token(session, user)

    verify_response = client.post("/api/v1/auth/verify-email", json={"token": token})
    assert verify_response.status_code == 200
    assert verify_response.json()["email_verified"] is True

    second_verify_response = client.post("/api/v1/auth/verify-email", json={"token": token})
    assert second_verify_response.status_code == 400


def test_forgot_and_reset_password_flow(client):
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "teacher@example.com",
            "name": "Teacher",
            "password": "Password123",
        },
    )
    assert register_response.status_code == 201

    forgot_response = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "teacher@example.com"},
    )
    assert forgot_response.status_code == 202

    with Session(get_engine()) as session:
        user = session.exec(select(User).where(User.email == "teacher@example.com")).one()
        token = issue_reset_password_token(session, user)
        auth_tokens = session.exec(
            select(AuthToken).where(AuthToken.user_id == user.id, AuthToken.token_type == "reset_password")
        ).all()
        assert len(auth_tokens) == 1

    reset_response = client.post(
        "/api/v1/auth/reset-password",
        json={
            "token": token,
            "password": "NewPassword123",
            "confirm_password": "NewPassword123",
        },
    )
    assert reset_response.status_code == 200

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "teacher@example.com", "password": "NewPassword123"},
    )
    assert login_response.status_code == 200


def test_production_requires_strong_jwt_secret(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("JWT_SECRET", "replace-with-a-long-random-secret")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///phase7-production-secret.db")
    get_settings.cache_clear()

    with pytest.raises(ValidationError, match="JWT_SECRET must be replaced"):
        create_app()

    get_settings.cache_clear()
