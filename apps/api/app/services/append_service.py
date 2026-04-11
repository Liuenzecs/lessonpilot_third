from __future__ import annotations

import json
from collections.abc import AsyncIterator

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models import Document, Task
from app.schemas.content import SectionBlock
from app.schemas.document import DocumentAppendPayload
from app.services.document_service import load_content, save_document, serialize_document
from app.services.llm_service import AppendContext, apply_suggestion_metadata, get_provider


def _format_sse(event: str, payload: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"


def get_document_task(session: Session, document: Document) -> Task:
    task = session.exec(select(Task).where(Task.id == document.task_id, Task.user_id == document.user_id)).first()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


def _find_section(content, section_id: str) -> SectionBlock:
    for block in content.blocks:
        if isinstance(block, SectionBlock) and block.id == section_id:
            return block
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section not found")


async def stream_append(
    session: Session,
    document: Document,
    task: Task,
    payload: DocumentAppendPayload,
) -> AsyncIterator[str]:
    provider = get_provider()

    yield _format_sse("status", {"state": "generating"})
    yield _format_sse(
        "progress",
        {
            "completed": 0,
            "total": 1,
            "current_section": "",
            "section_id": payload.section_id,
        },
    )
    yield _format_sse("document", serialize_document(document).model_dump(mode="json", by_alias=True))

    try:
        content = load_content(document)
        section = _find_section(content, payload.section_id)
        generated_blocks = await provider.generate_append(
            AppendContext(
                subject=task.subject,
                grade=task.grade,
                topic=task.topic,
                requirements=task.requirements,
                section_title=section.title,
                instruction=payload.instruction,
            )
        )
        pending_blocks = apply_suggestion_metadata(generated_blocks, kind="append")
        section.children.extend(pending_blocks)
        document = save_document(session, document, content, snapshot_source="append_ai")

        yield _format_sse(
            "progress",
            {
                "completed": 1,
                "total": 1,
                "current_section": section.title,
                "section_id": section.id,
            },
        )
        yield _format_sse("document", serialize_document(document).model_dump(mode="json", by_alias=True))
        yield _format_sse("status", {"state": "ready"})
        yield _format_sse("done", {"document_id": document.id, "section_id": section.id})
    except Exception as exc:
        yield _format_sse("error", {"message": str(exc)})
