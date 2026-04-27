from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, Column, DateTime, ForeignKey, String
from sqlmodel import Field, SQLModel

from app.models.base import utcnow


class PersonalAsset(SQLModel, table=True):
    """Teacher-owned imported material for later reuse."""

    __tablename__ = "personal_assets"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(sa_column=Column(String(36), ForeignKey("users.id"), index=True, nullable=False))
    title: str = Field(sa_column=Column(String(255), nullable=False))
    asset_type: str = Field(sa_column=Column(String(50), nullable=False, index=True))
    source_filename: str = Field(sa_column=Column(String(255), nullable=False))
    file_type: str = Field(sa_column=Column(String(16), nullable=False))
    subject: str = Field(default="语文", sa_column=Column(String(80), nullable=False, index=True))
    grade: str = Field(default="", sa_column=Column(String(80), nullable=False, index=True))
    topic: str = Field(default="", sa_column=Column(String(255), nullable=False))
    extracted_content: dict = Field(default={}, sa_column=Column(JSON, nullable=False))
    reuse_suggestions: list[dict] = Field(default=[], sa_column=Column(JSON, nullable=False))
    created_at: datetime = Field(default_factory=utcnow, sa_column=Column(DateTime(timezone=True), nullable=False))
    updated_at: datetime = Field(default_factory=utcnow, sa_column=Column(DateTime(timezone=True), nullable=False))
