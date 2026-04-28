"""分享链接模型 — 生成 token-based 链接，支持只读/评论权限。"""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlmodel import Field, SQLModel

from app.models.base import utcnow


class ShareLink(SQLModel, table=True):
    __tablename__ = "share_links"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    document_id: str = Field(
        sa_column=Column(String(36), ForeignKey("documents.id"), index=True, nullable=False)
    )
    owner_id: str = Field(
        sa_column=Column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    )
    token: str = Field(sa_column=Column(String(64), unique=True, index=True, nullable=False))
    permission: str = Field(default="read", sa_column=Column(String(16), nullable=False))
    expires_at: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True), nullable=True))
    is_active: bool = Field(default=True, sa_column=Column(Boolean, nullable=False))
    created_at: datetime = Field(default_factory=utcnow, sa_column=Column(DateTime(timezone=True), nullable=False))
    updated_at: datetime = Field(default_factory=utcnow, sa_column=Column(DateTime(timezone=True), nullable=False))


class ShareComment(SQLModel, table=True):
    __tablename__ = "share_comments"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    share_link_id: str = Field(
        sa_column=Column(String(36), ForeignKey("share_links.id"), index=True, nullable=False)
    )
    user_id: str | None = Field(
        default=None,
        sa_column=Column(String(36), ForeignKey("users.id"), index=True, nullable=True),
    )
    author_name: str = Field(default="匿名用户", sa_column=Column(String(100), nullable=False))
    section_name: str | None = Field(default=None, sa_column=Column(String(64), nullable=True))
    body: str = Field(sa_column=Column(Text, nullable=False))
    resolved: bool = Field(default=False, sa_column=Column(Boolean, nullable=False))
    created_at: datetime = Field(default_factory=utcnow, sa_column=Column(DateTime(timezone=True), nullable=False))
