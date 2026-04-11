from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, Response, status
from sqlmodel import Session

from app.core.db import get_session
from app.core.security import create_access_token, get_current_user
from app.models import User
from app.schemas.auth import (
    AuthResponse,
    ForgotPasswordPayload,
    LoginPayload,
    MessageResponse,
    RegisterPayload,
    ResetPasswordPayload,
    UserRead,
    VerifyEmailPayload,
)
from app.services.auth_service import (
    authenticate_user,
    issue_verification_token,
    register_user,
    request_password_reset,
    reset_password_with_token,
    verify_email_token,
)
from app.services.mail_service import send_password_reset_email, send_verification_email

router = APIRouter(prefix="/auth", tags=["auth"])


def _to_user_read(user: User) -> UserRead:
    return UserRead(
        id=user.id,
        email=user.email,
        name=user.name,
        email_verified=user.email_verified,
        email_verified_at=user.email_verified_at,
        created_at=user.created_at,
    )


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterPayload,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
) -> AuthResponse:
    user = register_user(session, payload)
    verification_token = issue_verification_token(session, user)
    if verification_token:
        background_tasks.add_task(send_verification_email, user.email, user.name, verification_token)
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


@router.post("/forgot-password", response_model=MessageResponse, status_code=status.HTTP_202_ACCEPTED)
def forgot_password(
    payload: ForgotPasswordPayload,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
) -> MessageResponse:
    user, reset_token = request_password_reset(session, payload.email)
    if user is not None and reset_token is not None:
        background_tasks.add_task(send_password_reset_email, user.email, user.name, reset_token)
    return MessageResponse(message="如果该邮箱已注册，我们会发送重置链接。")


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(
    payload: ResetPasswordPayload,
    session: Session = Depends(get_session),
) -> MessageResponse:
    reset_password_with_token(session, payload)
    return MessageResponse(message="密码已重置，请使用新密码登录。")


@router.post("/resend-verification", response_model=MessageResponse, status_code=status.HTTP_202_ACCEPTED)
def resend_verification(
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    verification_token = issue_verification_token(session, current_user)
    if verification_token:
        background_tasks.add_task(send_verification_email, current_user.email, current_user.name, verification_token)
        return MessageResponse(message="验证邮件已重新发送。")
    return MessageResponse(message="当前邮箱已验证，无需重复发送。")


@router.post("/verify-email", response_model=UserRead)
def verify_email(
    payload: VerifyEmailPayload,
    session: Session = Depends(get_session),
) -> UserRead:
    return _to_user_read(verify_email_token(session, payload.token))
