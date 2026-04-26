from __future__ import annotations

import json

from sqlmodel import Session

from app.core.db import get_engine
from app.models.knowledge import KnowledgeChunk
from app.services import generation_service, rewrite_service


def _parse_sse_events(raw_text: str) -> list[tuple[str, dict]]:
    events: list[tuple[str, dict]] = []
    for chunk in raw_text.strip().split("\n\n"):
        if not chunk.strip():
            continue
        event_name = ""
        data_payload = ""
        for line in chunk.splitlines():
            if line.startswith("event: "):
                event_name = line.removeprefix("event: ").strip()
            if line.startswith("data: "):
                data_payload = line.removeprefix("data: ").strip()
        if event_name and data_payload:
            events.append((event_name, json.loads(data_payload)))
    return events


def _create_task_and_document(client, auth_headers):
    create_response = client.post(
        "/api/v1/tasks/",
        headers=auth_headers,
        json={
            "subject": "语文",
            "grade": "七年级",
            "topic": "春",
            "requirements": "侧重朗读训练",
        },
    )
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]
    document_response = client.get(f"/api/v1/documents/?task_id={task_id}", headers=auth_headers)
    document = document_response.json()["items"][0]
    return task_id, document


def test_generation_produces_lesson_plan_content(client, auth_headers):
    task_id, document = _create_task_and_document(client, auth_headers)

    start_response = client.post(
        f"/api/v1/tasks/{task_id}/generate",
        headers=auth_headers,
        json={},
    )
    stream_url = start_response.json()["stream_url"]

    with client.stream("GET", stream_url, headers=auth_headers) as stream_response:
        payload = "".join(stream_response.iter_text())
    events = _parse_sse_events(payload)
    assert events[-1][0] == "document_done"
    assert len([item for item in events if item[0] == "section_document"]) == 6
    rag_events = [item for item in events if item[0] == "rag_status"]
    assert rag_events[0][1]["status"] == "matched_empty"

    refreshed = client.get(f"/api/v1/documents/{document['id']}", headers=auth_headers).json()
    content = refreshed["content"]
    assert content["doc_type"] == "lesson_plan"
    assert len(content["objectives"]) > 0
    assert len(content["teaching_process"]) > 0


def test_generation_rag_status_ready_and_section_references(client, auth_headers, monkeypatch):
    chunk_id = "123e4567-e89b-12d3-a456-426614174111"
    chunk = KnowledgeChunk(
        id=chunk_id,
        domain="红楼梦",
        knowledge_type="character_profile",
        title="薛宝钗人物分析",
        content="薛宝钗端庄稳重，适合与林黛玉进行人物对比教学。",
        source="测试知识包",
        chapter="全书",
        token_count=20,
    )
    with Session(get_engine()) as session:
        session.add(chunk)
        session.commit()

    async def fake_retrieve_knowledge(*_args, **_kwargs):
        return [
            KnowledgeChunk(
                id=chunk_id,
                domain="红楼梦",
                knowledge_type="character_profile",
                title="薛宝钗人物分析",
                content="薛宝钗端庄稳重，适合与林黛玉进行人物对比教学。",
                source="测试知识包",
                chapter="全书",
                token_count=20,
            )
        ]

    monkeypatch.setattr(generation_service, "retrieve_knowledge", fake_retrieve_knowledge)

    create_response = client.post(
        "/api/v1/tasks/",
        headers=auth_headers,
        json={
            "subject": "语文",
            "grade": "七年级",
            "topic": "红楼梦薛宝钗人物分析",
            "requirements": "强调人物对比",
        },
    )
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    start_response = client.post(
        f"/api/v1/tasks/{task_id}/generate",
        headers=auth_headers,
        json={},
    )

    with client.stream("GET", start_response.json()["stream_url"], headers=auth_headers) as resp:
        events = _parse_sse_events("".join(resp.iter_text()))

    rag_events = [item for item in events if item[0] == "rag_status"]
    citation_events = [item for item in events if item[0] == "citations"]
    assert rag_events[0][1]["status"] == "ready"
    assert rag_events[0][1]["domain"] == "红楼梦"
    assert citation_events

    documents_response = client.get(f"/api/v1/documents/?task_id={task_id}", headers=auth_headers)
    content = documents_response.json()["items"][0]["content"]
    assert content["section_references"]["objectives"][0]["title"] == "薛宝钗人物分析"


