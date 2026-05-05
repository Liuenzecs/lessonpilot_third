"""Admin API — minimal admin endpoints for public-service operations."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import Response
from sqlmodel import Session, func, select

from app.core.db import get_session
from app.core.security import require_admin
from app.models import CostLog, User
from app.schemas.admin import (
    AdminDisableUserPayload,
    AdminStatsResponse,
    AdminUserListResponse,
    AdminUserSummary,
)
from app.services.budget_service import check_budget_status

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/check")
def check_admin_access(_admin: User = Depends(require_admin)) -> dict:
    """轻量权限检查：200=管理员，403=无权限。"""
    return {"ok": True}


@router.get("/users", response_model=AdminUserListResponse)
def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    search: str = Query(""),
    session: Session = Depends(get_session),
    _admin: User = Depends(require_admin),
) -> AdminUserListResponse:
    stmt = select(User)
    if search:
        stmt = stmt.where(
            (User.email.ilike(f"%{search}%")) | (User.name.ilike(f"%{search}%"))
        )
    count_stmt = select(func.count(User.id))
    if search:
        count_stmt = count_stmt.where(
            (User.email.ilike(f"%{search}%")) | (User.name.ilike(f"%{search}%"))
        )
    total = session.exec(count_stmt).one()

    users = session.exec(stmt.order_by(User.created_at.desc()).offset((page - 1) * limit).limit(limit)).all()

    now = datetime.now(UTC)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    summaries: list[AdminUserSummary] = []
    for u in users:
        gens_today = session.exec(
            select(func.count(CostLog.id)).where(
                CostLog.user_id == u.id,
                CostLog.created_at >= start_of_day,
            )
        ).one()
        gens_month = session.exec(
            select(func.count(CostLog.id)).where(
                CostLog.user_id == u.id,
                CostLog.created_at >= start_of_month,
            )
        ).one()
        cost_month = session.exec(
            select(func.coalesce(func.sum(CostLog.cost_cny), 0.0)).where(
                CostLog.user_id == u.id,
                CostLog.created_at >= start_of_month,
            )
        ).one()
        summaries.append(
            AdminUserSummary(
                id=u.id,
                email=u.email,
                name=u.name,
                role=u.role,
                is_disabled=u.is_disabled,
                email_verified=u.email_verified,
                created_at=u.created_at,
                gens_today=gens_today,
                gens_this_month=gens_month,
                cost_this_month=round(float(cost_month), 4),
            )
        )

    return AdminUserListResponse(users=summaries, total=total, page=page, limit=limit)


@router.post("/users/{user_id}/disable", status_code=status.HTTP_204_NO_CONTENT)
def disable_user(
    user_id: str,
    payload: AdminDisableUserPayload = Depends(),
    session: Session = Depends(get_session),
    _admin: User = Depends(require_admin),
) -> Response:
    user = session.get(User, user_id)
    if user is None:
        from fastapi import HTTPException as HTTPE
        raise HTTPE(status_code=404, detail="User not found")
    user.is_disabled = True
    user.disabled_at = datetime.now(UTC)
    user.disabled_reason = payload.reason or None
    session.add(user)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/users/{user_id}/enable", status_code=status.HTTP_204_NO_CONTENT)
def enable_user(
    user_id: str,
    session: Session = Depends(get_session),
    _admin: User = Depends(require_admin),
) -> Response:
    user = session.get(User, user_id)
    if user is None:
        from fastapi import HTTPException as HTTPE
        raise HTTPE(status_code=404, detail="User not found")
    user.is_disabled = False
    user.disabled_at = None
    user.disabled_reason = None
    session.add(user)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/stats", response_model=AdminStatsResponse)
def get_admin_stats(
    session: Session = Depends(get_session),
    _admin: User = Depends(require_admin),
) -> AdminStatsResponse:
    now = datetime.now(UTC)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    seven_days_ago = now - timedelta(days=7)
    thirty_days_ago = now - timedelta(days=30)

    total_users = session.exec(select(func.count(User.id))).one()
    active_7d = session.exec(
        select(func.count(func.distinct(CostLog.user_id))).where(
            CostLog.created_at >= seven_days_ago,
        )
    ).one()
    active_30d = session.exec(
        select(func.count(func.distinct(CostLog.user_id))).where(
            CostLog.created_at >= thirty_days_ago,
        )
    ).one()

    gens_today = session.exec(
        select(func.count(CostLog.id)).where(CostLog.created_at >= start_of_day)
    ).one()
    gens_month = session.exec(
        select(func.count(CostLog.id)).where(CostLog.created_at >= start_of_month)
    ).one()

    cost_today = float(session.exec(
        select(func.coalesce(func.sum(CostLog.cost_cny), 0.0)).where(
            CostLog.created_at >= start_of_day,
        )
    ).one())
    cost_month = float(session.exec(
        select(func.coalesce(func.sum(CostLog.cost_cny), 0.0)).where(
            CostLog.created_at >= start_of_month,
        )
    ).one())

    budget_status = check_budget_status(session=session)

    return AdminStatsResponse(
        total_users=total_users,
        active_users_7d=active_7d,
        active_users_30d=active_30d,
        total_generations_today=gens_today,
        total_generations_this_month=gens_month,
        cost_today=round(cost_today, 4),
        cost_this_month=round(cost_month, 4),
        budget_status=budget_status,
    )
