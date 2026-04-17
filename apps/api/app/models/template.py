from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlmodel import Field, SQLModel

from app.models.base import utcnow


class Template(SQLModel, table=True):
    """Base template for lesson plans and study guides."""
    __tablename__ = "templates"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    name: str = Field(sa_column=Column(String(255), nullable=False))
    subject: str = Field(sa_column=Column(String(80), nullable=False, index=True))
    grade: str = Field(sa_column=Column(String(80), nullable=False, index=True))
    description: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    template_type: str = Field(
        default="lesson_plan",
        sa_column=Column(String(32), nullable=False, index=True),
    )
    content: dict = Field(
        default={},
        sa_column=Column(JSON, nullable=False),
    )
    is_public: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, index=True),
    )
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


class TemplateSection(SQLModel, table=True):
    """Individual sections within a template."""
    __tablename__ = "template_sections"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    template_id: str = Field(
        sa_column=Column(String(36), ForeignKey("templates.id", ondelete="CASCADE"), index=True, nullable=False)
    )
    section_name: str = Field(sa_column=Column(String(255), nullable=False))
    order: int = Field(sa_column=Column(Integer, nullable=False))
    description: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    prompt_hints: str | None = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
    )
    schema_constraints: dict | None = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
