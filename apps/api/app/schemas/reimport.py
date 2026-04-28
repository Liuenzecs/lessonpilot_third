"""回导 diff & merge schemas。"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class DiffSegment(BaseModel):
    type: Literal["equal", "insert", "delete"]
    text: str


class SectionDiff(BaseModel):
    section_name: str
    section_title: str
    status: Literal["unchanged", "modified", "new", "deleted"]
    original_content: Any | None = None
    imported_content: Any | None = None
    diff_segments: list[DiffSegment] | None = None


class ReimportPreview(BaseModel):
    source_filename: str
    original_document_id: str
    original_version: int
    sections: list[SectionDiff] = Field(default_factory=list)


class ReimportMergePayload(BaseModel):
    sections_to_accept: list[str] = Field(default_factory=list)
    sections_to_reject: list[str] = Field(default_factory=list)
    document_version: int
