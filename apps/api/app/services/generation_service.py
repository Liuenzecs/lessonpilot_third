from __future__ import annotations

import json
from collections.abc import AsyncIterator

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models import Document, Task
from app.models.base import utcnow
from app.schemas.content import ContentDocument, SectionBlock
from app.services.document_service import (
    load_content,
    record_current_snapshot,
    save_document,
    serialize_document,
)
from app.services.llm_service import (
    SectionGenerationContext,
    apply_suggestion_metadata,
    get_provider,
)


def _format_sse(event: str, payload: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"


def _find_target_section_ids(content: ContentDocument, section_id: str | None) -> list[str]:
    sections = [block for block in content.blocks if isinstance(block, SectionBlock)]
    if section_id is None:
        return [block.id for block in sections]
    matched = [block.id for block in sections if block.id == section_id]
    if not matched:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section not found")
    return matched


def _find_section(content: ContentDocument, section_id: str) -> SectionBlock:
    for block in content.blocks:
        if isinstance(block, SectionBlock) and block.id == section_id:
            return block
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section not found")


def _replace_pending_children(section: SectionBlock, generated_children) -> None:
    preserved_children = [child for child in section.children if child.status == "confirmed"]
    section.children = [*preserved_children, *generated_children]


def get_task_document(session: Session, task_id: str, user_id: str) -> tuple[Task, Document]:
    task = session.exec(select(Task).where(Task.id == task_id, Task.user_id == user_id)).first()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    document = session.exec(
        select(Document).where(Document.task_id == task_id, Document.user_id == user_id)
    ).first()
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return task, document


async def stream_generation(
    session: Session,
    task: Task,
    document: Document,
    section_id: str | None = None,
) -> AsyncIterator[str]:
    provider = get_provider()
    task.status = "generating"
    task.updated_at = utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)

    yield _format_sse("status", {"state": "generating"})
    yield _format_sse("document", serialize_document(document).model_dump(mode="json", by_alias=True))

    try:
        content = load_content(document)
        target_section_ids = _find_target_section_ids(content, section_id)
        total = len(target_section_ids)

        for index, current_section_id in enumerate(target_section_ids, start=1):
            content = load_content(document)
            section = _find_section(content, current_section_id)
            generated_blocks = await provider.generate_section(
                SectionGenerationContext(
                    subject=task.subject,
                    grade=task.grade,
                    topic=task.topic,
                    requirements=task.requirements,
                    section_title=section.title,
                )
            )
            pending_blocks = apply_suggestion_metadata(generated_blocks, kind="append")
            _replace_pending_children(section, pending_blocks)
            document = save_document(session, document, content)
            yield _format_sse(
                "progress",
                {
                    "completed": index,
                    "total": total,
                    "current_section": section.title,
                    "section_id": section.id,
                },
            )
            yield _format_sse(
                "document",
                serialize_document(document).model_dump(mode="json", by_alias=True),
            )

        task.status = "ready"
        task.updated_at = utcnow()
        session.add(task)
        session.commit()
        session.refresh(task)

        record_current_snapshot(session, document, "generation")
        yield _format_sse("status", {"state": "ready"})
        yield _format_sse("done", {"task_id": task.id, "document_id": document.id})
    except Exception as exc:
        task.status = "ready"
        task.updated_at = utcnow()
        session.add(task)
        session.commit()
        yield _format_sse("error", {"message": str(exc)})
