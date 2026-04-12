from __future__ import annotations

import hashlib
import secrets
from calendar import monthrange
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlmodel import Session, select

from app.core.config import get_settings
from app.models import BillingOrder, BillingWebhookEvent, InvoiceRequest, QuotaAdjustment, Task, User, UserSubscription
from app.models.base import utcnow
from app.schemas.billing import (
    AccountSubscriptionRead,
    BillingCycle,
    BillingOrderListResponse,
    BillingOrderRead,
    BillingWebhookPayload,
    InvoiceRequestCreatePayload,
    InvoiceRequestListResponse,
    InvoiceRequestRead,
    SubscriptionActionResponse,
    SubscriptionCheckoutPayload,
    SubscriptionEntitlementsRead,
)
from app.services.analytics_service import record_server_event

FREE_MONTHLY_TASK_LIMIT = 5


def _ensure_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _normalize_subscription_datetimes(subscription: UserSubscription) -> UserSubscription:
    subscription.trial_started_at = _ensure_utc(subscription.trial_started_at)
    subscription.trial_ends_at = _ensure_utc(subscription.trial_ends_at)
    subscription.current_period_start = _ensure_utc(subscription.current_period_start)
    subscription.current_period_end = _ensure_utc(subscription.current_period_end)
    subscription.trial_used_at = _ensure_utc(subscription.trial_used_at)
    return subscription


def month_start(now: datetime | None = None) -> datetime:
    current = now or datetime.now(UTC)
    return datetime(current.year, current.month, 1, tzinfo=UTC)


def month_key(now: datetime | None = None) -> str:
    current = now or datetime.now(UTC)
    return f"{current.year:04d}-{current.month:02d}"


def add_billing_period(start: datetime, billing_cycle: BillingCycle) -> datetime:
    if billing_cycle == "yearly":
        year = start.year + 1
        month = start.month
    else:
        year = start.year + (1 if start.month == 12 else 0)
        month = 1 if start.month == 12 else start.month + 1

    day = min(start.day, monthrange(year, month)[1])
    return start.replace(year=year, month=month, day=day)


def count_tasks_used_this_month(session: Session, user_id: str) -> int:
    created_after = month_start()
    tasks = session.exec(select(Task).where(Task.user_id == user_id, Task.created_at >= created_after)).all()
    return len(tasks)


def get_quota_adjustment_total(session: Session, user_id: str, *, for_month: str | None = None) -> int:
    target_month = for_month or month_key()
    statement = (
        select(func.coalesce(func.sum(QuotaAdjustment.delta), 0))
        .select_from(QuotaAdjustment)
        .where(QuotaAdjustment.user_id == user_id, QuotaAdjustment.month_key == target_month)
    )
    return int(session.exec(statement).one())


def ensure_subscription(session: Session, user: User) -> UserSubscription:
    subscription = session.exec(
        select(UserSubscription).where(UserSubscription.user_id == user.id)
    ).first()
    if subscription is None:
        subscription = UserSubscription(user_id=user.id)
        session.add(subscription)
        session.commit()
        session.refresh(subscription)
    subscription = _normalize_subscription_datetimes(subscription)
    return reconcile_subscription(session, subscription)


def reconcile_subscription(session: Session, subscription: UserSubscription) -> UserSubscription:
    subscription = _normalize_subscription_datetimes(subscription)
    now = utcnow()
    is_trial_live = bool(
        subscription.trial_started_at and subscription.trial_ends_at and subscription.trial_ends_at > now
    )
    has_active_period = bool(
        subscription.current_period_start
        and subscription.current_period_end
        and subscription.current_period_start <= now < subscription.current_period_end
    )

    if is_trial_live:
        target_plan = "professional"
        target_status = "trialing"
    elif has_active_period:
        target_plan = "professional"
        target_status = "active"
    elif subscription.plan == "professional" or subscription.trial_used_at or subscription.current_period_end:
        target_plan = "professional"
        target_status = "expired"
    else:
        target_plan = "free"
        target_status = "free"

    if subscription.plan != target_plan or subscription.status != target_status:
        subscription.plan = target_plan
        subscription.status = target_status
        subscription.updated_at = now
        session.add(subscription)
        session.commit()
        session.refresh(subscription)

    return subscription


def _has_professional_access(subscription: UserSubscription) -> bool:
    return subscription.status in {"trialing", "active"}


