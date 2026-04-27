from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, Column, DateTime, ForeignKey, String
from sqlmodel import Field, SQLModel

from app.models.base import utcnow


class TeachingPackage(SQLModel, table=True):
    """Structured classroom package generated from a lesson plan."""

    __tablename__ = "teaching_packages"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(sa_column=Column(String(36), ForeignKey("users.id"), index=True, nullable=False))
    task_id: str = Field(sa_column=Column(String(36), ForeignKey("tasks.id"), index=True, nullable=False))
    document_id: str = Field(sa_column=Column(String(36), ForeignKey("documents.id"), index=True, nullable=False))
    title: str = Field(sa_column=Column(String(255), nullable=False))
    status: str = Field(default="pending", sa_column=Column(String(32), nullable=False))
    content: dict = Field(default={}, sa_column=Column(JSON, nullable=False))
    created_at: datetime = Field(default_factory=utcnow, sa_column=Column(DateTime(timezone=True), nullable=False))
    updated_at: datetime = Field(default_factory=utcnow, sa_column=Column(DateTime(timezone=True), nullable=False))
