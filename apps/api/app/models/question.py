"""题库模型 — 语文重点篇目分层题库。"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, JSON, String
from sqlmodel import Field, SQLModel


class Question(SQLModel, table=True):
    """分层题库题目。"""

    __tablename__ = "questions"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    chapter: str = Field(sa_column=Column(String, nullable=False, index=True))
    grade: str = Field(sa_column=Column(String, nullable=False))
    question_type: str = Field(sa_column=Column(String, nullable=False))  # choice | fill_blank | short_answer
    difficulty: str = Field(sa_column=Column(String, nullable=False))  # A | B | C | D
    prompt: str = Field(sa_column=Column(String, nullable=False))
    options: list[str] | None = Field(default=None, sa_column=Column(JSON))
    answer: str = Field(sa_column=Column(String, nullable=False, default=""))
    analysis: str = Field(sa_column=Column(String, nullable=False, default=""))
    source: str = Field(sa_column=Column(String, nullable=False, default="原创"))
    tags: list[str] | None = Field(default=None, sa_column=Column(JSON))
    subject: str = Field(sa_column=Column(String, nullable=False, default="语文"))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