def _build_entitlements(subscription: UserSubscription) -> SubscriptionEntitlementsRead:
    if _has_professional_access(subscription):
        return SubscriptionEntitlementsRead(
            monthly_task_limit=None,
            word_export=True,
            pdf_export=True,
            ai_rewrite=True,
            ai_append=True,
            section_regenerate=True,
            version_history=True,
            all_subject_presets=True,
        )

    return SubscriptionEntitlementsRead(
        monthly_task_limit=FREE_MONTHLY_TASK_LIMIT,
        word_export=True,
        pdf_export=False,
        ai_rewrite=False,
        ai_append=False,
        section_regenerate=False,
        version_history=False,
        all_subject_presets=True,
    )


def _build_plan_label(subscription: UserSubscription) -> str:
    if subscription.status == "trialing":
        return "专业版试用中"
    if subscription.status == "active":
        return "专业版（月付）" if subscription.billing_cycle == "monthly" else "专业版（年付）"
    if subscription.status == "expired":
        return "专业版已到期"
    return "免费版"


def get_subscription_summary(session: Session, user: User) -> AccountSubscriptionRead:
    subscription = ensure_subscription(session, user)
    tasks_used_this_month = count_tasks_used_this_month(session, user.id)
    entitlements = _build_entitlements(subscription)
    quota_remaining = None
    if entitlements.monthly_task_limit is not None:
        entitlements.monthly_task_limit = max(
            entitlements.monthly_task_limit + get_quota_adjustment_total(session, user.id),
            0,
        )
        quota_remaining = max(entitlements.monthly_task_limit - tasks_used_this_month, 0)

    return AccountSubscriptionRead(
        plan=subscription.plan,
        plan_label=_build_plan_label(subscription),
        status=subscription.status,
        is_paid=subscription.status == "active",
        billing_cycle=subscription.billing_cycle,  # type: ignore[arg-type]
        trial_started_at=subscription.trial_started_at,
        trial_ends_at=subscription.trial_ends_at,
        current_period_start=subscription.current_period_start,
        current_period_end=subscription.current_period_end,
        next_renewal_at=subscription.current_period_end if subscription.status == "active" else None,
        monthly_task_limit=entitlements.monthly_task_limit,
        tasks_used_this_month=tasks_used_this_month,
        quota_remaining=quota_remaining,
        trial_used=subscription.trial_used_at is not None,
        entitlements=entitlements,
    )


def _billing_error(
    *,
    code: str,
    message: str,
    subscription: AccountSubscriptionRead,
) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_402_PAYMENT_REQUIRED,
        detail={
            "code": code,
            "message": message,
            "subscription": subscription.model_dump(mode="json"),
            "entitlements": subscription.entitlements.model_dump(mode="json"),
        },
    )


def require_task_quota(session: Session, user: User) -> AccountSubscriptionRead:
    summary = get_subscription_summary(session, user)
    if summary.monthly_task_limit is None:
        return summary
    if summary.tasks_used_this_month >= summary.monthly_task_limit:
        raise _billing_error(
            code="quota_exceeded",
            message="免费版每月最多新建 5 份教案，请升级到专业版继续使用。",
            subscription=summary,
        )
    return summary


def require_professional_feature(session: Session, user: User, feature_name: str) -> AccountSubscriptionRead:
    summary = get_subscription_summary(session, user)
    if summary.status in {"trialing", "active"}:
        return summary
    raise _billing_error(
        code="plan_required",
        message=f"{feature_name}为专业版能力，请升级后继续使用。",
        subscription=summary,
    )


def _professional_price_cents(billing_cycle: BillingCycle) -> int:
    settings = get_settings()
    if billing_cycle == "yearly":
        return settings.billing_professional_yearly_price_cents
    return settings.billing_professional_monthly_price_cents


def serialize_order(order: BillingOrder) -> BillingOrderRead:
    return BillingOrderRead(
        id=order.id,
        plan="professional",
        billing_cycle=order.billing_cycle,  # type: ignore[arg-type]
        channel=order.channel,  # type: ignore[arg-type]
        amount_cents=order.amount_cents,
        status=order.status,  # type: ignore[arg-type]
        checkout_url=order.checkout_url,
        external_order_id=order.external_order_id,
        paid_at=_ensure_utc(order.paid_at),
        effective_at=_ensure_utc(order.effective_at),
        created_at=_ensure_utc(order.created_at),
    )


def list_subscription_orders(session: Session, user: User) -> BillingOrderListResponse:
    orders = session.exec(
        select(BillingOrder).where(BillingOrder.user_id == user.id).order_by(BillingOrder.created_at.desc())
    ).all()
    return BillingOrderListResponse(items=[serialize_order(order) for order in orders])


