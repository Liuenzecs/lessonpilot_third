from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlmodel import Field, SQLModel

from app.models.base import utcnow


class BillingOrder(SQLModel, table=True):
    __tablename__ = "billing_orders"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(sa_column=Column(String(36), ForeignKey("users.id"), index=True, nullable=False))
    subscription_id: str | None = Field(
        default=None,
        sa_column=Column(String(36), ForeignKey("user_subscriptions.id"), index=True, nullable=True),
    )
    plan: str = Field(default="professional", sa_column=Column(String(32), nullable=False))
    billing_cycle: str = Field(sa_column=Column(String(16), nullable=False))
    channel: str = Field(sa_column=Column(String(16), nullable=False))
    amount_cents: int = Field(sa_column=Column(Integer, nullable=False))
    status: str = Field(default="pending", sa_column=Column(String(32), nullable=False))
    checkout_url: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    external_order_id: str | None = Field(
        default=None,
        sa_column=Column(String(120), unique=True, index=True, nullable=True),
    )
    paid_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    effective_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
