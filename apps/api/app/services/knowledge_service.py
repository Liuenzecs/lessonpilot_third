"""RAG 知识检索服务：embedding + 向量检索 + 引用处理。"""

from __future__ import annotations

import asyncio
import logging
import re
from dataclasses import dataclass
from functools import lru_cache

import httpx
from sqlalchemy import text
from sqlmodel import Session, select

from app.core.config import get_settings
from app.models.knowledge import KnowledgeChunk

logger = logging.getLogger("lessonpilot.knowledge")


_RAG_RULES: tuple[dict[str, tuple[str, ...]], ...] = (
    {
        "domain": "红楼梦",
        "keywords": (
            "红楼梦",
            "石头记",
            "贾宝玉",
            "林黛玉",
            "薛宝钗",
            "王熙凤",
            "贾母",
            "刘姥姥",
            "大观园",
            "金陵十二钗",
            "曹雪芹",
            "黛玉葬花",
            "宝玉挨打",
            "葫芦僧",
            "抄检大观园",
            "元春",
            "迎春",
            "探春",
            "惜春",
            "史湘云",
            "妙玉",
            "秦可卿",
            "李纨",
            "巧姐",
            "晴雯",
            "袭人",
            "紫鹃",
            "薛蟠",
            "贾政",
            "贾赦",
            "王夫人",
            "贾琏",
            "平儿",
        ),
    },
)

_CITE_PATTERN = re.compile(r"\[cite:([a-f0-9\-]+)\]")


@dataclass(slots=True)
class CitationMatch:
    chunk_id: str
    position: int


@dataclass(slots=True)
class CitationInfo:
    chunk_id: str
    source: str
    title: str
    knowledge_type: str
    chapter: str | None
    content_snippet: str


def extract_citations(raw: str) -> list[CitationMatch]:
    """从文本中提取所有 [cite:chunk_id] 标记。"""
    return [
        CitationMatch(chunk_id=match.group(1), position=match.start())
        for match in _CITE_PATTERN.finditer(raw)
    ]


def strip_citations(text: str) -> str:
    """移除文本中的所有 [cite:...] 标记。"""
    return _CITE_PATTERN.sub("", text)


def strip_citations_from_content(content: dict) -> tuple[dict, list[str]]:
    """递归移除 content dict 中所有字符串值的引用标记。"""
    chunk_ids: set[str] = set()
    cleaned = _strip_recursive(content, chunk_ids)
    return cleaned, list(chunk_ids)


def _strip_recursive(obj: object, chunk_ids: set[str]) -> object:
    if isinstance(obj, str):
        matches = extract_citations(obj)
        chunk_ids.update(match.chunk_id for match in matches)
        return strip_citations(obj)
    if isinstance(obj, list):
        return [_strip_recursive(item, chunk_ids) for item in obj]
    if isinstance(obj, dict):
        return {key: _strip_recursive(value, chunk_ids) for key, value in obj.items()}
    return obj


def resolve_rag_domain(topic: str) -> str | None:
    """根据 topic 命中知识域。"""
    settings = get_settings()
    if not settings.rag_enabled or settings.rag_trigger_mode == "disabled":
        return None
    if settings.rag_trigger_mode == "always":
        return _RAG_RULES[0]["domain"] if _RAG_RULES else None
    for rule in _RAG_RULES:
        if any(keyword in topic for keyword in rule["keywords"]):
            return rule["domain"]
    return None


def should_trigger_rag(topic: str) -> bool:
    return resolve_rag_domain(topic) is not None


@lru_cache(maxsize=4)
def _get_local_bge_model(model_name: str, device: str):
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:  # pragma: no cover - depends on local runtime
        raise RuntimeError(
            "本地 embedding 依赖未安装，请先安装 sentence-transformers。"
        ) from exc
    return SentenceTransformer(model_name, device=device)


def _encode_local_bge_sync(
    texts: tuple[str, ...],
    *,
    model_name: str,
    device: str,
) -> list[list[float]]:
    model = _get_local_bge_model(model_name, device)
    vectors = model.encode(
        list(texts),
        batch_size=min(16, max(1, len(texts))),
        normalize_embeddings=True,
    )
    return [vector.tolist() for vector in vectors]


async def _get_local_bge_embeddings(texts: list[str]) -> list[list[float]]:
    settings = get_settings()
    return await asyncio.to_thread(
        _encode_local_bge_sync,
        tuple(texts),
        model_name=settings.embedding_model,
        device=settings.embedding_device,
    )


async def _get_minimax_embeddings(texts: list[str], *, type_: str) -> list[list[float]]:
    settings = get_settings()
    url = f"{settings.minimax_base_url}/embeddings"
    payload = {
        "model": settings.minimax_embedding_model,
        "texts": texts,
        "type": type_,
    }
    headers = {"Authorization": f"Bearer {settings.minimax_api_key}"}

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

    return [item["embedding"] for item in data["data"]]


async def get_embeddings(
    texts: list[str],
    *,
    type_: str = "db",
) -> list[list[float]]:
    """根据 embedding_provider 获取向量。"""
    settings = get_settings()
    if not texts:
        return []
    if settings.embedding_provider == "minimax":
        return await _get_minimax_embeddings(texts, type_=type_)
    return await _get_local_bge_embeddings(texts)