def serialize_invoice_request(invoice_request: InvoiceRequest) -> InvoiceRequestRead:
    return InvoiceRequestRead(
        id=invoice_request.id,
        order_id=invoice_request.order_id,
        title=invoice_request.title,
        tax_number=invoice_request.tax_number,
        email=invoice_request.email,
        remark=invoice_request.remark,
        status="submitted",
        created_at=invoice_request.created_at,
    )


def list_invoice_requests(session: Session, user: User) -> InvoiceRequestListResponse:
    entries = session.exec(
        select(InvoiceRequest).where(InvoiceRequest.user_id == user.id).order_by(InvoiceRequest.created_at.desc())
    ).all()
    return InvoiceRequestListResponse(items=[serialize_invoice_request(entry) for entry in entries])


def start_trial(session: Session, user: User) -> SubscriptionActionResponse:
    settings = get_settings()
    subscription = _normalize_subscription_datetimes(ensure_subscription(session, user))
    if subscription.trial_used_at is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="每个账户只能开启一次 7 天免费试用")
    if subscription.status in {"trialing", "active"}:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="当前订阅状态无法再次开启试用")

    now = utcnow()
    subscription.plan = "professional"
    subscription.status = "trialing"
    subscription.trial_started_at = now
    subscription.trial_ends_at = now + timedelta(days=settings.billing_trial_days)
    subscription.trial_used_at = now
    subscription.updated_at = now
    session.add(subscription)
    session.commit()
    session.refresh(subscription)

    return SubscriptionActionResponse(
        subscription=get_subscription_summary(session, user),
        order=None,
        message="已开启 7 天免费试用，专业版能力已立即解锁。",
    )


def _build_external_order_id() -> str:
    return f"LP-{secrets.token_hex(8).upper()}"


def _build_checkout_url(order: BillingOrder) -> str:
    settings = get_settings()
    return f"{settings.billing_return_url.rstrip('/')}?order_id={order.id}&channel={order.channel}"


def _create_order(
    *,
    session: Session,
    user: User,
    subscription: UserSubscription,
    payload: SubscriptionCheckoutPayload,
    effective_at: datetime,
) -> BillingOrder:
    order = BillingOrder(
        user_id=user.id,
        subscription_id=subscription.id,
        plan="professional",
        billing_cycle=payload.billing_cycle,
        channel=payload.channel,
        amount_cents=_professional_price_cents(payload.billing_cycle),
        status="pending",
        external_order_id=_build_external_order_id(),
        effective_at=effective_at,
    )
    order.checkout_url = _build_checkout_url(order)
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


def _mark_order_paid(
    session: Session,
    subscription: UserSubscription,
    order: BillingOrder,
    *,
    paid_at: datetime,
) -> BillingOrder:
    subscription = _normalize_subscription_datetimes(subscription)
    paid_at = _ensure_utc(paid_at) or utcnow()
    order.effective_at = _ensure_utc(order.effective_at)

    if order.status == "paid":
        return order

    order.status = "paid"
    order.paid_at = paid_at
    order.updated_at = paid_at
    if order.effective_at is None:
        order.effective_at = paid_at

    subscription.plan = "professional"
    subscription.billing_cycle = order.billing_cycle
    if (
        subscription.status == "active"
        and subscription.current_period_end is not None
        and order.effective_at == subscription.current_period_end
        and subscription.current_period_start is not None
        and subscription.current_period_start <= paid_at < subscription.current_period_end
    ):
        subscription.current_period_end = add_billing_period(subscription.current_period_end, order.billing_cycle)  # type: ignore[arg-type]
    else:
        subscription.current_period_start = order.effective_at
        subscription.current_period_end = add_billing_period(order.effective_at, order.billing_cycle)  # type: ignore[arg-type]

    if subscription.trial_ends_at and subscription.trial_ends_at > paid_at:
        subscription.status = "trialing"
    else:
        subscription.status = "active"

    subscription.updated_at = paid_at
    session.add(order)
    session.add(subscription)
    session.commit()
    session.refresh(order)
    session.refresh(subscription)
    reconcile_subscription(session, subscription)
    user = session.get(User, order.user_id)
    if user is not None:
        record_server_event(
            session,
            event_name="payment_succeeded",
            user=user,
            page_path="/settings",
            properties={
                "billing_cycle": order.billing_cycle,
                "channel": order.channel,
                "amount_cents": order.amount_cents,
            },
            occurred_at=paid_at,
        )
    return order


