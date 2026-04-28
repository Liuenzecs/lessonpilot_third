"""班级组模型 — 用于同课多班差异化。"""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlmodel import Field, SQLModel

from app.models.base import utcnow


class ClassGroup(SQLModel, table=True):
    """教师自定义的班级分组，如'高一3班（重点）'。"""

    __tablename__ = "class_groups"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(
        sa_column=Column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    )
    name: str = Field(sa_column=Column(String(120), nullable=False))
    level: str = Field(
        default="standard",
        sa_column=Column(String(32), nullable=False, default="standard"),
    )
    notes: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
