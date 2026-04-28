"""题目相关 schema。"""

from __future__ import annotations

from pydantic import BaseModel, Field


class QuestionRead(BaseModel):
    id: str
    chapter: str
    grade: str
    question_type: str
    difficulty: str
    prompt: str
    options: list[str] | None = None
    answer: str = ""
    analysis: str = ""
    source: str = "原创"
    tags: list[str] | None = None
    subject: str = "语文"


class QuestionListResponse(BaseModel):
    items: list[QuestionRead]
    total: int
    limit: int
    offset: int


class QuestionChapterResponse(BaseModel):
    chapter: str


class QuestionSearchParams(BaseModel):
    chapter: str | None = None
    grade: str | None = None
    difficulty: str | None = None
    question_type: str | None = None
    subject: str = "语文"
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


class QuestionSeedResponse(BaseModel):
    inserted: int
