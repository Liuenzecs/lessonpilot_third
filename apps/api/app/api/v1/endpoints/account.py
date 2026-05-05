from __future__ import annotations

from urllib.parse import quote

from fastapi import APIRouter, BackgroundTasks, Body, Depends, Response, status
from fastapi.responses import Response as FastAPIResponse
from sqlmodel import Session

from app.core.db import get_session
from app.core.security import get_current_user
from app.models import User
from app.schemas.account import (
    AccountChangePasswordPayload,
    AccountDeletePayload,
    AccountRead,
    AccountUpdatePayload,
    FeedbackCreatePayload,
    FeedbackRead,
)
from app.schemas.usage import UserUsageResponse
from app.services.cost_tracker import (
    get_user_cost_this_month,
    get_user_usage_this_month,
    get_user_usage_today,
)
from app.services.quota_service import get_user_quota_summary
from app.schemas.auth import MessageResponse
from app.services.account_service import (
    change_account_password,
    create_feedback,
    delete_account,
    export_account_data,
    serialize_account,
    serialize_feedback,
    update_account_profile,
)
from app.services.mail_service import (
    send_feedback_notification,
    send_verification_email,
)

router = APIRouter(prefix="/account", tags=["account"])


@router.get("", response_model=AccountRead)
def get_account(current_user: User = Depends(get_current_user)) -> AccountRead:
    return serialize_account(current_user)


@router.patch("", response_model=AccountRead)
def patch_account(
    payload: AccountUpdatePayload,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> AccountRead:
    user, verification_token = update_account_profile(session, current_user, payload)
    if verification_token:
        background_tasks.add_task(send_verification_email, user.email, user.name, verification_token, user_id=user.id)
    return serialize_account(user)


@router.post("/change-password", response_model=MessageResponse)
def change_password(
    payload: AccountChangePasswordPayload,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    change_account_password(session, current_user, payload)
    return MessageResponse(message="密码修改成功。")


@router.post("/export")
def export_account(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> FastAPIResponse:
    payload = export_account_data(session, current_user)
    filename = quote(f"lessonpilot-account-{current_user.id}.json")
    return FastAPIResponse(
        content=payload,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"},
    )


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def remove_account(
    payload: AccountDeletePayload = Body(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Response:
    delete_account(session, current_user, payload)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/feedback", response_model=FeedbackRead, status_code=status.HTTP_201_CREATED)
def post_feedback(
    payload: FeedbackCreatePayload,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> FeedbackRead:
    feedback = create_feedback(session, current_user, payload)
    background_tasks.add_task(
        send_feedback_notification,
        user_id=current_user.id,
        user_name=current_user.name,
        user_email=current_user.email,
        mood=payload.mood,
        message=payload.message,
        page_path=payload.page_path,
    )
    return serialize_feedback(feedback)


@router.get("/usage", response_model=UserUsageResponse)
def get_usage(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> UserUsageResponse:
    summary = get_user_quota_summary(session=session, user_id=current_user.id)
    cost_month = get_user_cost_this_month(session=session, user_id=current_user.id)
    return UserUsageResponse(
        generations_today=summary["generations_today"],
        generations_this_month=summary["generations_this_month"],
        daily_limit=summary["daily_limit"],
        monthly_limit=summary["monthly_limit"],
        cost_this_month=round(cost_month, 4),
    )