def get_embedding_runtime_metadata() -> dict[str, str]:
    """返回当前 embedding 运行时配置，用于写入知识元数据。"""
    settings = get_settings()
    if settings.embedding_provider == "minimax":
        model_name = settings.minimax_embedding_model
        return {
            "provider": settings.embedding_provider,
            "model": model_name,
            "version": f"{settings.embedding_provider}:{model_name}",
        }

    model_name = settings.embedding_model
    return {
        "provider": settings.embedding_provider,
        "model": model_name,
        "device": settings.embedding_device,
        "version": f"{settings.embedding_provider}:{model_name}",
    }


def build_embedding_error_message(exc: Exception) -> str:
    """根据当前 provider 构造老师/运维可读的 embedding 错误提示。"""
    settings = get_settings()
    if settings.embedding_provider == "local_bge":
        if isinstance(exc, RuntimeError):
            return (
                "本地 embedding 初始化失败，请确认已安装 sentence-transformers，"
                f"并且模型 {settings.embedding_model} 可在当前环境加载。"
            )
        return "本地 embedding 生成失败，请检查模型依赖、CPU 环境与日志。"

    return "MiniMax embedding 调用失败，请检查 API key、按量余额和 embedding 接口权限。"


async def retrieve_knowledge(
    session: Session,
    *,
    topic: str,
    requirements: str = "",
    max_tokens: int = 3000,
    top_k: int = 8,
    domain: str | None = None,
) -> list[KnowledgeChunk]:
    """基于 topic + requirements 进行向量检索，返回最相关的知识片段。"""
    target_domain = domain or resolve_rag_domain(topic)
    if not target_domain:
        return []

    query_text = f"{topic} {requirements}".strip()
    try:
        query_embedding = (await get_embeddings([query_text], type_="query"))[0]
    except Exception:
        logger.warning("Embedding 调用失败，跳过 RAG 检索", exc_info=True)
        return []

    embedding_str = "[" + ",".join(str(value) for value in query_embedding) + "]"
    raw_results = session.exec(
        text(
            "SELECT *, embedding <=> :query_embedding AS distance "
            "FROM knowledge_chunks "
            "WHERE domain = :domain "
            "ORDER BY embedding <=> :query_embedding "
            "LIMIT :top_k"
        ),
        params={
            "domain": target_domain,
            "query_embedding": embedding_str,
            "top_k": top_k,
        },
    ).all()

    chunks: list[KnowledgeChunk] = []
    total_tokens = 0
    for row in raw_results:
        chunk = _row_to_chunk(row)
        if total_tokens + chunk.token_count > max_tokens:
            break
        chunks.append(chunk)
        total_tokens += chunk.token_count
    return chunks


def _row_to_chunk(row: object) -> KnowledgeChunk:
    row_dict = row._mapping if hasattr(row, "_mapping") else dict(row)
    return KnowledgeChunk(
        id=row_dict["id"],
        domain=row_dict["domain"],
        knowledge_type=row_dict["knowledge_type"],
        title=row_dict["title"],
        content=row_dict["content"],
        source=row_dict["source"],
        chapter=row_dict.get("chapter"),
        metadata_=row_dict.get("metadata_"),
        token_count=row_dict["token_count"],
        created_at=row_dict["created_at"],
        updated_at=row_dict["updated_at"],
    )


def format_knowledge_context(chunks: list[KnowledgeChunk]) -> str:
    """将检索到的知识片段格式化为 prompt 注入文本。"""
    if not chunks:
        return ""
    lines = [
        "## 参考资料",
        "",
        "以下是根据课题检索到的相关参考资料，请在生成内容时优先参考。",
        "如引用，请在内容对应位置标注 [cite:资料ID]。",
        "",
    ]
    for chunk in chunks:
        lines.append(f"[资料] ID: {chunk.id}")
        lines.append(f"来源：{chunk.source}")
        lines.append(f"类型：{chunk.knowledge_type}")
        if chunk.chapter:
            lines.append(f"章节：{chunk.chapter}")
        lines.append(f"内容：{chunk.content}")
        lines.append("")
    return "\n".join(lines)


def build_citation_metadata(
    chunk_ids: list[str],
    session: Session,
) -> list[CitationInfo]:
    """根据 chunk_id 列表查询引用元数据。"""
    if not chunk_ids:
        return []
    chunks = session.exec(
        select(KnowledgeChunk).where(KnowledgeChunk.id.in_(chunk_ids))
    ).all()
    chunk_map = {chunk.id: chunk for chunk in chunks}
    result: list[CitationInfo] = []
    for chunk_id in chunk_ids:
        chunk = chunk_map.get(chunk_id)
        if chunk is None:
            continue
        snippet = (
            chunk.content[:200] + "..."
            if len(chunk.content) > 200
            else chunk.content
        )
        result.append(
            CitationInfo(
                chunk_id=chunk.id,
                source=chunk.source,
                title=chunk.title,
                knowledge_type=chunk.knowledge_type,
                chapter=chunk.chapter,
                content_snippet=snippet,
            )
        )
    return result


def estimate_tokens(text: str) -> int:
    """中文文本 token 估算（1 token ≈ 1.5 字）。"""
    return max(1, len(text) // 2)
