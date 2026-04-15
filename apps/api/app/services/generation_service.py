"""AI 生成服务：流式生成教案/学案。

逐 token 转发 + section 级 SSE 事件，通过 SSE 推送给前端。
"""

from __future__ import annotations

import json
import logging
import re
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

logger = logging.getLogger("lessonpilot.generation")

# ---------------------------------------------------------------------------
# Section 名称 → 中文标题映射
# ---------------------------------------------------------------------------

LESSON_PLAN_SECTIONS: list[tuple[str, str]] = [
    ("objectives", "教学目标"),
    ("key_points", "教学重难点"),
    ("preparation", "教学准备"),
    ("teaching_process", "教学过程"),
    ("board_design", "板书设计"),
    ("reflection", "教学反思"),
]

STUDY_GUIDE_SECTIONS: list[tuple[str, str]] = [
    ("learning_objectives", "学习目标"),
    ("key_difficulties", "重点难点预测"),
    ("prior_knowledge", "知识链接"),
    ("self_study", "自主学习"),
    ("collaboration", "合作探究"),
    ("presentation", "展示提升"),
    ("assessment", "达标测评"),
    ("extension", "拓展延伸"),
    ("self_reflection", "自主反思"),
]


def _get_section_map(doc_type: str) -> dict[str, str]:
    """返回 section_name → title 映射。"""
    entries = LESSON_PLAN_SECTIONS if doc_type == "lesson_plan" else STUDY_GUIDE_SECTIONS
    return {name: title for name, title in entries}


def _get_section_order(doc_type: str) -> list[str]:
    """返回 section 名称有序列表。"""
    entries = LESSON_PLAN_SECTIONS if doc_type == "lesson_plan" else STUDY_GUIDE_SECTIONS
    return [name for name, _ in entries]


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
# JSON 解析
# ---------------------------------------------------------------------------


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
# 流式 section 检测
# ---------------------------------------------------------------------------


class _SectionTracker:
    """跟踪累积文本中的 section 边界。"""

    def __init__(self, doc_type: str) -> None:
        self.doc_type = doc_type
        self.section_map = _get_section_map(doc_type)
        self.section_order = _get_section_order(doc_type)
        self.completed_sections: set[str] = set()
        # 上次检测到的长度，避免重复扫描
        self._last_scan_pos = 0
        # 预编译正则：匹配 "section_name_status": "pending" 或 "confirmed"
        self._status_pattern = re.compile(
            r'"(' + "|".join(re.escape(n) for n in self.section_order) + r')_status"\s*:\s*"(?:pending|confirmed)"'
        )

    def detect_sections(self, accumulated: str) -> list[str]:
        """检测新增的已完成 section，返回新检测到的 section_name 列表。"""
        newly_detected: list[str] = []
        # 只扫描新增加的文本区域（加一些 overlap 以防分割）
        scan_start = max(0, self._last_scan_pos - 100)
        scan_text = accumulated[scan_start:]
        self._last_scan_pos = len(accumulated)

        for match in self._status_pattern.finditer(scan_text):
            section_name = match.group(1)
            if section_name not in self.completed_sections:
                self.completed_sections.add(section_name)
                newly_detected.append(section_name)

        return newly_detected

    def get_title(self, section_name: str) -> str:
        return self.section_map.get(section_name, section_name)


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
                    "doc_type": doc_type,
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

            # 逐 token 流式转发 + section 边界检测
            tracker = _SectionTracker(doc_type)
            accumulated = ""

            async for chunk in stream:
                accumulated += chunk

                # 发送 raw text delta
                yield _format_sse("section_delta", {"text": chunk})

                # 检测 section 边界
                newly_completed = tracker.detect_sections(accumulated)
                for section_name in newly_completed:
                    yield _format_sse(
                        "section_start",
                        {
                            "doc_type": doc_type,
                            "section_name": section_name,
                            "title": tracker.get_title(section_name),
                        },
                    )
                    yield _format_sse(
                        "section_complete",
                        {
                            "doc_type": doc_type,
                            "section_name": section_name,
                        },
                    )

            # 流结束：解析完整 JSON，校验，保存
            try:
                content = _parse_content_json(accumulated, doc_type)
            except Exception:
                logger.warning(
                    "AI 输出 JSON 解析失败 (task=%s, doc_type=%s)，使用空模板回退",
                    task.id,
                    doc_type,
                )
                content = _create_fallback_content(task, doc_type)
                yield _format_sse(
                    "warning",
                    {
                        "message": f"{'教案' if doc_type == 'lesson_plan' else '学案'}内容解析异常，"
                        "已使用空模板。请尝试重新生成或手动编辑。",
                        "doc_type": doc_type,
                    },
                )

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
        logger.exception("生成失败 (task=%s): %s", task.id, exc)
        task.status = "ready"
        session.add(task)
        session.commit()
        yield _format_sse("error", {"message": "生成过程中出现错误，请稍后重试。"})


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
