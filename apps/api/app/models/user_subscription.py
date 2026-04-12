from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlmodel import Field, SQLModel

from app.models.base import utcnow


class UserSubscription(SQLModel, table=True):
    __tablename__ = "user_subscriptions"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(
        sa_column=Column(String(36), ForeignKey("users.id"), unique=True, index=True, nullable=False)
    )
    plan: str = Field(default="free", sa_column=Column(String(32), nullable=False))
    status: str = Field(default="free", sa_column=Column(String(32), nullable=False))
    billing_cycle: str | None = Field(default=None, sa_column=Column(String(16), nullable=True))
    trial_started_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    trial_ends_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    current_period_start: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    current_period_end: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    trial_used_at: datetime | None = Field(
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
