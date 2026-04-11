from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status
from sqlmodel import Session

from app.core.db import get_session
from app.core.security import create_access_token, get_current_user
from app.models import User
from app.schemas.auth import AuthResponse, LoginPayload, RegisterPayload, UserRead
from app.services.auth_service import authenticate_user, register_user

router = APIRouter(prefix="/auth", tags=["auth"])


def _to_user_read(user: User) -> UserRead:
    return UserRead(id=user.id, email=user.email, name=user.name, created_at=user.created_at)


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterPayload,
    session: Session = Depends(get_session),
) -> AuthResponse:
    user = register_user(session, payload)
    return AuthResponse(access_token=create_access_token(user.id), user=_to_user_read(user))


@router.post("/login", response_model=AuthResponse)
def login(
    payload: LoginPayload,
    session: Session = Depends(get_session),
) -> AuthResponse:
    user = authenticate_user(session, payload)
    return AuthResponse(access_token=create_access_token(user.id), user=_to_user_read(user))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(current_user: User = Depends(get_current_user)) -> Response:
    _ = current_user
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)) -> UserRead:
    return _to_user_read(current_user)
