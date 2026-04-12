from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlmodel import Field, SQLModel

from app.models.base import utcnow


class EmailDeliveryLog(SQLModel, table=True):
    __tablename__ = "email_delivery_logs"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str | None = Field(default=None, sa_column=Column(String(36), ForeignKey("users.id"), nullable=True))
    template_key: str = Field(sa_column=Column(String(64), index=True, nullable=False))
    recipient_email: str = Field(sa_column=Column(String(255), index=True, nullable=False))
    subject: str = Field(sa_column=Column(String(255), nullable=False))
    delivery_mode: str = Field(sa_column=Column(String(16), nullable=False))
    status: str = Field(sa_column=Column(String(16), index=True, nullable=False))
    dedupe_key: str | None = Field(default=None, sa_column=Column(String(160), index=True, nullable=True))
    error_message: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    created_at: datetime = Field(default_factory=utcnow, sa_column=Column(DateTime(timezone=True), nullable=False))
