from __future__ import annotations

import hashlib
import secrets
from datetime import UTC, timedelta
from typing import Literal

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.core.config import get_settings
from app.core.security import hash_password, verify_password
from app.models import AuthToken, User
from app.models.base import utcnow
from app.schemas.auth import LoginPayload, RegisterPayload, ResetPasswordPayload

AuthTokenType = Literal["verify_email", "reset_password"]


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def validate_password_strength(password: str) -> None:
    has_letter = any(char.isalpha() for char in password)
    has_digit = any(char.isdigit() for char in password)
    if len(password) < 8 or not has_letter or not has_digit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters and contain letters and numbers",
        )


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _resolve_expiry(token_type: AuthTokenType):
    settings = get_settings()
    if token_type == "verify_email":
        return utcnow() + timedelta(hours=settings.verify_email_token_expire_hours)
    return utcnow() + timedelta(minutes=settings.reset_password_token_expire_minutes)


def _issue_token(session: Session, user_id: str, token_type: AuthTokenType) -> str:
    existing_tokens = session.exec(
        select(AuthToken).where(AuthToken.user_id == user_id, AuthToken.token_type == token_type)
    ).all()
    for existing_token in existing_tokens:
        session.delete(existing_token)

    raw_token = secrets.token_urlsafe(32)
    auth_token = AuthToken(
        user_id=user_id,
        token_hash=_hash_token(raw_token),
        token_type=token_type,
        expires_at=_resolve_expiry(token_type),
    )
    session.add(auth_token)
    session.commit()
    return raw_token


def _consume_token(session: Session, raw_token: str, token_type: AuthTokenType) -> AuthToken:
    token = session.exec(
        select(AuthToken).where(
            AuthToken.token_hash == _hash_token(raw_token),
            AuthToken.token_type == token_type,
        )
    ).first()
    if token is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")

    expires_at = token.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)

    if token.used_at is not None or expires_at <= utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")
    return token


def issue_verification_token(session: Session, user: User) -> str | None:
    if user.email_verified:
        return None
    return _issue_token(session, user.id, "verify_email")


def issue_reset_password_token(session: Session, user: User) -> str:
    return _issue_token(session, user.id, "reset_password")


def register_user(session: Session, payload: RegisterPayload) -> User:
    normalized_email = _normalize_email(payload.email)
    validate_password_strength(payload.password)
    existing_user = session.exec(select(User).where(User.email == normalized_email)).first()
    if existing_user is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        email=normalized_email,
        name=payload.name.strip(),
        password_hash=hash_password(payload.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def authenticate_user(session: Session, payload: LoginPayload) -> User:
    user = session.exec(select(User).where(User.email == _normalize_email(payload.email))).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return user


def verify_email_token(session: Session, raw_token: str) -> User:
    token = _consume_token(session, raw_token, "verify_email")
    user = session.get(User, token.user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.email_verified = True
    user.email_verified_at = utcnow()
    token.used_at = utcnow()
    session.add(user)
    session.add(token)
    session.commit()
    session.refresh(user)
    return user


def request_password_reset(session: Session, email: str) -> tuple[User | None, str | None]:
    user = session.exec(select(User).where(User.email == _normalize_email(email))).first()
    if user is None:
        return None, None
    return user, issue_reset_password_token(session, user)


def reset_password_with_token(session: Session, payload: ResetPasswordPayload) -> None:
    validate_password_strength(payload.password)
    token = _consume_token(session, payload.token, "reset_password")
    user = session.get(User, token.user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.password_hash = hash_password(payload.password)
    token.used_at = utcnow()
    session.add(user)
    session.add(token)
    session.commit()
