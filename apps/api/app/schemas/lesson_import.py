from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.content import LessonCategory, LessonPlanContent, Scene
from app.schemas.document import DocumentRead
from app.schemas.task import TaskRead


class ImportWarning(BaseModel):
    severity: Literal["info", "warning"] = "warning"
    section: str | None = None
    message: str


class UnmappedSection(BaseModel):
    title: str | None = None
    content: str


class LessonPlanImportMetadata(BaseModel):
    title: str = Field(default="", max_length=255)
    subject: str = Field(default="语文", min_length=1, max_length=80)
    grade: str = Field(default="", max_length=80)
    topic: str = Field(default="", max_length=255)
    class_hour: int = Field(default=1, ge=1, le=10)
    lesson_category: LessonCategory = "new"
    scene: Scene = "public_school"


class LessonPlanImportPreview(BaseModel):
    source_filename: str
    metadata: LessonPlanImportMetadata
    content: LessonPlanContent
    mapped_sections: list[str] = Field(default_factory=list)
    unmapped_sections: list[UnmappedSection] = Field(default_factory=list)
    warnings: list[ImportWarning] = Field(default_factory=list)


class LessonPlanImportConfirmPayload(BaseModel):
    metadata: LessonPlanImportMetadata
    content: LessonPlanContent


class LessonPlanImportConfirmResponse(BaseModel):
    task: TaskRead
    document: DocumentRead


# ---------------------------------------------------------------------------
# Batch import schemas
# ---------------------------------------------------------------------------


class BatchImportPreview(BaseModel):
    items: list[LessonPlanImportPreview]


class BatchImportConfirmPayload(BaseModel):
    items: list[LessonPlanImportConfirmPayload]


class BatchImportFailure(BaseModel):
    source_filename: str
    error: str


class BatchImportConfirmResponse(BaseModel):
    items: list[LessonPlanImportConfirmResponse] = Field(default_factory=list)
    total: int
    succeeded: int
    failed: int
    failures: list[BatchImportFailure] = Field(default_factory=list)
