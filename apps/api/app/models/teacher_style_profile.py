from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlmodel import Field, SQLModel

from app.models.base import utcnow


class TeacherStyleProfile(SQLModel, table=True):
    """Private teacher writing-style memory for generation prompts."""

    __tablename__ = "teacher_style_profiles"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(sa_column=Column(String(36), ForeignKey("users.id"), unique=True, index=True, nullable=False))
    enabled: bool = Field(default=True, sa_column=Column(Boolean, nullable=False, default=True))
    objective_style: str = Field(default="", sa_column=Column(Text, nullable=False, default=""))
    process_style: str = Field(default="", sa_column=Column(Text, nullable=False, default=""))
    school_wording: str = Field(default="", sa_column=Column(Text, nullable=False, default=""))
    activity_preferences: str = Field(default="", sa_column=Column(Text, nullable=False, default=""))
    avoid_phrases: str = Field(default="", sa_column=Column(Text, nullable=False, default=""))
    sample_count: int = Field(default=0, sa_column=Column(Integer, nullable=False, default=0))
    created_at: datetime = Field(default_factory=utcnow, sa_column=Column(DateTime(timezone=True), nullable=False))
    updated_at: datetime = Field(default_factory=utcnow, sa_column=Column(DateTime(timezone=True), nullable=False))
