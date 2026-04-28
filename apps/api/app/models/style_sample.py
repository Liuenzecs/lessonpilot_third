"""风格样本模型 — 用于深度风格模型 (few-shot) 的自动学习。"""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text
from sqlmodel import Field, SQLModel

from app.models.base import utcnow


class StyleSample(SQLModel, table=True):
    """记录教师确认 section 时的风格数据，用于自动分析学习。"""

    __tablename__ = "style_samples"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(
        sa_column=Column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    )
    document_id: str = Field(
        sa_column=Column(String(36), ForeignKey("documents.id"), index=True, nullable=False)
    )
    subject: str = Field(sa_column=Column(String(80), nullable=False))
    grade: str = Field(sa_column=Column(String(80), nullable=False))
    section_key: str = Field(sa_column=Column(String(80), nullable=False))
    original_content: str | None = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )
    confirmed_content: str | None = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )
    diff_summary: str | None = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )
    extracted_patterns: dict | None = Field(
        default=None, sa_column=Column(JSON, nullable=True)
    )
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
