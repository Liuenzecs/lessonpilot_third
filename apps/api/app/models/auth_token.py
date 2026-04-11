from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlmodel import Field, SQLModel

from app.models.base import utcnow


class AuthToken(SQLModel, table=True):
    __tablename__ = "auth_tokens"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(sa_column=Column(String(36), ForeignKey("users.id"), index=True, nullable=False))
    token_hash: str = Field(sa_column=Column(String(128), unique=True, index=True, nullable=False))
    token_type: str = Field(sa_column=Column(String(32), index=True, nullable=False))
    expires_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    used_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
