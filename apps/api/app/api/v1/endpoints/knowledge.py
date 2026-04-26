from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlmodel import Session, select

from app.core.config import get_settings
from app.core.db import get_session
from app.core.security import get_current_user
from app.models.knowledge import KNOWLEDGE_TYPES, KnowledgeChunk
from app.models.user import User
from app.schemas.knowledge import (
    KnowledgeChunkCreate,
    KnowledgeChunkRead,
    KnowledgeDiagnoseQuery,
    KnowledgeDiagnoseResult,
    KnowledgePreviewChunk,
    KnowledgeSearchQuery,
    KnowledgeSearchResult,
)
from app.services.knowledge_service import (
    build_embedding_error_message,
    count_knowledge_chunks,
    estimate_tokens,
    get_embedding_runtime_metadata,
    get_embeddings,
    preview_knowledge_chunks,
    resolve_rag_domain_match,
)

router = APIRouter()


def _build_chunk_metadata(metadata_: dict | None) -> dict:
    merged = dict(metadata_ or {})
    merged["embedding_runtime"] = get_embedding_runtime_metadata()
    return merged


def _build_preview_chunk(chunk: KnowledgeChunk) -> KnowledgePreviewChunk:
    snippet = chunk.content[:160] + "..." if len(chunk.content) > 160 else chunk.content
    return KnowledgePreviewChunk(
        id=chunk.id,
        domain=chunk.domain,
        knowledge_type=chunk.knowledge_type,
        title=chunk.title,
        source=chunk.source,
        chapter=chunk.chapter,
        content_snippet=snippet,
    )


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


@router.post("/diagnose", response_model=KnowledgeDiagnoseResult)
def diagnose_knowledge(
    *,
    session: Session = Depends(get_session),
    _user: User = Depends(get_current_user),
    query: KnowledgeDiagnoseQuery,
) -> KnowledgeDiagnoseResult:
    settings = get_settings()
    if not settings.rag_enabled or settings.rag_trigger_mode == "disabled":
        return KnowledgeDiagnoseResult(
            status="disabled",
            message="知识增强当前已关闭，本次会按普通生成处理。",
        )

    match = resolve_rag_domain_match(query.topic)
    if match is None:
        return KnowledgeDiagnoseResult(
            status="unmatched",
            message="当前课题暂未命中已配置的语文知识包，本次会按普通生成处理。",
        )

    chunk_count = count_knowledge_chunks(session, match.domain)
    if chunk_count == 0:
        return KnowledgeDiagnoseResult(
            status="matched_empty",
            domain=match.domain,
            matched_keywords=match.matched_keywords,
            chunk_count=0,
            message="已命中知识域，但知识库里还没有对应资料，请先导入知识包。",
        )

    preview_chunks = [
        _build_preview_chunk(chunk)
        for chunk in preview_knowledge_chunks(
            session,
            domain=match.domain,
            limit=max(1, min(query.top_k, 8)),
        )
    ]
    return KnowledgeDiagnoseResult(
        status="ready",
        domain=match.domain,
        matched_keywords=match.matched_keywords,
        chunk_count=chunk_count,
        preview_chunks=preview_chunks,
        message=f"已命中“{match.domain}”知识包，生成时会优先参考相关资料。",
    )


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
