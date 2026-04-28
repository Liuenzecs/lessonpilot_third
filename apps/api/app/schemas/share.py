"""分享链接 schemas。"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class ShareLinkCreate(BaseModel):
    permission: Literal["read", "comment"] = "read"
    expires_in_days: int | None = Field(default=None, ge=1, le=365)


class ShareLinkRead(BaseModel):
    id: str
    document_id: str
    token: str
    permission: str
    expires_at: datetime | None
    is_active: bool
    url: str
    created_at: datetime


class ShareLinkUpdate(BaseModel):
    is_active: bool | None = None
    permission: Literal["read", "comment"] | None = None
    expires_in_days: int | None = Field(default=None, ge=1, le=365)


class ShareCommentCreate(BaseModel):
    section_name: str | None = None
    body: str = Field(min_length=1, max_length=2000)
    author_name: str = Field(default="匿名用户", max_length=50)


class ShareCommentRead(BaseModel):
    id: str
    section_name: str | None
    body: str
    author_name: str
    resolved: bool
    created_at: datetime


class SharedDocumentView(BaseModel):
    title: str
    subject: str
    grade: str
    topic: str
    doc_type: str
    content: Any
    permission: str
    comments: list[ShareCommentRead] = Field(default_factory=list)
