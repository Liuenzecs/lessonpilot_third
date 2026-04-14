from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String
from sqlmodel import Field, SQLModel

from app.models.base import utcnow


class Document(SQLModel, table=True):
    __tablename__ = "documents"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    task_id: str = Field(
        sa_column=Column(String(36), ForeignKey("tasks.id"), index=True, nullable=False)
    )
    user_id: str = Field(
        sa_column=Column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    )
    doc_type: str = Field(default="lesson_plan", sa_column=Column(String(32), nullable=False))
    title: str = Field(sa_column=Column(String(255), nullable=False))
    content: dict = Field(sa_column=Column(JSON, nullable=False))
    version: int = Field(default=1, sa_column=Column(Integer, nullable=False))
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
