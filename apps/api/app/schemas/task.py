from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.content import LessonCategory, LessonType, Scene


class TaskCreatePayload(BaseModel):
    subject: str = Field(min_length=1, max_length=80)
    grade: str = Field(min_length=1, max_length=80)
    topic: str = Field(min_length=1, max_length=255)
    requirements: str | None = Field(default=None, max_length=2000)
    title: str | None = Field(default=None, max_length=255)
    scene: Scene = "public_school"
    lesson_type: LessonType = "lesson_plan"
    class_hour: int = Field(default=1, ge=1, le=10)
    lesson_category: LessonCategory = "new"


class TaskUpdatePayload(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    requirements: str | None = Field(default=None, max_length=2000)
    status: str | None = Field(default=None, max_length=32)


class TaskRead(BaseModel):
    id: str
    title: str
    subject: str
    grade: str
    topic: str
    requirements: str | None
    status: str
    scene: str
    lesson_type: str
    class_hour: int
    lesson_category: str
    created_at: datetime
    updated_at: datetime


class PaginatedTasks(BaseModel):
    items: list[TaskRead]
    page: int
    page_size: int
    total: int


class GenerationStartPayload(BaseModel):
    section_id: str | None = None


class GenerationStartResponse(BaseModel):
    stream_url: str
