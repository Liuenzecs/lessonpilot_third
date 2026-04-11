from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator

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


class DocumentRewritePayload(BaseModel):
    document_version: int = Field(alias="document_version")
    mode: Literal["block", "selection"]
    target_block_id: str = Field(alias="target_block_id")
    action: Literal["rewrite", "polish", "expand"]
    selection_text: str | None = Field(default=None, alias="selection_text")

    model_config = {"populate_by_name": True}

    @model_validator(mode="after")
    def validate_selection_text(self) -> "DocumentRewritePayload":
        if self.mode == "selection" and not (self.selection_text or "").strip():
            raise ValueError("selection_text is required for selection rewrite mode")
        return self


class DocumentRewriteStartResponse(BaseModel):
    stream_url: str


class DocumentAppendPayload(BaseModel):
    document_version: int
    section_id: str = Field(min_length=1, max_length=64)
    instruction: str = Field(min_length=1, max_length=2000)


class DocumentAppendStartResponse(BaseModel):
    stream_url: str


class DocumentSnapshotRead(BaseModel):
    id: str
    document_id: str
    version: int
    content: ContentDocument
    source: str
    created_at: datetime


class DocumentHistoryResponse(BaseModel):
    items: list[DocumentSnapshotRead]


class DocumentListResponse(BaseModel):
    items: list[DocumentRead]