def create_checkout(session: Session, user: User, payload: SubscriptionCheckoutPayload) -> SubscriptionActionResponse:
    subscription = _normalize_subscription_datetimes(ensure_subscription(session, user))
    now = utcnow()
    if subscription.status == "active":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="当前专业版仍在有效期内，请使用手动续费")
    if (
        subscription.status == "trialing"
        and subscription.current_period_start is not None
        and subscription.current_period_start > now
    ):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="试用结束后的付费周期已安排，无需重复支付")

    effective_at = (
        subscription.trial_ends_at
        if subscription.status == "trialing" and subscription.trial_ends_at and subscription.trial_ends_at > now
        else now
    )
    order = _create_order(
        session=session,
        user=user,
        subscription=subscription,
        payload=payload,
        effective_at=effective_at,
    )

    if get_settings().billing_mode == "mock":
        order = _mark_order_paid(session, subscription, order, paid_at=now)
        message = "模拟支付已完成，订阅状态已更新。"
    else:
        message = "订单已创建，请完成支付后返回 LessonPilot。"

    return SubscriptionActionResponse(
        subscription=get_subscription_summary(session, user),
        order=serialize_order(order),
        message=message,
    )


def renew_subscription(
    session: Session,
    user: User,
    payload: SubscriptionCheckoutPayload,
) -> SubscriptionActionResponse:
    subscription = _normalize_subscription_datetimes(ensure_subscription(session, user))
    now = utcnow()
    if subscription.status != "active" or subscription.current_period_end is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="当前没有可续费的专业版订阅")

    effective_at = subscription.current_period_end if subscription.current_period_end > now else now
    order = _create_order(
        session=session,
        user=user,
        subscription=subscription,
        payload=payload,
        effective_at=effective_at,
    )

    if get_settings().billing_mode == "mock":
        order = _mark_order_paid(session, subscription, order, paid_at=now)
        message = "模拟续费已完成，新的订阅周期已顺延。"
    else:
        message = "续费订单已创建，请完成支付。"

    return SubscriptionActionResponse(
        subscription=get_subscription_summary(session, user),
        order=serialize_order(order),
        message=message,
    )


def create_invoice_request(session: Session, user: User, payload: InvoiceRequestCreatePayload) -> InvoiceRequestRead:
    order = session.exec(
        select(BillingOrder).where(BillingOrder.id == payload.order_id, BillingOrder.user_id == user.id)
    ).first()
    if order is None or order.status != "paid":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未找到可开票的已支付订单")

    entry = InvoiceRequest(
        user_id=user.id,
        order_id=order.id,
        title=payload.title.strip(),
        tax_number=payload.tax_number.strip(),
        email=payload.email.strip().lower(),
        remark=payload.remark.strip() if payload.remark else None,
    )
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return serialize_invoice_request(entry)


def _hash_signature(payload: BillingWebhookPayload) -> str:
    secret = get_settings().billing_webhook_secret
    raw = f"{payload.event_id}:{payload.event_type}:{payload.order_id or payload.external_order_id}:{secret}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def process_billing_webhook(session: Session, payload: BillingWebhookPayload) -> bool:
    existing = session.exec(
        select(BillingWebhookEvent).where(BillingWebhookEvent.event_id == payload.event_id)
    ).first()
    if existing is not None:
        return False

    signature_valid = True
    if get_settings().billing_mode == "gateway":
        signature_valid = payload.signature == _hash_signature(payload)
        if not signature_valid:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid billing webhook signature")

    order = None
    if payload.order_id:
        order = session.get(BillingOrder, payload.order_id)
    if order is None and payload.external_order_id:
        order = session.exec(
            select(BillingOrder).where(BillingOrder.external_order_id == payload.external_order_id)
        ).first()
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Billing order not found")

    event = BillingWebhookEvent(
        event_id=payload.event_id,
        event_type=payload.event_type,
        channel=payload.channel,
        signature_valid=signature_valid,
        payload=payload.model_dump(mode="json"),
        processed_at=utcnow(),
    )
    session.add(event)

    subscription = None
    if order.subscription_id:
        subscription = session.get(UserSubscription, order.subscription_id)

    if payload.event_type == "payment.succeeded":
        if subscription is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")
        _mark_order_paid(session, subscription, order, paid_at=_ensure_utc(payload.paid_at) or utcnow())
    else:
        order.status = "failed" if payload.event_type == "payment.failed" else "expired"
        order.updated_at = utcnow()
        session.add(order)
        session.commit()

    session.commit()
    return True
