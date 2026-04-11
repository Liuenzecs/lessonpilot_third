from __future__ import annotations

import json
from collections.abc import AsyncIterator
from dataclasses import dataclass

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models import Document, Task
from app.schemas.content import Block, ContentDocument, ExerciseGroupBlock, SectionBlock, TeachingStepBlock
from app.schemas.document import DocumentRewritePayload
from app.services.document_service import load_content, save_document, serialize_document
from app.services.llm_service import RewriteContext, apply_suggestion_metadata, get_provider


@dataclass(slots=True)
class BlockLocation:
    block: Block
    siblings: list
    index: int
    section_title: str | None


def _format_sse(event: str, payload: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"


def _get_children(block: Block) -> list[Block]:
    if isinstance(block, (SectionBlock, TeachingStepBlock, ExerciseGroupBlock)):
        return block.children
    return []


def _find_block_location(
    blocks: list[Block],
    target_block_id: str,
    section_title: str | None = None,
) -> BlockLocation | None:
    for index, block in enumerate(blocks):
        current_section_title = section_title
        if isinstance(block, SectionBlock):
            current_section_title = block.title

        if block.id == target_block_id:
            return BlockLocation(
                block=block,
                siblings=blocks,
                index=index,
                section_title=current_section_title,
            )

        children = _get_children(block)
        if children:
            found = _find_block_location(children, target_block_id, current_section_title)
            if found is not None:
                return found
    return None


def _remove_replace_suggestions(blocks: list[Block], target_block_id: str) -> list[Block]:
    next_blocks: list[Block] = []
    for block in blocks:
        suggestion = block.suggestion
        is_targeted_replace = (
            block.status == "pending"
            and suggestion is not None
            and suggestion.kind == "replace"
            and suggestion.target_block_id == target_block_id
        )
        if is_targeted_replace:
            continue

        if isinstance(block, SectionBlock):
            block.children = _remove_replace_suggestions(list(block.children), target_block_id)
        elif isinstance(block, TeachingStepBlock):
            block.children = _remove_replace_suggestions(list(block.children), target_block_id)
        elif isinstance(block, ExerciseGroupBlock):
            block.children = _remove_replace_suggestions(list(block.children), target_block_id)
        next_blocks.append(block)
    return next_blocks


def _validate_rewrite_target(content: ContentDocument, payload: DocumentRewritePayload) -> BlockLocation:
    location = _find_block_location(content.blocks, payload.target_block_id)
    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target block not found")

    if location.block.status != "confirmed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only confirmed blocks can be rewritten",
        )
    if isinstance(location.block, SectionBlock):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Section blocks cannot be rewritten",
        )
    if payload.mode == "selection" and location.block.type != "paragraph":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selection rewrite only supports paragraph blocks",
        )

    return location


def get_document_task(session: Session, document: Document) -> Task:
    task = session.exec(select(Task).where(Task.id == document.task_id, Task.user_id == document.user_id)).first()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


async def stream_rewrite(
    session: Session,
    document: Document,
    task: Task,
    payload: DocumentRewritePayload,
) -> AsyncIterator[str]:
    provider = get_provider()

    yield _format_sse("status", {"state": "rewriting"})
    yield _format_sse(
        "progress",
        {
            "completed": 0,
            "total": 1,
            "target_block_id": payload.target_block_id,
            "action": payload.action,
        },
    )
    yield _format_sse("document", serialize_document(document).model_dump(mode="json", by_alias=True))

    try:
        content = load_content(document)
        location = _validate_rewrite_target(content, payload)
        rewritten_block = await provider.rewrite_block(
            RewriteContext(
                subject=task.subject,
                grade=task.grade,
                topic=task.topic,
                requirements=task.requirements,
                section_title=location.section_title,
                mode=payload.mode,
                action=payload.action,
                target_block_id=payload.target_block_id,
                target_block_type=location.block.type,
                target_block_payload=location.block.model_dump(mode="json", by_alias=True),
                selection_text=payload.selection_text,
            )
        )

        content.blocks = _remove_replace_suggestions(content.blocks, payload.target_block_id)
        location = _validate_rewrite_target(content, payload)
        suggestion_block = apply_suggestion_metadata(
            [rewritten_block],
            kind="replace",
            target_block_id=payload.target_block_id,
            action=payload.action,
        )[0]
        location.siblings.insert(location.index + 1, suggestion_block)
        document = save_document(session, document, content, snapshot_source="rewrite")

        yield _format_sse(
            "progress",
            {
                "completed": 1,
                "total": 1,
                "target_block_id": payload.target_block_id,
                "action": payload.action,
            },
        )
        yield _format_sse("document", serialize_document(document).model_dump(mode="json", by_alias=True))
        yield _format_sse("status", {"state": "ready"})
        yield _format_sse("done", {"document_id": document.id, "target_block_id": payload.target_block_id})
    except Exception as exc:
        yield _format_sse("error", {"message": str(exc)})
