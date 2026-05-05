from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlmodel import Field, SQLModel

from app.models.base import utcnow


class CostLog(SQLModel, table=True):
    __tablename__ = "cost_logs"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False, index=True),
    )
    user_id: str = Field(
        sa_column=Column(String(36), nullable=False, index=True)
    )
    provider: str = Field(sa_column=Column(String(20), nullable=False))
    model: str = Field(sa_column=Column(String(40), nullable=False))
    operation: str = Field(sa_column=Column(String(20), nullable=False))
    prompt_tokens: int = Field(default=0, sa_column=Column(Integer, nullable=False))
    completion_tokens: int = Field(default=0, sa_column=Column(Integer, nullable=False))
    total_tokens: int = Field(default=0, sa_column=Column(Integer, nullable=False))
    cost_cny: float = Field(default=0.0, sa_column=Column(Float, nullable=False))
    task_id: str | None = Field(default=None, sa_column=Column(String(36), nullable=True))
    doc_type: str | None = Field(default=None, sa_column=Column(String(20), nullable=True))
    section_name: str | None = Field(default=None, sa_column=Column(String(40), nullable=True))
    error: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
