from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import func, or_
from sqlmodel import Session, select

from app.core.config import get_settings
from app.models import AnalyticsEvent, BillingOrder, Feedback, QuotaAdjustment, Task, User
from app.schemas.account import FeedbackRead
from app.schemas.admin import (
    AdminOverviewMetricRead,
    AdminOverviewRead,
    AdminUserDetailRead,
    AdminUserListItemRead,
    AdminUserListResponse,
    QuotaAdjustmentCreatePayload,
    QuotaAdjustmentListResponse,
    QuotaAdjustmentRead,
)
from app.schemas.auth import UserRead
from app.schemas.task import TaskRead
from app.services.billing_service import get_subscription_summary, serialize_order

ADMIN_OVERVIEW_EVENTS = [
    ("page_view", "页面访问"),
    ("cta_click", "CTA 点击"),
    ("register_success", "注册成功"),
    ("trial_started", "开始试用"),
    ("checkout_started", "发起支付"),
    ("payment_succeeded", "支付成功"),
    ("task_created", "新建教案"),
    ("task_duplicated", "复制教案"),
    ("docx_export_succeeded", "Word 导出"),
    ("pdf_export_succeeded", "PDF 导出"),
    ("feedback_submitted", "反馈提交"),
]


def require_admin_user(current_user: User) -> User:
    if current_user.email.lower() not in get_settings().admin_allowlist:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="你没有访问管理后台的权限")
    return current_user


def _serialize_user(user: User) -> UserRead:
    return UserRead(
        id=user.id,
        email=user.email,
        name=user.name,
        email_verified=user.email_verified,
        email_verified_at=user.email_verified_at,
        created_at=user.created_at,
    )


def _serialize_task(task: Task) -> TaskRead:
    return TaskRead(
        id=task.id,
        title=task.title,
        subject=task.subject,
        grade=task.grade,
        topic=task.topic,
        requirements=task.requirements,
        status=task.status,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


def _serialize_feedback(entry: Feedback) -> FeedbackRead:
    return FeedbackRead(
        id=entry.id,
        user_id=entry.user_id,
        mood=entry.mood,
        message=entry.message,
        page_path=entry.page_path,
        created_at=entry.created_at,
    )


def _serialize_adjustment(entry: QuotaAdjustment) -> QuotaAdjustmentRead:
    return QuotaAdjustmentRead(
        id=entry.id,
        user_id=entry.user_id,
        applied_by_user_id=entry.applied_by_user_id,
        month_key=entry.month_key,
        delta=entry.delta,
        reason=entry.reason,
        created_at=entry.created_at,
    )


def _count_events_since(session: Session, since: datetime) -> dict[str, int]:
    rows = session.exec(
        select(AnalyticsEvent.event_name, func.count())
        .where(AnalyticsEvent.occurred_at >= since)
        .group_by(AnalyticsEvent.event_name)
    ).all()
    return {event_name: int(count) for event_name, count in rows}


def get_admin_overview(session: Session) -> AdminOverviewRead:
    now = datetime.now(UTC)
    counts_7 = _count_events_since(session, now - timedelta(days=7))
    counts_30 = _count_events_since(session, now - timedelta(days=30))

    return AdminOverviewRead(
        last_7_days=[
            AdminOverviewMetricRead(key=key, label=label, value=counts_7.get(key, 0))
            for key, label in ADMIN_OVERVIEW_EVENTS
        ],
        last_30_days=[
            AdminOverviewMetricRead(key=key, label=label, value=counts_30.get(key, 0))
            for key, label in ADMIN_OVERVIEW_EVENTS
        ],
    )


def list_admin_users(
    session: Session,
    *,
    query: str | None = None,
    plan: str | None = None,
    status_filter: str | None = None,
) -> AdminUserListResponse:
    statement = select(User).order_by(User.created_at.desc())
    if query:
        like = f"%{query.strip()}%"
        statement = statement.where(or_(User.email.ilike(like), User.name.ilike(like)))

    users = session.exec(statement).all()
    items: list[AdminUserListItemRead] = []
    for user in users:
        subscription = get_subscription_summary(session, user)
        if plan and subscription.plan != plan:
            continue
        if status_filter and subscription.status != status_filter:
            continue
        items.append(AdminUserListItemRead(user=_serialize_user(user), subscription=subscription))

    return AdminUserListResponse(items=items, total=len(items))


def get_admin_user_detail(session: Session, user_id: str) -> AdminUserDetailRead:
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    latest_paid_order = session.exec(
        select(BillingOrder)
        .where(BillingOrder.user_id == user_id, BillingOrder.status == "paid")
        .order_by(BillingOrder.created_at.desc())
    ).first()
    recent_tasks = session.exec(
        select(Task).where(Task.user_id == user_id).order_by(Task.updated_at.desc()).limit(5)
    ).all()
    recent_feedback = session.exec(
        select(Feedback).where(Feedback.user_id == user_id).order_by(Feedback.created_at.desc()).limit(5)
    ).all()
    quota_adjustments = session.exec(
        select(QuotaAdjustment).where(QuotaAdjustment.user_id == user_id).order_by(QuotaAdjustment.created_at.desc())
    ).all()

    return AdminUserDetailRead(
        user=_serialize_user(user),
        subscription=get_subscription_summary(session, user),
        latest_paid_order=serialize_order(latest_paid_order) if latest_paid_order else None,
        recent_tasks=[_serialize_task(task) for task in recent_tasks],
        recent_feedback=[_serialize_feedback(entry) for entry in recent_feedback],
        quota_adjustments=[_serialize_adjustment(entry) for entry in quota_adjustments],
    )


def list_quota_adjustments(session: Session, user_id: str) -> QuotaAdjustmentListResponse:
    if session.get(User, user_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    rows = session.exec(
        select(QuotaAdjustment).where(QuotaAdjustment.user_id == user_id).order_by(QuotaAdjustment.created_at.desc())
    ).all()
    return QuotaAdjustmentListResponse(items=[_serialize_adjustment(entry) for entry in rows])


def create_quota_adjustment(
    session: Session,
    *,
    target_user_id: str,
    admin_user: User,
    payload: QuotaAdjustmentCreatePayload,
) -> QuotaAdjustmentRead:
    target_user = session.get(User, target_user_id)
    if target_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    subscription = get_subscription_summary(session, target_user)
    if subscription.monthly_task_limit is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="当前用户没有可调整的免费额度上限")

    month_key = payload.month_key or datetime.now(UTC).strftime("%Y-%m")
    adjustment = QuotaAdjustment(
        user_id=target_user.id,
        applied_by_user_id=admin_user.id,
        month_key=month_key,
        delta=payload.delta,
        reason=payload.reason.strip() if payload.reason else None,
    )
    session.add(adjustment)
    session.commit()
    session.refresh(adjustment)
    return _serialize_adjustment(adjustment)
