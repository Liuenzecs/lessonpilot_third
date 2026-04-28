"""教学单元模型 — 学期内单元分组。"""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlmodel import Field, SQLModel

from app.models.base import utcnow


class TeachingUnit(SQLModel, table=True):
    """学期下的教学单元，如'第一单元：散文阅读'。"""

    __tablename__ = "teaching_units"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    semester_id: str = Field(
        sa_column=Column(String(36), ForeignKey("semesters.id"), index=True, nullable=False)
    )
    name: str = Field(sa_column=Column(String(255), nullable=False))
    order: int = Field(default=1, sa_column=Column(Integer, nullable=False))
    topic_overview: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
