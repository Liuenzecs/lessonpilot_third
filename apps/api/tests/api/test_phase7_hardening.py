from __future__ import annotations

import asyncio
from uuid import uuid4

from sqlmodel import Session, select

from app.core.db import get_engine
from app.models import Document, Task
from app.schemas.content import ParagraphBlock
from app.services import generation_service, rewrite_service
from app.services.document_service import load_content, save_document


class DisconnectAfterFirstCheckRequest:
    def __init__(self) -> None:
        self._checks = 0

    async def is_disconnected(self) -> bool:
        self._checks += 1
        return self._checks > 1


def _create_task_and_document(client, auth_headers, topic: str):
    create_response = client.post(
        "/api/v1/tasks/",
        headers=auth_headers,
        json={
            "subject": "数学",
            "grade": "八年级",
            "topic": topic,
            "requirements": "Phase 7 测试",
        },
    )
    assert create_response.status_code == 201
    task = create_response.json()
    document = client.get(f"/api/v1/documents/?task_id={task['id']}", headers=auth_headers).json()["items"][0]
    return task, document


def _add_confirmed_paragraph(document_id: str) -> str:
    with Session(get_engine()) as session:
        document = session.get(Document, document_id)
        assert document is not None
        content = load_content(document)
        section = content.blocks[0]
        paragraph = ParagraphBlock(
            id=str(uuid4()),
            status="confirmed",
            source="human",
            content="<p>这是一个可重写的段落。</p>",
        )
        section.children.append(paragraph)
        save_document(session, document, content)
        return paragraph.id


def test_generation_stops_when_client_disconnects(client, auth_headers, monkeypatch):
    task, _ = _create_task_and_document(client, auth_headers, "古诗词鉴赏")

    calls = {"count": 0}

    class FakeProvider:
        async def generate_section(self, _context):
            calls["count"] += 1
            return []

    monkeypatch.setattr(generation_service, "get_provider", lambda: FakeProvider())
    request = DisconnectAfterFirstCheckRequest()

    async def consume() -> list[str]:
        with Session(get_engine()) as session:
            session_task = session.exec(select(Task).where(Task.id == task["id"])).one()
            session_document = session.exec(select(Document).where(Document.task_id == task["id"])).one()
            events: list[str] = []
            async for chunk in generation_service.stream_generation(
                session,
                session_task,
                session_document,
                request=request,
            ):
                events.append(chunk)
            return events

    events = asyncio.run(consume())
    assert calls["count"] == 1
    assert not any("event: done" in event for event in events)


def test_rewrite_stops_when_client_disconnects(client, auth_headers, monkeypatch):
    task, document = _create_task_and_document(client, auth_headers, "一般现在时")
    paragraph_id = _add_confirmed_paragraph(document["id"])

    rewrite_calls = {"count": 0}

    class FakeRewriteProvider:
        async def rewrite_block(self, _context):
            rewrite_calls["count"] += 1
            return ParagraphBlock(
                id=str(uuid4()),
                status="pending",
                source="ai",
                content="<p>AI 重写内容</p>",
            )

    monkeypatch.setattr(rewrite_service, "get_provider", lambda: FakeRewriteProvider())

    async def consume_rewrite() -> list[str]:
        with Session(get_engine()) as session:
            session_task = session.exec(select(Task).where(Task.id == task["id"])).one()
            session_document = session.exec(select(Document).where(Document.task_id == task["id"])).one()
            from app.schemas.document import DocumentRewritePayload

            payload = DocumentRewritePayload(
                document_version=session_document.version,
                mode="block",
                target_block_id=paragraph_id,
                action="rewrite",
            )
            events: list[str] = []
            async for chunk in rewrite_service.stream_rewrite(
                session,
                session_document,
                session_task,
                payload,
                request=DisconnectAfterFirstCheckRequest(),
            ):
                events.append(chunk)
            return events

    rewrite_events = asyncio.run(consume_rewrite())
    assert rewrite_calls["count"] == 1
    assert not any("event: done" in event for event in rewrite_events)
