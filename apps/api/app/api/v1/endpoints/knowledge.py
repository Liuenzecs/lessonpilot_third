from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlmodel import Session, select

from app.core.db import get_session
from app.core.security import get_current_user
from app.models.knowledge import KNOWLEDGE_TYPES, KnowledgeChunk
from app.models.user import User
from app.schemas.knowledge import (
    KnowledgeChunkCreate,
    KnowledgeChunkRead,
    KnowledgeSearchQuery,
    KnowledgeSearchResult,
)
from app.services.knowledge_service import (
    build_embedding_error_message,
    estimate_tokens,
    get_embedding_runtime_metadata,
    get_embeddings,
)

router = APIRouter()


def _build_chunk_metadata(metadata_: dict | None) -> dict:
    merged = dict(metadata_ or {})
    merged["embedding_runtime"] = get_embedding_runtime_metadata()
    return merged


@router.get("/", response_model=list[KnowledgeChunkRead])
def list_knowledge(
    *,
    session: Session = Depends(get_session),
    _user: User = Depends(get_current_user),
    domain: str | None = None,
    knowledge_type: str | None = None,
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[KnowledgeChunk]:
    stmt = select(KnowledgeChunk)
    if domain:
        stmt = stmt.where(KnowledgeChunk.domain == domain)
    if knowledge_type:
        stmt = stmt.where(KnowledgeChunk.knowledge_type == knowledge_type)
    stmt = stmt.order_by(KnowledgeChunk.created_at.desc()).offset(offset).limit(limit)
    return list(session.exec(stmt).all())


@router.get("/{chunk_id}", response_model=KnowledgeChunkRead)
def get_knowledge(
    *,
    session: Session = Depends(get_session),
    _user: User = Depends(get_current_user),
    chunk_id: str,
) -> KnowledgeChunk:
    chunk = session.exec(
        select(KnowledgeChunk).where(KnowledgeChunk.id == chunk_id)
    ).first()
    if chunk is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge chunk not found")
    return chunk


@router.post("/", response_model=KnowledgeChunkRead, status_code=status.HTTP_201_CREATED)
async def create_knowledge(
    *,
    session: Session = Depends(get_session),
    _user: User = Depends(get_current_user),
    data: KnowledgeChunkCreate,
) -> KnowledgeChunk:
    if data.knowledge_type not in KNOWLEDGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid knowledge_type. Must be one of: {', '.join(KNOWLEDGE_TYPES)}",
        )

    try:
        embeddings = await get_embeddings([data.content], type_="db")
        embedding = embeddings[0]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=build_embedding_error_message(e),
        ) from e

    chunk = KnowledgeChunk(
        domain=data.domain,
        knowledge_type=data.knowledge_type,
        title=data.title,
        content=data.content,
        source=data.source,
        chapter=data.chapter,
        metadata_=_build_chunk_metadata(data.metadata_),
        embedding=embedding,
        token_count=estimate_tokens(data.content),
    )
    session.add(chunk)
    session.commit()
    session.refresh(chunk)
    return chunk


@router.post("/search", response_model=list[KnowledgeSearchResult])
async def search_knowledge(
    *,
    session: Session = Depends(get_session),
    _user: User = Depends(get_current_user),
    query: KnowledgeSearchQuery,
) -> list[KnowledgeSearchResult]:
    try:
        embeddings = await get_embeddings([query.query], type_="query")
        query_embedding = embeddings[0]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=build_embedding_error_message(e),
        ) from e

    embedding_str = "[" + ",".join(str(v) for v in query_embedding) + "]"

    sql = (
        "SELECT *, embedding <=> :query_embedding AS distance "
        "FROM knowledge_chunks "
    )
    conditions = []
    params: dict = {"query_embedding": embedding_str}

    if query.domain:
        conditions.append("domain = :domain")
        params["domain"] = query.domain
    if query.knowledge_type:
        conditions.append("knowledge_type = :knowledge_type")
        params["knowledge_type"] = query.knowledge_type

    if conditions:
        sql += "WHERE " + " AND ".join(conditions) + " "

    sql += "ORDER BY embedding <=> :query_embedding LIMIT :top_k"
    params["top_k"] = query.top_k

    rows = session.exec(text(sql), params=params).all()

    results: list[KnowledgeSearchResult] = []
    for row in rows:
        rd = row._mapping if hasattr(row, "_mapping") else dict(row)
        chunk = KnowledgeChunk(
            id=rd["id"],
            domain=rd["domain"],
            knowledge_type=rd["knowledge_type"],
            title=rd["title"],
            content=rd["content"],
            source=rd["source"],
            chapter=rd.get("chapter"),
            metadata_=rd.get("metadata_"),
            token_count=rd["token_count"],
            created_at=rd["created_at"],
            updated_at=rd["updated_at"],
        )
        results.append(
            KnowledgeSearchResult(
                chunk=KnowledgeChunkRead.model_validate(chunk),
                similarity_score=rd["distance"],
            )
        )
    return results


@router.delete("/{chunk_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_knowledge(
    *,
    session: Session = Depends(get_session),
    _user: User = Depends(get_current_user),
    chunk_id: str,
) -> None:
    chunk = session.exec(
        select(KnowledgeChunk).where(KnowledgeChunk.id == chunk_id)
    ).first()
    if chunk is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge chunk not found")
    session.delete(chunk)
    session.commit()