def test_section_rewrite_flow(client, auth_headers):
    _, document = _create_task_and_document(client, auth_headers)

    # 先生成内容
    task_id = document["task_id"]
    start_response = client.post(
        f"/api/v1/tasks/{task_id}/generate",
        headers=auth_headers,
        json={},
    )
    with client.stream("GET", start_response.json()["stream_url"], headers=auth_headers) as resp:
        "".join(resp.iter_text())

    refreshed = client.get(f"/api/v1/documents/{document['id']}", headers=auth_headers).json()

    # Section 级重写
    rewrite_start = client.post(
        f"/api/v1/documents/{refreshed['id']}/rewrite",
        headers=auth_headers,
        json={
            "document_version": refreshed["version"],
            "section_name": "objectives",
            "action": "rewrite",
        },
    )
    assert rewrite_start.status_code == 200

    with client.stream("GET", rewrite_start.json()["stream_url"], headers=auth_headers) as resp:
        events = _parse_sse_events("".join(resp.iter_text()))
    assert events[-1][0] == "document_done"
    assert "section_document" in [event_name for event_name, _ in events]


def test_empty_objectives_rewrite_uses_section_generation(client, auth_headers, monkeypatch):
    _, document = _create_task_and_document(client, auth_headers)
    calls: dict[str, str] = {}

    class EmptySectionProvider:
        async def generate_document_section(self, ctx):
            calls["generated"] = ctx.section_name
            yield (
                '[{"dimension":"知识与技能","content":"理解课文内容"},'
                '{"dimension":"能力","content":"概括文章结构"},'
                '{"dimension":"情感态度与价值观","content":"感受作品情感"}]'
            )

        async def rewrite_section(self, _ctx):
            calls["rewritten"] = "true"
            yield "[]"

    monkeypatch.setattr(rewrite_service, "get_provider", lambda: EmptySectionProvider())

    rewrite_start = client.post(
        f"/api/v1/documents/{document['id']}/rewrite",
        headers=auth_headers,
        json={
            "document_version": document["version"],
            "section_name": "objectives",
            "action": "rewrite",
        },
    )
    assert rewrite_start.status_code == 200

    with client.stream("GET", rewrite_start.json()["stream_url"], headers=auth_headers) as resp:
        events = _parse_sse_events("".join(resp.iter_text()))

    refreshed = client.get(f"/api/v1/documents/{document['id']}", headers=auth_headers).json()
    assert events[-1][0] == "document_done"
    assert calls["generated"] == "objectives"
    assert "rewritten" not in calls
    assert len(refreshed["content"]["objectives"]) == 3
    assert refreshed["content"]["objectives"][0]["dimension"] == "knowledge"


def test_empty_reflection_rewrite_generates_draft(client, auth_headers, monkeypatch):
    _, document = _create_task_and_document(client, auth_headers)
    captured: dict[str, str] = {}

    class ReflectionProvider:
        async def generate_document_section(self, ctx):
            captured["rules"] = ctx.section_rules
            yield '"本节目标整体达成较好，但对重点问题的追问还可以更深入。后续可增加学生复盘与迁移练习。"'  # noqa: E501

        async def rewrite_section(self, _ctx):
            yield '""'

    monkeypatch.setattr(rewrite_service, "get_provider", lambda: ReflectionProvider())

    rewrite_start = client.post(
        f"/api/v1/documents/{document['id']}/rewrite",
        headers=auth_headers,
        json={
            "document_version": document["version"],
            "section_name": "reflection",
            "action": "rewrite",
        },
    )
    assert rewrite_start.status_code == 200

    with client.stream("GET", rewrite_start.json()["stream_url"], headers=auth_headers) as resp:
        events = _parse_sse_events("".join(resp.iter_text()))

    refreshed = client.get(f"/api/v1/documents/{document['id']}", headers=auth_headers).json()
    assert events[-1][0] == "document_done"
    assert "反思草稿" in captured["rules"]
    assert refreshed["content"]["reflection"] != ""


def test_history_and_restore(client, auth_headers):
    _, document = _create_task_and_document(client, auth_headers)

    # 多次更新文档以产生历史
    current_document = document
    for _ in range(12):
        content = current_document["content"]
        content["objectives_status"] = "confirmed"
        patch_response = client.patch(
            f"/api/v1/documents/{current_document['id']}",
            headers=auth_headers,
            json={"version": current_document["version"], "content": content},
        )
        assert patch_response.status_code == 200
        current_document = patch_response.json()

    history_response = client.get(
        f"/api/v1/documents/{current_document['id']}/history?limit=10",
        headers=auth_headers,
    )
    assert history_response.status_code == 200
    history_items = history_response.json()["items"]
    assert len(history_items) == 10
    assert history_items[0]["version"] == current_document["version"]

    # 恢复快照
    snapshot_id = history_items[-1]["id"]
    restored = client.post(
        f"/api/v1/documents/{current_document['id']}/history/{snapshot_id}/restore",
        headers=auth_headers,
    )
    assert restored.status_code == 200
    assert restored.json()["version"] > current_document["version"]

    latest_history = client.get(
        f"/api/v1/documents/{current_document['id']}/history?limit=1",
        headers=auth_headers,
    ).json()["items"][0]
    assert latest_history["source"] == "restore"
