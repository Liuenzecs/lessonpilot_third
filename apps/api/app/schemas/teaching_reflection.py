"""教学反思 schema。"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class TeachingReflectionCreate(BaseModel):
    goal_achievement: int = Field(default=3, ge=1, le=5)
    difficulty_handling: str | None = Field(default=None, max_length=2000)
    student_response: str | None = Field(default=None, max_length=2000)
    time_feedback: str | None = Field(default=None, max_length=2000)
    improvement_notes: str | None = Field(default=None, max_length=2000)
    free_text: str | None = Field(default=None, max_length=5000)


class TeachingReflectionRead(BaseModel):
    id: str
    task_id: str
    user_id: str
    goal_achievement: int
    difficulty_handling: str | None = None
    student_response: str | None = None
    time_feedback: str | None = None
    improvement_notes: str | None = None
    free_text: str | None = None
    created_at: datetime
    updated_at: datetime
