"""Section 级 AI 重写服务。

支持 rewrite / expand / simplify 三种操作，逐 token 流式输出。
SSE 协议与 generation_service 对齐：section_start / section_delta / section_complete。
"""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator

from fastapi import HTTPException, Request, status
from sqlmodel import Session, select

from app.models import Document, Task
from app.schemas.content import (
    DocumentContent,
    LessonPlanContent,
    StudyGuideContent,
)
from app.schemas.document import DocumentRewritePayload
from app.services.generation_service import _get_section_map
from app.services.llm_service import (
    RewriteSectionContext,
    get_provider,
)

logger = logging.getLogger("lessonpilot.rewrite")


def _format_sse(event: str, payload: object) -> str:
    data = json.dumps(payload, ensure_ascii=False) if not isinstance(payload, str) else payload
    return f"event: {event}\ndata: {data}\n\n"


class _ClientDisconnected(Exception):
    pass


async def _ensure_client_connected(request: Request | None) -> None:
    if request is not None and hasattr(request, "is_disconnected") and await request.is_disconnected():
        raise _ClientDisconnected()


# ---------------------------------------------------------------------------
# Section 内容读写工具
# ---------------------------------------------------------------------------


def _get_section_content(content: DocumentContent, section_name: str) -> str:
    """获取某个 section 的当前内容，返回 JSON 字符串。"""
    data = content.model_dump(by_alias=True)
    value = data.get(section_name)
    if value is None:
        return ""
    return json.dumps(value, ensure_ascii=False)


def _set_section_content(
    content: DocumentContent, section_name: str, raw_json: str
) -> DocumentContent:
    """用重写结果替换某个 section 的内容，返回新的 content 对象。"""
    data = content.model_dump(by_alias=True)
    try:
        new_value = json.loads(raw_json)
    except json.JSONDecodeError:
        logger.warning(
            "重写结果 JSON 解析失败 (section=%s)，保留原内容", section_name
        )
        return content
    data[section_name] = new_value
    # 同时将 status 设为 pending
    status_key = f"{section_name}_status"
    if status_key in data:
        data[status_key] = "pending"
    # 根据 doc_type 重新验证
    if data.get("doc_type") == "study_guide":
        return StudyGuideContent.model_validate(data)
    return LessonPlanContent.model_validate(data)


def get_document_task(session: Session, document: Document) -> Task:
    task = session.exec(
        select(Task).where(Task.id == document.task_id, Task.user_id == document.user_id)
    ).first()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


# ---------------------------------------------------------------------------
# 流式重写
# ---------------------------------------------------------------------------


async def stream_rewrite(
    *,
    session: Session,
    document: Document,
    task: Task,
    payload: DocumentRewritePayload,
    request: Request | None = None,
) -> AsyncIterator[str]:
    provider = get_provider()
    section_map = _get_section_map(document.doc_type)
    section_title = section_map.get(payload.section_name, payload.section_name)

    yield _format_sse("status", {"state": "rewriting"})

    try:
        await _ensure_client_connected(request)

        # 解析当前内容
        if document.doc_type == "study_guide":
            content = StudyGuideContent.model_validate(document.content)
        else:
            content = LessonPlanContent.model_validate(document.content)

        current_section_json = _get_section_content(content, payload.section_name)

        ctx = RewriteSectionContext(
            subject=task.subject,
            grade=task.grade,
            topic=task.topic,
            section_name=payload.section_name,
            current_content=current_section_json,
            action=payload.action,
            instruction=payload.instruction or "",
        )

        # 逐 token 流式输出
        yield _format_sse(
            "section_start",
            {"section_name": payload.section_name, "title": section_title},
        )

        chunks: list[str] = []
        async for chunk in provider.rewrite_section(ctx):
            chunks.append(chunk)
            yield _format_sse(
                "section_delta",
                {"section_name": payload.section_name, "delta": chunk},
            )

        raw_json = "".join(chunks)

        yield _format_sse(
            "section_complete",
            {"section_name": payload.section_name},
        )

        # 解析并更新内容
        new_content = _set_section_content(content, payload.section_name, raw_json)
        document.content = new_content.model_dump(by_alias=True)
        session.add(document)
        session.commit()
        session.refresh(document)

        await _ensure_client_connected(request)

        yield _format_sse(
            "document",
            {
                "id": document.id,
                "doc_type": document.doc_type,
                "content": document.content,
                "version": document.version,
            },
        )
        yield _format_sse("status", {"state": "ready"})
        yield _format_sse("done", {"document_id": document.id})

    except _ClientDisconnected:
        return
    except Exception as exc:
        logger.exception("重写失败 (document=%s, section=%s): %s", document.id, payload.section_name, exc)
        yield _format_sse("error", {"message": "重写过程中出现错误，请稍后重试。"})
