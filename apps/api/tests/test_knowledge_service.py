from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock

from app.models.knowledge import KnowledgeChunk
from app.schemas.content import TeachingObjective
from app.services.knowledge_pack_service import load_default_knowledge_pack
from app.services.knowledge_service import (
    estimate_tokens,
    extract_citations,
    format_knowledge_context,
    get_embeddings,
    resolve_rag_domain,
    resolve_rag_domain_match,
    should_trigger_rag,
    strip_citations,
    strip_citations_from_content,
)

# ---------------------------------------------------------------------------
# should_trigger_rag
# ---------------------------------------------------------------------------


def test_should_trigger_rag_match():
    assert should_trigger_rag("红楼梦人物分析") is True
    assert should_trigger_rag("贾宝玉的性格特点") is True
    assert should_trigger_rag("黛玉葬花赏析") is True
    assert should_trigger_rag("春 朱自清 第一课时") is True
    assert should_trigger_rag("桃花源记文言文教学") is True


def test_should_trigger_rag_no_match():
    assert should_trigger_rag("论语十二章") is False
    assert should_trigger_rag("") is False


def test_should_trigger_rag_disabled(monkeypatch):
    monkeypatch.setenv("RAG_ENABLED", "false")
    from app.core.config import get_settings
    get_settings.cache_clear()
    assert should_trigger_rag("红楼梦") is False
    get_settings.cache_clear()


def test_resolve_rag_domain():
    assert resolve_rag_domain("贾宝玉人物分析") == "红楼梦"
    assert resolve_rag_domain("春——朱自清") == "春"
    assert resolve_rag_domain("背影 朱自清") == "背影"


def test_resolve_rag_domain_match_includes_evidence():
    match = resolve_rag_domain_match("岳阳楼记第二课时")

    assert match is not None
    assert match.domain == "岳阳楼记"
    assert match.matched_keywords == ["岳阳楼记"]
    assert match.pack_id == "chinese_literature_core"


def test_default_knowledge_pack_manifest_is_valid():
    pack = load_default_knowledge_pack()

    assert {domain.domain for domain in pack.domains} >= {
        "红楼梦",
        "春",
        "背影",
        "桃花源记",
        "岳阳楼记",
        "天净沙·秋思",
    }
    assert all(entry.domain in pack.domain_map for entry in pack.entries)


# ---------------------------------------------------------------------------
# extract_citations / strip_citations
# ---------------------------------------------------------------------------


def test_extract_citations_single():
    matches = extract_citations("林黛玉多愁善感[cite:abc-123]。")
    assert len(matches) == 1
    assert matches[0].chunk_id == "abc-123"


def test_extract_citations_multiple():
    text = "黛玉[cite:a1]和宝钗[cite:b2]的对比[cite:c3]。"
    matches = extract_citations(text)
    assert len(matches) == 3
    assert [m.chunk_id for m in matches] == ["a1", "b2", "c3"]


def test_extract_citations_none():
    assert extract_citations("没有引用的文本") == []


def test_strip_citations():
    assert strip_citations("林黛玉[cite:abc]多愁善感") == "林黛玉多愁善感"


def test_strip_citations_no_markers():
    assert strip_citations("普通文本") == "普通文本"


# ---------------------------------------------------------------------------
# strip_citations_from_content
# ---------------------------------------------------------------------------


def test_strip_citations_from_content():
    content = {
        "objectives": [
            {"content": "理解黛玉[cite:abc-123]的性格特点"}
        ],
        "key_points": "重点分析[cite:def-456]"
    }
    cleaned, ids = strip_citations_from_content(content)
    assert cleaned["objectives"][0]["content"] == "理解黛玉的性格特点"
    assert cleaned["key_points"] == "重点分析"
    assert set(ids) == {"abc-123", "def-456"}


def test_strip_citations_from_content_empty():
    content = {"text": "无引用内容"}
    cleaned, ids = strip_citations_from_content(content)
    assert cleaned == {"text": "无引用内容"}
    assert ids == []


def test_strip_citations_from_pydantic_content():
    content = {
        "objectives": [
            TeachingObjective(
                dimension="knowledge",
                content="理解人物形象[cite:abc-123]",
            )
        ]
    }

    cleaned, ids = strip_citations_from_content(content)

    assert cleaned["objectives"][0]["content"] == "理解人物形象"
    assert ids == ["abc-123"]


# ---------------------------------------------------------------------------
# format_knowledge_context
# ---------------------------------------------------------------------------


def test_format_knowledge_context_empty():
    assert format_knowledge_context([]) == ""


def test_format_knowledge_context_with_chunks():
    chunks = [
        KnowledgeChunk(
            id="test-001",
            domain="红楼梦",
            knowledge_type="character_profile",
            title="林黛玉人物分析",
            content="林黛玉是红楼梦的女主角之一",
            source="红楼梦人物辞典",
            chapter="全书",
            token_count=20,
        )
    ]
    result = format_knowledge_context(chunks)
    assert "test-001" in result
    assert "林黛玉是红楼梦的女主角之一" in result
    assert "character_profile" in result
    assert "红楼梦人物辞典" in result


# ---------------------------------------------------------------------------
# estimate_tokens
# ---------------------------------------------------------------------------


def test_estimate_tokens():
    assert estimate_tokens("一二三四五六") == 3
    assert estimate_tokens("") == 1


def test_get_embeddings_local_bge(monkeypatch):
    monkeypatch.setenv("EMBEDDING_PROVIDER", "local_bge")
    from app.core.config import get_settings
    get_settings.cache_clear()

    mocked = AsyncMock(return_value=[[0.1, 0.2, 0.3]])
    monkeypatch.setattr(
        "app.services.knowledge_service._get_local_bge_embeddings",
        mocked,
    )
    result = asyncio.run(get_embeddings(["测试文本"]))
    assert result == [[0.1, 0.2, 0.3]]
    mocked.assert_awaited_once()
    get_settings.cache_clear()
