from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, EmailStr, Field

BillingCycle = Literal["monthly", "yearly"]
BillingChannel = Literal["wechat", "alipay"]
SubscriptionPlan = Literal["free", "professional"]
SubscriptionStatus = Literal["free", "trialing", "active", "expired"]


class SubscriptionEntitlementsRead(BaseModel):
    monthly_task_limit: int | None
    word_export: bool
    pdf_export: bool
    ai_rewrite: bool
    ai_append: bool
    section_regenerate: bool
    version_history: bool
    all_subject_presets: bool


class AccountSubscriptionRead(BaseModel):
    plan: SubscriptionPlan
    plan_label: str
    status: SubscriptionStatus
    is_paid: bool
    billing_cycle: BillingCycle | None
    trial_started_at: datetime | None = None
    trial_ends_at: datetime | None = None
    current_period_start: datetime | None = None
    current_period_end: datetime | None = None
    next_renewal_at: datetime | None = None
    monthly_task_limit: int | None = None
    tasks_used_this_month: int
    quota_remaining: int | None = None
    trial_used: bool
    entitlements: SubscriptionEntitlementsRead


class SubscriptionCheckoutPayload(BaseModel):
    plan: Literal["professional"] = "professional"
    billing_cycle: BillingCycle
    channel: BillingChannel


class BillingOrderRead(BaseModel):
    id: str
    plan: Literal["professional"]
    billing_cycle: BillingCycle
    channel: BillingChannel
    amount_cents: int
    status: Literal["pending", "paid", "failed", "expired"]
    checkout_url: str | None = None
    external_order_id: str | None = None
    paid_at: datetime | None = None
    effective_at: datetime | None = None
    created_at: datetime


class SubscriptionActionResponse(BaseModel):
    subscription: AccountSubscriptionRead
    order: BillingOrderRead | None = None
    message: str


class BillingOrderListResponse(BaseModel):
    items: list[BillingOrderRead]


class InvoiceRequestCreatePayload(BaseModel):
    order_id: str = Field(min_length=8, max_length=64)
    title: str = Field(min_length=2, max_length=200)
    tax_number: str = Field(min_length=6, max_length=64)
    email: EmailStr
    remark: str | None = Field(default=None, max_length=1000)


class InvoiceRequestRead(BaseModel):
    id: str
    order_id: str
    title: str
    tax_number: str
    email: EmailStr
    remark: str | None = None
    status: Literal["submitted"]
    created_at: datetime


class InvoiceRequestListResponse(BaseModel):
    items: list[InvoiceRequestRead]


class BillingWebhookPayload(BaseModel):
    event_id: str = Field(min_length=4, max_length=120)
    event_type: Literal["payment.succeeded", "payment.failed", "payment.expired"]
    order_id: str | None = Field(default=None, min_length=8, max_length=64)
    external_order_id: str | None = Field(default=None, min_length=4, max_length=120)
    channel: BillingChannel | None = None
    paid_at: datetime | None = None
    signature: str | None = Field(default=None, max_length=255)
    payload: dict[str, Any] = Field(default_factory=dict)


class BillingWebhookResponse(BaseModel):
    processed: bool
    message: str
