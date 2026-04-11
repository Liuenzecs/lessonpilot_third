from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String
from sqlmodel import Field, SQLModel

from app.models.base import utcnow


class DocumentSnapshot(SQLModel, table=True):
    __tablename__ = "document_snapshots"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    document_id: str = Field(
        sa_column=Column(String(36), ForeignKey("documents.id"), index=True, nullable=False)
    )
    version: int = Field(default=1, sa_column=Column(Integer, nullable=False))
    content: dict = Field(sa_column=Column(JSON, nullable=False))
    source: str = Field(sa_column=Column(String(32), nullable=False))
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
