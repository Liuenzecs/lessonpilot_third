"""教学反思模型 — 课后反思记录，反馈到下次备课。"""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlmodel import Field, SQLModel

from app.models.base import utcnow


class TeachingReflection(SQLModel, table=True):
    """教师课后填写的结构化反思。"""

    __tablename__ = "teaching_reflections"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    task_id: str = Field(
        sa_column=Column(String(36), ForeignKey("tasks.id"), index=True, nullable=False)
    )
    user_id: str = Field(
        sa_column=Column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    )
    goal_achievement: int = Field(
        default=3, sa_column=Column(Integer, nullable=False)
    )
    difficulty_handling: str | None = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )
    student_response: str | None = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )
    time_feedback: str | None = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )
    improvement_notes: str | None = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )
    free_text: str | None = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
