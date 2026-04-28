"""教学单元 + 学期备课包 schema。"""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class TeachingUnitCreate(BaseModel):
    name: str = Field(max_length=255)
    order: int = Field(default=1, ge=1)
    topic_overview: str | None = Field(default=None, max_length=2000)


class TeachingUnitUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    order: int | None = Field(default=None, ge=1)
    topic_overview: str | None = Field(default=None, max_length=2000)


class TeachingUnitRead(BaseModel):
    id: str
    semester_id: str
    name: str
    order: int
    topic_overview: str | None = None
    created_at: datetime
    updated_at: datetime


class SemesterPackageRequest(BaseModel):
    doc_types: list[str] = Field(default=["lesson_plan"], max_length=2)
    template_id: str | None = None
    class_group_id: str | None = None
    scene: str = "public_school"


class BatchTaskProgress(BaseModel):
    total: int
    completed: int
    failed: int
    status: str  # "pending" | "running" | "completed" | "failed"
    items: list[dict] = Field(default_factory=list)
