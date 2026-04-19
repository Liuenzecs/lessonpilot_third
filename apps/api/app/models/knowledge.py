from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON, Column, DateTime, Integer, String, Text
from sqlmodel import Field, SQLModel

from app.models.base import utcnow

KNOWLEDGE_TYPES = (
    "exam_question",
    "character_profile",
    "plot_summary",
    "poetry_analysis",
    "literary_analysis",
    "original_text",
)


class KnowledgeChunk(SQLModel, table=True):
    __tablename__ = "knowledge_chunks"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    domain: str = Field(sa_column=Column(String(80), nullable=False, index=True))
    knowledge_type: str = Field(sa_column=Column(String(50), nullable=False, index=True))
    title: str = Field(sa_column=Column(String(500), nullable=False))
    content: str = Field(sa_column=Column(Text, nullable=False))
    source: str = Field(sa_column=Column(String(255), nullable=False))
    chapter: str | None = Field(default=None, sa_column=Column(String(100)))
    metadata_: dict | None = Field(default=None, sa_column=Column("metadata_", JSON))
    embedding: list[float] | None = Field(
        default=None, sa_column=Column(Vector(1024))
    )
    token_count: int = Field(default=0, sa_column=Column(Integer, nullable=False))
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
