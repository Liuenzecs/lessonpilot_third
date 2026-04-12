from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from app.core.db import get_session
from app.core.security import get_current_user
from app.models import User
from app.schemas.admin import (
    AdminOverviewRead,
    AdminUserDetailRead,
    AdminUserListResponse,
    QuotaAdjustmentCreatePayload,
    QuotaAdjustmentListResponse,
    QuotaAdjustmentRead,
)
from app.services.admin_service import (
    create_quota_adjustment,
    get_admin_overview,
    get_admin_user_detail,
    list_admin_users,
    list_quota_adjustments,
    require_admin_user,
)

router = APIRouter(prefix="/admin", tags=["admin"])


def _admin_guard(current_user: User = Depends(get_current_user)) -> User:
    return require_admin_user(current_user)


@router.get("/overview", response_model=AdminOverviewRead)
def get_overview(
    session: Session = Depends(get_session),
    _: User = Depends(_admin_guard),
) -> AdminOverviewRead:
    return get_admin_overview(session)


@router.get("/users", response_model=AdminUserListResponse)
def get_users(
    query: str | None = Query(default=None, max_length=255),
    plan: str | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    session: Session = Depends(get_session),
    _: User = Depends(_admin_guard),
) -> AdminUserListResponse:
    return list_admin_users(session, query=query, plan=plan, status_filter=status_filter)


@router.get("/users/{user_id}", response_model=AdminUserDetailRead)
def get_user_detail(
    user_id: str,
    session: Session = Depends(get_session),
    _: User = Depends(_admin_guard),
) -> AdminUserDetailRead:
    return get_admin_user_detail(session, user_id)


@router.get("/users/{user_id}/quota-adjustments", response_model=QuotaAdjustmentListResponse)
def get_user_quota_adjustments(
    user_id: str,
    session: Session = Depends(get_session),
    _: User = Depends(_admin_guard),
) -> QuotaAdjustmentListResponse:
    return list_quota_adjustments(session, user_id)


@router.post(
    "/users/{user_id}/quota-adjustments",
    response_model=QuotaAdjustmentRead,
    status_code=status.HTTP_201_CREATED,
)
def post_user_quota_adjustment(
    user_id: str,
    payload: QuotaAdjustmentCreatePayload,
    session: Session = Depends(get_session),
    current_user: User = Depends(_admin_guard),
) -> QuotaAdjustmentRead:
    return create_quota_adjustment(session, target_user_id=user_id, admin_user=current_user, payload=payload)
