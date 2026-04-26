from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class KnowledgeChunkRead(BaseModel):
    id: str
    domain: str
    knowledge_type: str
    title: str
    content: str
    source: str
    chapter: str | None = None
    metadata_: dict | None = None
    token_count: int


class KnowledgeChunkCreate(BaseModel):
    domain: str
    knowledge_type: str
    title: str
    content: str
    source: str
    chapter: str | None = None
    metadata_: dict | None = None


class KnowledgeSearchQuery(BaseModel):
    query: str
    domain: str | None = None
    knowledge_type: str | None = None
    top_k: int = 5


class KnowledgeSearchResult(BaseModel):
    chunk: KnowledgeChunkRead
    similarity_score: float


class KnowledgeDiagnoseQuery(BaseModel):
    topic: str
    requirements: str = ""
    top_k: int = 3


class KnowledgePreviewChunk(BaseModel):
    id: str
    domain: str
    knowledge_type: str
    title: str
    source: str
    chapter: str | None = None
    content_snippet: str


class KnowledgeDiagnoseResult(BaseModel):
    status: Literal["disabled", "unmatched", "matched_empty", "ready", "degraded"]
    domain: str | None = None
    matched_keywords: list[str] = []
    chunk_count: int = 0
    preview_chunks: list[KnowledgePreviewChunk] = []
    message: str
