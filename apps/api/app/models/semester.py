"""教学日历模型 — 学期、周计划、排课条目。"""

from __future__ import annotations

from datetime import date, datetime
from uuid import uuid4

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlmodel import Field, SQLModel

from app.models.base import utcnow


class Semester(SQLModel, table=True):
    __tablename__ = "semesters"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(
        sa_column=Column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    )
    name: str = Field(sa_column=Column(String(255), nullable=False))
    start_date: date = Field(sa_column=Column(Date, nullable=False))
    end_date: date = Field(sa_column=Column(Date, nullable=False))
    grade: str = Field(sa_column=Column(String(80), nullable=False))
    subject: str = Field(sa_column=Column(String(80), nullable=False))
    week_count: int = Field(default=20, sa_column=Column(Integer, nullable=False))
    created_at: datetime = Field(default_factory=utcnow, sa_column=Column(DateTime(timezone=True), nullable=False))
    updated_at: datetime = Field(default_factory=utcnow, sa_column=Column(DateTime(timezone=True), nullable=False))


class WeekSchedule(SQLModel, table=True):
    __tablename__ = "week_schedules"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    semester_id: str = Field(
        sa_column=Column(String(36), ForeignKey("semesters.id"), index=True, nullable=False)
    )
    week_number: int = Field(sa_column=Column(Integer, nullable=False))
    label: str = Field(default="", sa_column=Column(String(100), nullable=False))
    start_date: date = Field(sa_column=Column(Date, nullable=False))
    end_date: date = Field(sa_column=Column(Date, nullable=False))
    notes: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    created_at: datetime = Field(default_factory=utcnow, sa_column=Column(DateTime(timezone=True), nullable=False))
    updated_at: datetime = Field(default_factory=utcnow, sa_column=Column(DateTime(timezone=True), nullable=False))


class LessonScheduleEntry(SQLModel, table=True):
    __tablename__ = "lesson_schedule_entries"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    week_schedule_id: str = Field(
        sa_column=Column(String(36), ForeignKey("week_schedules.id"), index=True, nullable=False)
    )
    task_id: str = Field(
        sa_column=Column(String(36), ForeignKey("tasks.id"), index=True, nullable=False)
    )
    day_of_week: int = Field(default=1, sa_column=Column(Integer, nullable=False))
    class_period: int | None = Field(default=None, sa_column=Column(Integer, nullable=True))
    class_group_id: str | None = Field(
        default=None,
        sa_column=Column(String(36), ForeignKey("class_groups.id"), nullable=True, index=True),
    )
    unit_id: str | None = Field(
        default=None,
        sa_column=Column(String(36), ForeignKey("teaching_units.id"), nullable=True, index=True),
    )
    notes: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    created_at: datetime = Field(default_factory=utcnow, sa_column=Column(DateTime(timezone=True), nullable=False))
