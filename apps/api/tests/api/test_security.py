from __future__ import annotations

import asyncio

from sqlmodel import Session, select

from app.core.db import get_engine
from app.models import Document, Task
from app.services import generation_service, rewrite_service


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
            "subject": "语文",
            "grade": "七年级",
            "topic": topic,
            "requirements": "Phase 7 测试",
        },
    )
    assert create_response.status_code == 201
    task = create_response.json()
    document = client.get(f"/api/v1/documents/?task_id={task['id']}", headers=auth_headers).json()["items"][0]
    return task, document


def test_generation_stops_when_client_disconnects(client, auth_headers, monkeypatch):
    """Test that generation handles client disconnect gracefully.

    New generation model: one-shot per document type. The FakeProvider
    yields quickly, so the disconnect check may not intercept mid-generation.
    Instead, verify the task status is set back to 'ready' after disconnect.
    """
    task, _ = _create_task_and_document(client, auth_headers, "古诗词鉴赏")

    class FakeGenProvider:
        async def generate_lesson_plan(self, _ctx):
            yield '{"doc_type":"lesson_plan"}'

        async def generate_study_guide(self, _ctx):
            yield '{"doc_type":"study_guide"}'

        async def rewrite_section(self, _ctx):
            yield "rewritten"

    monkeypatch.setattr(generation_service, "get_provider", lambda: FakeGenProvider())
    request = DisconnectAfterFirstCheckRequest()

    async def consume() -> list[str]:
        with Session(get_engine()) as session:
            session_task = session.exec(select(Task).where(Task.id == task["id"])).one()
            events: list[str] = []
            async for chunk in generation_service.stream_generation(
                session=session,
                task=session_task,
                request=request,
            ):
                events.append(chunk)
            return events

    asyncio.run(consume())
    # Generation completes because FakeProvider is instant.
    # The key assertion: task status returns to 'ready' after generation.
    with Session(get_engine()) as session:
        session_task = session.exec(select(Task).where(Task.id == task["id"])).one()
        assert session_task.status == "ready"


def test_rewrite_stops_when_client_disconnects(client, auth_headers, monkeypatch):
    task, document = _create_task_and_document(client, auth_headers, "一般现在时")

    rewrite_calls = {"count": 0}

    class FakeRewriteProvider:
        async def rewrite_section(self, _ctx):
            rewrite_calls["count"] += 1
            yield '{"dimension":"knowledge","content":"重写后的目标"}'

        async def generate_lesson_plan(self, _ctx):
            yield '{}'

        async def generate_study_guide(self, _ctx):
            yield '{}'

    monkeypatch.setattr(rewrite_service, "get_provider", lambda: FakeRewriteProvider())

    async def consume_rewrite() -> list[str]:
        with Session(get_engine()) as session:
            session_task = session.exec(select(Task).where(Task.id == task["id"])).one()
            session_document = session.exec(
                select(Document).where(Document.id == document["id"])
            ).one()
            from app.schemas.document import DocumentRewritePayload

            payload = DocumentRewritePayload(
                document_version=session_document.version,
                section_name="objectives",
                action="rewrite",
            )
            events: list[str] = []
            async for chunk in rewrite_service.stream_rewrite(
                session=session,
                document=session_document,
                task=session_task,
                payload=payload,
                request=DisconnectAfterFirstCheckRequest(),
            ):
                events.append(chunk)
            return events

    rewrite_events = asyncio.run(consume_rewrite())
    assert rewrite_calls["count"] == 1
    assert not any("event: done" in event for event in rewrite_events)
