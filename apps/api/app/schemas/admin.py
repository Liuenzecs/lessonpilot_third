from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.account import FeedbackRead
from app.schemas.auth import UserRead
from app.schemas.billing import AccountSubscriptionRead, BillingOrderRead
from app.schemas.task import TaskRead


class AdminOverviewMetricRead(BaseModel):
    key: str
    label: str
    value: int


class AdminOverviewRead(BaseModel):
    last_7_days: list[AdminOverviewMetricRead]
    last_30_days: list[AdminOverviewMetricRead]


class AdminUserListItemRead(BaseModel):
    user: UserRead
    subscription: AccountSubscriptionRead


class AdminUserListResponse(BaseModel):
    items: list[AdminUserListItemRead]
    total: int


class QuotaAdjustmentRead(BaseModel):
    id: str
    user_id: str
    applied_by_user_id: str
    month_key: str
    delta: int
    reason: str | None = None
    created_at: datetime


class QuotaAdjustmentCreatePayload(BaseModel):
    delta: int = Field(ge=-100, le=100)
    reason: str | None = Field(default=None, max_length=1000)
    month_key: str | None = Field(default=None, pattern=r"^\d{4}-\d{2}$")


class QuotaAdjustmentListResponse(BaseModel):
    items: list[QuotaAdjustmentRead]


class AdminUserDetailRead(BaseModel):
    user: UserRead
    subscription: AccountSubscriptionRead
    latest_paid_order: BillingOrderRead | None = None
    recent_tasks: list[TaskRead]
    recent_feedback: list[FeedbackRead]
    quota_adjustments: list[QuotaAdjustmentRead]
