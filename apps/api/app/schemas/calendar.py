"""教学日历 schemas。"""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class SemesterCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    start_date: date
    end_date: date
    grade: str = Field(min_length=1, max_length=80)
    subject: str = Field(default="语文", min_length=1, max_length=80)


class SemesterUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    start_date: date | None = None
    end_date: date | None = None


class SemesterRead(BaseModel):
    id: str
    name: str
    start_date: date
    end_date: date
    grade: str
    subject: str
    week_count: int
    created_at: datetime
    updated_at: datetime


class WeekScheduleRead(BaseModel):
    id: str
    semester_id: str
    week_number: int
    label: str
    start_date: date
    end_date: date
    notes: str | None
    entries: list["LessonScheduleEntryRead"] = Field(default_factory=list)


class WeekScheduleUpdate(BaseModel):
    label: str | None = None
    notes: str | None = None


class LessonScheduleEntryCreate(BaseModel):
    task_id: str
    day_of_week: int = Field(ge=1, le=5)
    class_period: int | None = None
    notes: str | None = None


class LessonScheduleEntryUpdate(BaseModel):
    day_of_week: int | None = Field(default=None, ge=1, le=5)
    class_period: int | None = None
    notes: str | None = None


class LessonScheduleEntryRead(BaseModel):
    id: str
    week_schedule_id: str
    task_id: str
    day_of_week: int
    class_period: int | None
    notes: str | None
    task_title: str = ""
    task_subject: str = ""
    task_grade: str = ""
    created_at: datetime


class SemesterDetailRead(SemesterRead):
    weeks: list[WeekScheduleRead] = Field(default_factory=list)
