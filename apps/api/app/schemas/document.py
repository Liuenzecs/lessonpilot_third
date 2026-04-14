from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.content import DocumentContent


class DocumentRead(BaseModel):
    id: str
    task_id: str
    user_id: str
    doc_type: Literal["lesson_plan", "study_guide"]
    title: str
    content: DocumentContent
    version: int
    created_at: datetime
    updated_at: datetime


class DocumentUpdatePayload(BaseModel):
    version: int
    content: DocumentContent


class DocumentRewritePayload(BaseModel):
    """Section 级重写请求。"""

    document_version: int
    section_name: str = Field(
        description="要重写的 section 名称，如 objectives/teaching_process 等"
    )
    action: Literal["rewrite", "expand", "simplify"] = "rewrite"
    instruction: str | None = Field(
        default=None, max_length=1000, description="老师的额外指示"
    )


class DocumentRewriteStartResponse(BaseModel):
    stream_url: str


class DocumentSnapshotRead(BaseModel):
    id: str
    document_id: str
    version: int
    content: DocumentContent
    source: str
    created_at: datetime


class DocumentHistoryResponse(BaseModel):
    items: list[DocumentSnapshotRead]


class DocumentListResponse(BaseModel):
    items: list[DocumentRead]
