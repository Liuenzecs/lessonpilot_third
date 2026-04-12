from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, Column, DateTime, ForeignKey, String, Text
from sqlmodel import Field, SQLModel

from app.models.base import utcnow


class AnalyticsEvent(SQLModel, table=True):
    __tablename__ = "analytics_events"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    event_name: str = Field(sa_column=Column(String(80), index=True, nullable=False))
    occurred_at: datetime = Field(default_factory=utcnow, sa_column=Column(DateTime(timezone=True), nullable=False))
    source: str = Field(sa_column=Column(String(16), index=True, nullable=False))
    user_id: str | None = Field(default=None, sa_column=Column(String(36), ForeignKey("users.id"), nullable=True))
    anonymous_id: str | None = Field(default=None, sa_column=Column(String(64), index=True, nullable=True))
    session_id: str = Field(sa_column=Column(String(64), index=True, nullable=False))
    page_path: str = Field(sa_column=Column(String(500), nullable=False))
    referrer: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    properties: dict = Field(default_factory=dict, sa_column=Column(JSON, nullable=False, default=dict))
    client_event_id: str | None = Field(default=None, sa_column=Column(String(120), unique=True, nullable=True))
    created_at: datetime = Field(default_factory=utcnow, sa_column=Column(DateTime(timezone=True), nullable=False))
