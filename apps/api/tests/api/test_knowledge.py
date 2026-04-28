from __future__ import annotations

from sqlmodel import Session

from app.core.db import get_engine
from app.models.knowledge import KnowledgeChunk
from app.services.knowledge_pack_service import load_default_knowledge_pack
from scripts.seed_knowledge import _select_new_entries


def _insert_chunk(domain: str = "春", title: str | None = None) -> KnowledgeChunk:
    chunk = KnowledgeChunk(
        id="123e4567-e89b-12d3-a456-426614174000",
        domain=domain,
        knowledge_type="literary_analysis",
        title=title or f"{domain}教学主线",
        content=f"{domain}适合围绕朗读、内容梳理和表达方法组织教学。",
        source="测试知识包",
        chapter="测试单元",
        token_count=20,
    )
    with Session(get_engine()) as session:
        session.add(chunk)
        session.commit()
    return chunk


def test_diagnose_knowledge_ready(client, auth_headers):
    _insert_chunk("春")

    response = client.post(
        "/api/v1/knowledge/diagnose",
        headers=auth_headers,
        json={"topic": "春 朱自清 第一课时"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ready"
    assert payload["domain"] == "春"
    assert payload["chunk_count"] == 1
    assert payload["preview_chunks"][0]["title"] == "春教学主线"


def test_diagnose_knowledge_unmatched(client, auth_headers):
    response = client.post(
        "/api/v1/knowledge/diagnose",
        headers=auth_headers,
        json={"topic": "论语十二章"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "unmatched"
    assert payload["domain"] is None


def test_create_knowledge_rejects_unsupported_type(client, auth_headers):
    response = client.post(
        "/api/v1/knowledge/",
        headers=auth_headers,
        json={
            "domain": "春",
            "knowledge_type": "teaching_strategy",
            "title": "非法类型",
            "content": "测试内容",
            "source": "测试",
        },
    )

    assert response.status_code == 400
    assert "Invalid knowledge_type" in response.json()["detail"]


def test_seed_knowledge_pack_skips_existing_domain_title(client, auth_headers):
    pack = load_default_knowledge_pack()
    first_entry = pack.entries[0]
    _insert_chunk(first_entry.domain, first_entry.title)

    with Session(get_engine()) as session:
        new_entries = _select_new_entries(session, pack)

    assert (first_entry.domain, first_entry.title) not in {
        (entry.domain, entry.title) for entry in new_entries
    }
