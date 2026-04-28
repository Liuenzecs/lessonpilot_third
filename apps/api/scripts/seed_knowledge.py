"""导入 LessonPilot 语文知识包。

用法：cd apps/api && python -m scripts.seed_knowledge
"""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlmodel import Session, select

from app.core.db import get_engine
from app.models.knowledge import KnowledgeChunk
from app.services.knowledge_pack_service import (
    KnowledgePack,
    KnowledgePackEntry,
    build_pack_entry_metadata,
    load_default_knowledge_pack,
)
from app.services.knowledge_service import (
    build_embedding_error_message,
    estimate_tokens,
    get_embedding_runtime_metadata,
    get_embeddings,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def _entry_key(entry: KnowledgePackEntry) -> tuple[str, str]:
    return entry.domain, entry.title


def _select_new_entries(
    session: Session,
    pack: KnowledgePack,
) -> list[KnowledgePackEntry]:
    existing = session.exec(select(KnowledgeChunk.domain, KnowledgeChunk.title)).all()
    existing_keys = {(domain, title) for domain, title in existing}
    return [entry for entry in pack.entries if _entry_key(entry) not in existing_keys]


async def _get_embeddings_with_retry(
    texts: list[str],
    *,
    retries: int = 2,
) -> list[list[float]]:
    last_error: Exception | None = None
    for attempt in range(1, retries + 2):
        try:
            return await get_embeddings(texts, type_="db")
        except Exception as exc:  # pragma: no cover - 依赖运行时 provider
            last_error = exc
            logger.warning(
                "Embedding 批量生成失败（第 %d/%d 次）：%s",
                attempt,
                retries + 1,
                build_embedding_error_message(exc),
            )
            if attempt <= retries:
                await asyncio.sleep(min(attempt, 2))

    assert last_error is not None
    raise last_error


async def seed() -> None:
    engine = get_engine()
    runtime = get_embedding_runtime_metadata()
    pack = load_default_knowledge_pack()
    logger.info(
        "当前 embedding 配置：provider=%s model=%s%s",
        runtime["provider"],
        runtime["model"],
        f" device={runtime['device']}" if "device" in runtime else "",
    )
    logger.info("准备导入知识包：%s@%s", pack.pack_id, pack.version)

    with Session(engine) as session:
        new_entries = _select_new_entries(session, pack)

        if not new_entries:
            logger.info("没有新的知识条目需要导入")
            return

        logger.info("需要导入 %d 条新知识条目", len(new_entries))
        batch_size = 10

        for i in range(0, len(new_entries), batch_size):
            batch_entries = new_entries[i : i + batch_size]
            try:
                embeddings = await _get_embeddings_with_retry(
                    [entry.content for entry in batch_entries]
                )
            except Exception as exc:
                logger.error("Embedding 调用失败：%s", build_embedding_error_message(exc))
                logger.info("跳过 batch %d-%d", i, i + len(batch_entries))
                continue

            for entry, embedding in zip(batch_entries, embeddings):
                chunk = KnowledgeChunk(
                    domain=entry.domain,
                    knowledge_type=entry.knowledge_type,
                    title=entry.title,
                    content=entry.content,
                    source=entry.source,
                    chapter=entry.chapter,
                    metadata_=build_pack_entry_metadata(
                        pack=pack,
                        entry=entry,
                        embedding_runtime=runtime,
                    ),
                    embedding=embedding,
                    token_count=estimate_tokens(entry.content),
                )
                session.add(chunk)
                logger.info("  导入: [%s] %s", entry.domain, entry.title)

            session.commit()

        logger.info("导入完成")

    engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
