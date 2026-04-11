from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlmodel import Field, SQLModel

from app.models.base import utcnow


class Feedback(SQLModel, table=True):
    __tablename__ = "feedback_entries"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(sa_column=Column(String(36), ForeignKey("users.id"), index=True, nullable=False))
    mood: str = Field(sa_column=Column(String(16), nullable=False))
    message: str = Field(sa_column=Column(Text, nullable=False))
    page_path: str | None = Field(default=None, sa_column=Column(String(500), nullable=True))
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
