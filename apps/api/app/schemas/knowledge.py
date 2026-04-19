from __future__ import annotations

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
