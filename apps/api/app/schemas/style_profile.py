from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class TeacherStyleProfileRead(BaseModel):
    id: str | None = None
    enabled: bool = True
    objective_style: str = ""
    process_style: str = ""
    school_wording: str = ""
    activity_preferences: str = ""
    avoid_phrases: str = ""
    sample_count: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None


class TeacherStyleProfileUpdate(BaseModel):
    enabled: bool = True
    objective_style: str = Field(default="", max_length=1200)
    process_style: str = Field(default="", max_length=1200)
    school_wording: str = Field(default="", max_length=1200)
    activity_preferences: str = Field(default="", max_length=1200)
    avoid_phrases: str = Field(default="", max_length=1200)
