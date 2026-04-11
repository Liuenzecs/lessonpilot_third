from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.schemas.content import ContentDocument


class DocumentRead(BaseModel):
    id: str
    task_id: str
    user_id: str
    doc_type: str
    title: str
    content: ContentDocument
    version: int
    created_at: datetime
    updated_at: datetime


class DocumentUpdatePayload(BaseModel):
    version: int
    content: ContentDocument


class DocumentListResponse(BaseModel):
    items: list[DocumentRead]

