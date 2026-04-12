from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, Boolean, Column, DateTime, String
from sqlmodel import Field, SQLModel

from app.models.base import utcnow


class BillingWebhookEvent(SQLModel, table=True):
    __tablename__ = "billing_webhook_events"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    event_id: str = Field(sa_column=Column(String(120), unique=True, index=True, nullable=False))
    event_type: str = Field(sa_column=Column(String(64), nullable=False))
    channel: str | None = Field(default=None, sa_column=Column(String(16), nullable=True))
    signature_valid: bool = Field(default=False, sa_column=Column(Boolean, nullable=False, default=False))
    payload: dict = Field(sa_column=Column(JSON, nullable=False))
    processed_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
