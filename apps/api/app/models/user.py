from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, String
from sqlmodel import Field, SQLModel

from app.models.base import utcnow


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    email: str = Field(sa_column=Column(String(255), unique=True, index=True, nullable=False))
    name: str = Field(sa_column=Column(String(120), nullable=False))
    password_hash: str = Field(sa_column=Column(String(255), nullable=False))
    email_verified: bool = Field(default=False, sa_column=Column(Boolean, nullable=False, default=False))
    email_verified_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    role: str = Field(default="teacher", sa_column=Column(String(16), nullable=False, default="teacher"))
    is_disabled: bool = Field(default=False, sa_column=Column(Boolean, nullable=False, default=False))
    disabled_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    disabled_reason: str | None = Field(default=None, sa_column=Column(String(500), nullable=True))
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
