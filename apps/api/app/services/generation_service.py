"""AI 生成服务：流式生成教案/学案。

一次性流式生成完整内容，通过 SSE 推送给前端。
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator

from fastapi import HTTPException, Request, status
from sqlmodel import Session, select

from app.models import Document, Task
from app.schemas.content import (
    DocumentContent,
    LessonPlanContent,
    StudyGuideContent,
    create_empty_lesson_plan,
    create_empty_study_guide,
)
from app.services.llm_service import (
    LessonPlanContext,
    StudyGuideContext,
    get_provider,
)

# ---------------------------------------------------------------------------
# SSE 工具
# ---------------------------------------------------------------------------


def _format_sse(event: str, payload: object) -> str:
    data = json.dumps(payload, ensure_ascii=False) if not isinstance(payload, str) else payload
    return f"event: {event}\ndata: {data}\n\n"


class _ClientDisconnected(Exception):
    pass


async def _ensure_client_connected(request: Request | None) -> None:
    if request is not None and hasattr(request, "is_disconnected") and await request.is_disconnected():
        raise _ClientDisconnected()


# ---------------------------------------------------------------------------
# 流式 JSON 拼装
# ---------------------------------------------------------------------------


async def _assemble_streamed_json(
    stream: AsyncIterator[str],
) -> str:
    """从流式 token 拼装完整 JSON 字符串。"""
    chunks: list[str] = []
    async for chunk in stream:
        chunks.append(chunk)
    return "".join(chunks)


def _parse_content_json(raw: str, doc_type: str) -> DocumentContent:
    """解析 AI 输出的 JSON 为结构化内容模型。"""
    text = raw.strip()
    # 移除 code fence
    if text.startswith("```"):
        lines = text.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)

    data = json.loads(text)
    if doc_type == "study_guide":
        return StudyGuideContent.model_validate(data)
    return LessonPlanContent.model_validate(data)


# ---------------------------------------------------------------------------
# 公共查询
# ---------------------------------------------------------------------------


def get_task_and_documents(
    session: Session, task_id: str, user_id: str
) -> tuple[Task, list[Document]]:
    task = session.exec(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    ).first()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    docs = session.exec(
        select(Document).where(Document.task_id == task_id)
    ).all()
    return task, list(docs)


# ---------------------------------------------------------------------------
# 生成主流程
# ---------------------------------------------------------------------------


async def stream_generation(
    *,
    session: Session,
    task: Task,
    request: Request | None = None,
) -> AsyncIterator[str]:
    """流式生成教案/学案。根据 task.lesson_type 决定生成教案、学案或两者。"""
    provider = get_provider()

    try:
        task.status = "generating"
        session.add(task)
        session.commit()

        yield _format_sse("status", {"status": "generating"})

        doc_types: list[str] = []
        if task.lesson_type in ("lesson_plan", "both"):
            doc_types.append("lesson_plan")
        if task.lesson_type in ("study_guide", "both"):
            doc_types.append("study_guide")

        for idx, doc_type in enumerate(doc_types):
            await _ensure_client_connected(request)

            yield _format_sse(
                "progress",
                {
                    "progress": idx / len(doc_types),
                    "message": f"正在生成{'教案' if doc_type == 'lesson_plan' else '学案'}...",
                },
            )

            doc = _get_or_create_document(session, task, doc_type)

            if doc_type == "lesson_plan":
                ctx = LessonPlanContext(
                    subject=task.subject,
                    grade=task.grade,
                    topic=task.topic,
                    requirements=task.requirements or "",
                    scene=task.scene,
                    class_hour=task.class_hour,
                    lesson_category=task.lesson_category,
                )
                stream = provider.generate_lesson_plan(ctx)
            else:
                ctx = StudyGuideContext(
                    subject=task.subject,
                    grade=task.grade,
                    topic=task.topic,
                    requirements=task.requirements or "",
                    scene=task.scene,
                    class_hour=task.class_hour,
                )
                stream = provider.generate_study_guide(ctx)

            raw_json = await _assemble_streamed_json(stream)

            try:
                content = _parse_content_json(raw_json, doc_type)
            except Exception:
                content = _create_fallback_content(task, doc_type)

            doc.content = content.model_dump(by_alias=True)
            session.add(doc)
            session.commit()
            session.refresh(doc)

            yield _format_sse(
                "progress",
                {
                    "progress": (idx + 1) / len(doc_types),
                    "message": f"{'教案' if doc_type == 'lesson_plan' else '学案'}生成完成",
                },
            )
            yield _format_sse(
                "document",
                {
                    "id": doc.id,
                    "doc_type": doc.doc_type,
                    "content": doc.content,
                    "version": doc.version,
                },
            )

        task.status = "ready"
        session.add(task)
        session.commit()

        yield _format_sse("status", {"status": "ready"})
        yield _format_sse("done", {"message": "生成完成"})

    except _ClientDisconnected:
        task.status = "ready"
        session.add(task)
        session.commit()
        return
    except Exception as exc:
        task.status = "ready"
        session.add(task)
        session.commit()
        yield _format_sse("error", {"message": str(exc)})


# ---------------------------------------------------------------------------
# 内部工具
# ---------------------------------------------------------------------------


def _get_or_create_document(
    session: Session, task: Task, doc_type: str
) -> Document:
    stmt = select(Document).where(
        Document.task_id == task.id,
        Document.doc_type == doc_type,
    )
    doc = session.exec(stmt).first()
    if doc:
        return doc

    content = _create_fallback_content(task, doc_type)
    doc = Document(
        task_id=task.id,
        user_id=task.user_id,
        doc_type=doc_type,
        title=task.title,
        content=content.model_dump(by_alias=True),
    )
    session.add(doc)
    session.commit()
    session.refresh(doc)
    return doc


def _create_fallback_content(task: Task, doc_type: str) -> DocumentContent:
    if doc_type == "study_guide":
        return create_empty_study_guide(
            subject=task.subject,
            grade=task.grade,
            topic=task.topic,
        )
    return create_empty_lesson_plan(
        subject=task.subject,
        grade=task.grade,
        topic=task.topic,
        class_hour=task.class_hour,
        lesson_category=task.lesson_category,
    )
