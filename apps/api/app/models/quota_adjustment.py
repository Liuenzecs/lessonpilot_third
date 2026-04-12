from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlmodel import Field, SQLModel

from app.models.base import utcnow


class QuotaAdjustment(SQLModel, table=True):
    __tablename__ = "quota_adjustments"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(sa_column=Column(String(36), ForeignKey("users.id"), index=True, nullable=False))
    applied_by_user_id: str = Field(sa_column=Column(String(36), ForeignKey("users.id"), nullable=False))
    month_key: str = Field(sa_column=Column(String(7), index=True, nullable=False))
    delta: int = Field(sa_column=Column(Integer, nullable=False))
    reason: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    created_at: datetime = Field(default_factory=utcnow, sa_column=Column(DateTime(timezone=True), nullable=False))
