from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlmodel import Field, SQLModel

from app.models.base import utcnow


class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(sa_column=Column(String(36), ForeignKey("users.id"), index=True, nullable=False))
    title: str = Field(sa_column=Column(String(255), nullable=False))
    subject: str = Field(sa_column=Column(String(80), nullable=False))
    grade: str = Field(sa_column=Column(String(80), nullable=False))
    topic: str = Field(sa_column=Column(String(255), nullable=False))
    requirements: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    status: str = Field(default="draft", sa_column=Column(String(32), nullable=False))
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
