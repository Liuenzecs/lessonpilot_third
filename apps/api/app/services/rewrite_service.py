"""Section 级 AI 重写服务。"""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator

from fastapi import HTTPException, Request, status
from sqlmodel import Session, select

from app.core.config import get_settings
from app.models import Document, Task
from app.services.cost_tracker import log_llm_usage
from app.schemas.content import (
    LessonPlanContent,
    StudyGuideContent,
)
from app.schemas.document import DocumentRewritePayload
from app.services.document_service import _create_snapshot
from app.services.generation_service import (
    _apply_citations_to_section,
    _get_section_map,
    _get_section_specs,
    _get_section_value,
    _load_prompt_hints,
    _parse_section_value,
    _section_has_content,
    _set_section_value,
    _summarize_completed_sections,
    _validate_section_value,
)
from app.services.llm_service import (
    RewriteSectionContext,
    SectionGenerationContext,
    get_provider,
)
from app.services.sse_utils import ClientDisconnected, ensure_client_connected, format_sse
from app.services.style_profile_service import get_teacher_style_context

logger = logging.getLogger("lessonpilot.rewrite")


# SSE utilities imported from sse_utils: format_sse, ClientDisconnected, ensure_client_connected


def _get_empty_section_generation_rules(
    section_name: str,
    section_spec: dict[str, object],
) -> str:
    if section_name == "reflection":
        return "老师显式点击生成该教学反思时，请输出 2-3 句可编辑的反思草稿，围绕目标达成、难点处理和后续改进建议展开。"
    if section_name == "self_reflection":
        return (
            "老师显式点击生成该自主反思时，请输出 2-3 句可编辑的学生反思提示，"
            "帮助学生回顾收获、困难与下一步改进方向。"
        )
    return str(section_spec["rules"])


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
    section_specs = {
        item["name"]: item for item in _get_section_specs(document.doc_type)
    }
    section_spec = section_specs.get(payload.section_name)
    if section_spec is None:
        raise HTTPException(status_code=400, detail="Unknown section name")

    yield format_sse("status", {"state": "rewriting"})

    try:
        await ensure_client_connected(request)

        # 解析当前内容
        if document.doc_type == "study_guide":
            content = StudyGuideContent.model_validate(document.content)
        else:
            content = LessonPlanContent.model_validate(document.content)

        current_section_value = _get_section_value(content, payload.section_name)
        current_section_json = json.dumps(current_section_value, ensure_ascii=False)
        prompt_hints = _load_prompt_hints(session, task.template_id, document.doc_type)
        teacher_style_ctx = get_teacher_style_context(session, task.user_id)
        if teacher_style_ctx:
            prompt_hints = "\n\n".join(part for part in (prompt_hints, teacher_style_ctx) if part)
        should_generate_from_scratch = (
            payload.action == "rewrite" and not _section_has_content(current_section_value)
        )
        can_generate_from_scratch = hasattr(provider, "generate_document_section")

        # 逐 token 流式输出
        yield format_sse(
            "section_start",
            {"section_name": payload.section_name, "title": section_title},
        )

        chunks: list[str] = []
        if should_generate_from_scratch and can_generate_from_scratch:
            generation_ctx = SectionGenerationContext(
                doc_type=document.doc_type,
                subject=task.subject,
                grade=task.grade,
                topic=task.topic,
                requirements=task.requirements or "",
                scene=task.scene,
                class_hour=task.class_hour,
                lesson_category=task.lesson_category,
                prompt_hints=prompt_hints,
                knowledge_context="",
                section_name=payload.section_name,
                section_title=section_title,
                section_schema=str(section_spec["schema"]),
                existing_sections=_summarize_completed_sections(content),
                section_rules=_get_empty_section_generation_rules(payload.section_name, section_spec),
            )
            async for chunk in provider.generate_document_section(generation_ctx):
                chunks.append(chunk)
                yield format_sse(
                    "section_delta",
                    {"section_name": payload.section_name, "delta": chunk},
                )
        else:
            rewrite_ctx = RewriteSectionContext(
                subject=task.subject,
                grade=task.grade,
                topic=task.topic,
                section_name=payload.section_name,
                current_content=current_section_json,
                action=payload.action,
                instruction=payload.instruction or "",
            )
            if teacher_style_ctx:
                rewrite_ctx.instruction = "\n\n".join(
                    part for part in (rewrite_ctx.instruction, teacher_style_ctx) if part
                )
            async for chunk in provider.rewrite_section(rewrite_ctx):
                chunks.append(chunk)
                yield format_sse(
                    "section_delta",
                    {"section_name": payload.section_name, "delta": chunk},
                )

        raw_json = "".join(chunks)

        # Track LLM usage / cost
        settings = get_settings()
        if settings.cost_tracking_enabled:
            usage = provider.get_last_usage()
            if usage and usage.total_tokens > 0:
                try:
                    log_llm_usage(
                        session=session,
                        user_id=task.user_id,
                        provider=settings.llm_provider,
                        model=settings.deepseek_model if settings.llm_provider == "deepseek" else settings.minimax_model,
                        operation="rewrite_section",
                        prompt_tokens=usage.prompt_tokens,
                        completion_tokens=usage.completion_tokens,
                        total_tokens=usage.total_tokens,
                        task_id=task.id,
                        doc_type=document.doc_type,
                        section_name=payload.section_name,
                    )
                except Exception:
                    logger.warning(
                        "Failed to log LLM usage for rewrite section=%s",
                        payload.section_name,
                        exc_info=True,
                    )

        # 解析并更新内容
        try:
            parsed_value = _parse_section_value(raw_json, section_spec)
            parsed_value = _validate_section_value(parsed_value, section_spec)
        except Exception:
            logger.warning(
                "重写结果 JSON 解析失败 (section=%s)，保留原内容",
                payload.section_name,
                exc_info=True,
            )
            parsed_value = _get_section_value(content, payload.section_name)
        parsed_value, references = _apply_citations_to_section(
            payload.section_name,
            parsed_value,
            session,
        )
        new_content = _set_section_value(
            content,
            payload.section_name,
            parsed_value,
            references,
        )
        document.content = new_content.model_dump(by_alias=True)
        document.version += 1
        _create_snapshot(session, document, new_content, "rewrite")
        session.add(document)
        session.commit()
        session.refresh(document)

        await ensure_client_connected(request)

        yield format_sse(
            "section_document",
            {
                "id": document.id,
                "task_id": document.task_id,
                "user_id": document.user_id,
                "doc_type": document.doc_type,
                "title": document.title,
                "content": document.content,
                "version": document.version,
                "created_at": document.created_at.isoformat(),
                "updated_at": document.updated_at.isoformat(),
                "section_name": payload.section_name,
                "section_title": section_title,
            },
        )
        yield format_sse(
            "section_done",
            {"section_name": payload.section_name},
        )
        yield format_sse("status", {"state": "ready"})
        yield format_sse("document_done", {"document_id": document.id})

    except ClientDisconnected:
        return
    except Exception as exc:
        logger.exception("重写失败 (document=%s, section=%s): %s", document.id, payload.section_name, exc)
        yield format_sse("error", {"message": "重写过程中出现错误，请稍后重试。"})
