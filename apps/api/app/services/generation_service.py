"""AI 生成服务：按 section 顺序流式生成教案/学案。"""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator
from typing import Any

from fastapi import HTTPException, Request, status
from pydantic import TypeAdapter
from sqlmodel import Session, select

from app.core.config import get_settings
from app.models import Document, Task
from app.models.template import TemplateSection
from app.schemas.content import (
    AssessmentItem,
    CitationReference,
    DocumentContent,
    KeyPoints,
    LessonPlanContent,
    StudyGuideContent,
    TeachingObjective,
    TeachingProcessStep,
    create_empty_lesson_plan,
    create_empty_study_guide,
)
from app.schemas.personal_asset import PersonalAssetRecommendation
from app.services.document_service import load_content, save_document
from app.services.knowledge_service import (
    build_citation_metadata,
    count_knowledge_chunks,
    format_knowledge_context,
    resolve_rag_domain_match,
    retrieve_knowledge,
    strip_citations_from_content,
)
from app.services.llm_service import SectionGenerationContext, get_provider
from app.services.personal_asset_service import (
    format_personal_asset_context,
    recommend_personal_assets,
)
from app.services.sse_utils import ClientDisconnected, ensure_client_connected, format_sse

logger = logging.getLogger("lessonpilot.generation")

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
    entries = LESSON_PLAN_SECTIONS if doc_type == "lesson_plan" else STUDY_GUIDE_SECTIONS
    return {name: title for name, title in entries}


def _get_section_order(doc_type: str) -> list[str]:
    entries = LESSON_PLAN_SECTIONS if doc_type == "lesson_plan" else STUDY_GUIDE_SECTIONS
    return [name for name, _ in entries]


def _load_prompt_hints(session: Session, template_id: str | None, doc_type: str) -> str:
    if not template_id:
        return ""
    sections = session.exec(
        select(TemplateSection)
        .where(TemplateSection.template_id == template_id)
        .order_by(TemplateSection.order)
    ).all()
    if not sections:
        return ""
    hints: list[str] = []
    for section in sections:
        if section.prompt_hints:
            hints.append(f"【{section.section_name}】{section.prompt_hints}")
    return "\n".join(hints)


def get_task_and_documents(
    session: Session, task_id: str, user_id: str
) -> tuple[Task, list[Document]]:
    task = session.exec(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    ).first()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    docs = session.exec(select(Document).where(Document.task_id == task_id)).all()
    return task, list(docs)


_SECTION_SPECS: dict[str, list[dict[str, Any]]] = {
    "lesson_plan": [
        {
            "name": "objectives",
            "title": "教学目标",
            "schema": '[{"dimension":"knowledge","content":"具体目标"}]',
            "rules": "输出 2-3 条具体、可衡量的目标，覆盖知识、能力、情感维度。",
            "kind": "array",
            "adapter": TypeAdapter(list[TeachingObjective]),
            "fallback": [],
        },
        {
            "name": "key_points",
            "title": "教学重难点",
            "schema": '{"keyPoints":["重点1"],"difficulties":["难点1"]}',
            "rules": "重点和难点都要落到本课真实内容，不要空泛。",
            "kind": "object",
            "adapter": TypeAdapter(KeyPoints),
            "fallback": {"keyPoints": [], "difficulties": []},
        },
        {
            "name": "preparation",
            "title": "教学准备",
            "schema": '["教具准备1","学习单"]',
            "rules": "只写老师实际需要准备的内容，简洁清楚。",
            "kind": "array",
            "adapter": TypeAdapter(list[str]),
            "fallback": [],
        },
        {
            "name": "teaching_process",
            "title": "教学过程",
            "schema": (
                '[{"phase":"导入","duration":5,"teacher_activity":"...",'
                '"student_activity":"...","design_intent":"..."}]'
            ),
            "rules": "至少 3 个环节；每个环节都要有教师活动、学生活动、设计意图和时长。",
            "kind": "array",
            "adapter": TypeAdapter(list[TeachingProcessStep]),
            "fallback": [],
        },
        {
            "name": "board_design",
            "title": "板书设计",
            "schema": '"板书主线\\n一、...\\n二、..."',
            "rules": "输出可直接用于板书的层级文本。",
            "kind": "string",
            "adapter": TypeAdapter(str),
            "fallback": "",
        },
        {
            "name": "reflection",
            "title": "教学反思",
            "schema": '""',
            "rules": "默认留空字符串，不主动编造教学反思。",
            "kind": "string",
            "adapter": TypeAdapter(str),
            "fallback": "",
        },
    ],
    "study_guide": [
        {
            "name": "learning_objectives",
            "title": "学习目标",
            "schema": '["我能...","我能..."]',
            "rules": '必须用“我能...”口吻，写 2-3 条。',
            "kind": "array",
            "adapter": TypeAdapter(list[str]),
            "fallback": [],
        },
        {
            "name": "key_difficulties",
            "title": "重点难点预测",
            "schema": '["重点1","难点1"]',
            "rules": "围绕本课具体内容预测学生的重点与难点。",
            "kind": "array",
            "adapter": TypeAdapter(list[str]),
            "fallback": [],
        },
        {
            "name": "prior_knowledge",
            "title": "知识链接",
            "schema": '["前置知识1","前置知识2"]',
            "rules": "列出学生进入本课前需要回顾的知识。",
            "kind": "array",
            "adapter": TypeAdapter(list[str]),
            "fallback": [],
        },
        {
            "name": "self_study",
            "title": "自主学习",
            "schema": '[{"level":"A","itemType":"short_answer","prompt":"...","options":[],"answer":"","analysis":""}]',
            "rules": "输出基础层题目，适合学生独立完成。",
            "kind": "array",
            "adapter": TypeAdapter(list[AssessmentItem]),
            "fallback": [],
        },
        {
            "name": "collaboration",
            "title": "合作探究",
            "schema": '[{"level":"B","itemType":"short_answer","prompt":"...","options":[],"answer":"","analysis":""}]',
            "rules": "输出适合小组讨论和合作探究的题目。",
            "kind": "array",
            "adapter": TypeAdapter(list[AssessmentItem]),
            "fallback": [],
        },
        {
            "name": "presentation",
            "title": "展示提升",
            "schema": '[{"level":"C","itemType":"short_answer","prompt":"...","options":[],"answer":"","analysis":""}]',
            "rules": "输出促进表达、迁移和展示的题目。",
            "kind": "array",
            "adapter": TypeAdapter(list[AssessmentItem]),
            "fallback": [],
        },
        {
            "name": "assessment",
            "title": "达标测评",
            "schema": (
                '[{"level":"A","itemType":"choice","prompt":"...",'
                '"options":["A","B"],"answer":"A","analysis":"..."}]'
            ),
            "rules": "至少包含 1 道可课堂检测的题目，答案和解析完整。",
            "kind": "array",
            "adapter": TypeAdapter(list[AssessmentItem]),
            "fallback": [],
        },
        {
            "name": "extension",
            "title": "拓展延伸",
            "schema": '[{"level":"D","itemType":"short_answer","prompt":"...","options":[],"answer":"","analysis":""}]',
            "rules": "输出 1 组可选做的拓展任务。",
            "kind": "array",
            "adapter": TypeAdapter(list[AssessmentItem]),
            "fallback": [],
        },
        {
            "name": "self_reflection",
            "title": "自主反思",
            "schema": '""',
            "rules": "默认留空字符串，不主动编造学生反思。",
            "kind": "string",
            "adapter": TypeAdapter(str),
            "fallback": "",
        },
    ],
}

_LEARNING_PROCESS_SECTION_MAP = {
    "self_study": "selfStudy",
    "collaboration": "collaboration",
    "presentation": "presentation",
}

_OBJECTIVE_DIMENSION_MAP = {
    "knowledge": "knowledge",
    "知识": "knowledge",
    "知识与技能": "knowledge",
    "知识技能": "knowledge",
    "知识目标": "knowledge",
    "ability": "ability",
    "过程与方法": "ability",
    "能力": "ability",
    "方法": "ability",
    "能力目标": "ability",
    "emotion": "emotion",
    "emotionvalue": "emotion",
    "情感": "emotion",
    "情感态度价值观": "emotion",
    "情感态度与价值观": "emotion",
    "情感目标": "emotion",
    "价值观": "emotion",
}

_ASSESSMENT_TYPE_MAP = {
    "choice": "choice",
    "singlechoice": "choice",
    "multiplechoice": "choice",
    "选择题": "choice",
    "fillblank": "fill_blank",
    "fill_blank": "fill_blank",
    "填空题": "fill_blank",
    "shortanswer": "short_answer",
    "short_answer": "short_answer",
    "简答题": "short_answer",
    "问答题": "short_answer",
}

_DEFAULT_ASSESSMENT_LEVEL = {
    "self_study": "A",
    "collaboration": "B",
    "presentation": "C",
    "assessment": "A",
    "extension": "D",
}


def _get_section_specs(doc_type: str) -> list[dict[str, Any]]:
    return _SECTION_SPECS[doc_type]


def _normalize_label(value: Any) -> str:
    return str(value).strip().replace(" ", "").replace("_", "").lower()


def _ensure_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _extract_text_value(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, dict):
        for key in (
            "content",
            "text",
            "value",
            "goal",
            "objective",
            "description",
            "prompt",
            "question",
            "stem",
            "title",
        ):
            candidate = value.get(key)
            if isinstance(candidate, str) and candidate.strip():
                return candidate.strip()
    return ""


def _normalize_string_list(value: Any) -> list[str]:
    if isinstance(value, dict):
        for key in ("items", "list", "values", "contents", "goals", "objectives"):
            if key in value:
                return _normalize_string_list(value.get(key))
        return [text for text in (_extract_text_value(item) for item in value.values()) if text]
    return [text for text in (_extract_text_value(item) for item in _ensure_list(value)) if text]


def _normalize_string_value(value: Any) -> str:
    if isinstance(value, dict):
        for key in ("content", "text", "value", "body", "reflection"):
            candidate = value.get(key)
            if isinstance(candidate, str) and candidate.strip():
                return candidate.strip()
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, list):
        return "\n".join(text for text in (_extract_text_value(item) for item in value) if text)
    return str(value).strip() if value is not None else ""


def _normalize_objective_dimension(value: Any, fallback: str) -> str:
    normalized = _normalize_label(value)
    return _OBJECTIVE_DIMENSION_MAP.get(normalized, fallback)


def _normalize_objectives_value(value: Any) -> list[dict[str, str]]:
    if isinstance(value, dict):
        dimension_pairs = []
        for key, item in value.items():
            if _normalize_label(key) in _OBJECTIVE_DIMENSION_MAP:
                dimension_pairs.append(
                    {
                        "dimension": _normalize_objective_dimension(key, "knowledge"),
                        "content": _extract_text_value(item),
                    }
                )
        if dimension_pairs:
            return [item for item in dimension_pairs if item["content"]]
        for key in ("objectives", "goals", "items", "list", "values"):
            if key in value:
                value = value.get(key)
                break

    default_dimensions = ["knowledge", "ability", "emotion"]
    normalized_items: list[dict[str, str]] = []
    for index, item in enumerate(_ensure_list(value)):
        fallback_dimension = default_dimensions[min(index, len(default_dimensions) - 1)]
        if isinstance(item, dict):
            dimension = _normalize_objective_dimension(
                item.get("dimension") or item.get("type") or item.get("category") or item.get("label"),
                fallback_dimension,
            )
            content = _extract_text_value(item)
        else:
            dimension = fallback_dimension
            content = _extract_text_value(item)
        if content:
            normalized_items.append({"dimension": dimension, "content": content})
    return normalized_items


def _normalize_key_points_value(value: Any) -> dict[str, list[str]]:
    if isinstance(value, dict):
        key_points = (
            value.get("keyPoints")
            or value.get("key_points")
            or value.get("重点")
            or value.get("重点内容")
        )
        difficulties = (
            value.get("difficulties")
            or value.get("difficulty")
            or value.get("难点")
            or value.get("难点内容")
        )
        return {
            "keyPoints": _normalize_string_list(key_points),
            "difficulties": _normalize_string_list(difficulties),
        }
    return {"keyPoints": _normalize_string_list(value), "difficulties": []}


def _normalize_duration(value: Any) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        digits = "".join(char for char in value if char.isdigit())
        if digits:
            return int(digits)
    return 5


def _normalize_teaching_process_value(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, dict):
        for key in ("steps", "items", "process", "teaching_process"):
            if key in value:
                value = value.get(key)
                break

    normalized_items: list[dict[str, Any]] = []
    for item in _ensure_list(value):
        if not isinstance(item, dict):
            continue
        normalized_items.append(
            {
                "phase": _extract_text_value(
                    item.get("phase")
                    or item.get("title")
                    or item.get("name")
                    or item.get("stage")
                ),
                "duration": _normalize_duration(item.get("duration") or item.get("time") or item.get("minutes")),
                "teacher_activity": _extract_text_value(
                    item.get("teacher_activity")
                    or item.get("teacherActivity")
                    or item.get("teacher_action")
                    or item.get("teacherAction")
                    or item.get("teacher")
                ),
                "student_activity": _extract_text_value(
                    item.get("student_activity")
                    or item.get("studentActivity")
                    or item.get("student_action")
                    or item.get("studentAction")
                    or item.get("student")
                ),
                "design_intent": _extract_text_value(
                    item.get("design_intent")
                    or item.get("designIntent")
                    or item.get("intent")
                    or item.get("rationale")
                ),
            }
        )
    return normalized_items


def _normalize_assessment_type(value: Any) -> str:
    normalized = _normalize_label(value)
    return _ASSESSMENT_TYPE_MAP.get(normalized, "short_answer")


def _normalize_options(value: Any) -> list[str]:
    if isinstance(value, str):
        return [item.strip() for item in value.splitlines() if item.strip()]
    return _normalize_string_list(value)


def _normalize_assessment_items_value(
    value: Any,
    section_name: str,
) -> list[dict[str, Any]]:
    if isinstance(value, dict):
        for key in ("items", "questions", "list", "values"):
            if key in value:
                value = value.get(key)
                break

    normalized_items: list[dict[str, Any]] = []
    for item in _ensure_list(value):
        if not isinstance(item, dict):
            text = _extract_text_value(item)
            if not text:
                continue
            normalized_items.append(
                {
                    "level": _DEFAULT_ASSESSMENT_LEVEL.get(section_name, "A"),
                    "itemType": "short_answer",
                    "prompt": text,
                    "options": [],
                    "answer": "",
                    "analysis": "",
                }
            )
            continue

        normalized_items.append(
            {
                "level": str(item.get("level") or _DEFAULT_ASSESSMENT_LEVEL.get(section_name, "A")).strip() or "A",
                "itemType": _normalize_assessment_type(
                    item.get("itemType")
                    or item.get("item_type")
                    or item.get("type")
                    or item.get("questionType")
                    or item.get("question_type")
                ),
                "prompt": _extract_text_value(
                    item.get("prompt")
                    or item.get("question")
                    or item.get("stem")
                    or item.get("title")
                    or item.get("content")
                ),
                "options": _normalize_options(item.get("options") or item.get("choices") or item.get("选项")),
                "answer": _extract_text_value(
                    item.get("answer")
                    or item.get("reference_answer")
                    or item.get("referenceAnswer")
                    or item.get("solution")
                    or item.get("参考答案")
                    or item.get("答案")
                ),
                "analysis": _extract_text_value(
                    item.get("analysis")
                    or item.get("explanation")
                    or item.get("reason")
                    or item.get("解析")
                ),
            }
        )
    return normalized_items


def _normalize_section_value(value: Any, spec: dict[str, Any]) -> Any:
    section_name = spec["name"]

    if section_name == "objectives":
        return _normalize_objectives_value(value)
    if section_name == "key_points":
        return _normalize_key_points_value(value)
    if section_name == "teaching_process":
        return _normalize_teaching_process_value(value)
    if section_name in {"preparation", "learning_objectives", "key_difficulties", "prior_knowledge"}:
        return _normalize_string_list(value)
    if section_name in {"board_design", "reflection", "self_reflection"}:
        return _normalize_string_value(value)
    if section_name in {"self_study", "collaboration", "presentation", "assessment", "extension"}:
        return _normalize_assessment_items_value(value, section_name)
    return value


def _remove_code_fence(raw: str) -> str:
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


def _extract_section_payload(parsed: Any, section_name: str) -> Any:
    if not isinstance(parsed, dict):
        return parsed
    if section_name in parsed:
        return parsed[section_name]
    alias = _LEARNING_PROCESS_SECTION_MAP.get(section_name)
    if alias and alias in parsed:
        return parsed[alias]
    if len(parsed) == 1:
        return next(iter(parsed.values()))
    return parsed


def _parse_section_value(raw: str, spec: dict[str, Any]) -> Any:
    text = _remove_code_fence(raw)
    if spec["kind"] == "string":
        try:
            parsed = json.loads(text)
            return parsed if isinstance(parsed, str) else text
        except json.JSONDecodeError:
            return text
    parsed = json.loads(text)
    return _extract_section_payload(parsed, spec["name"])


def _validate_section_value(value: Any, spec: dict[str, Any]) -> Any:
    normalized_value = _normalize_section_value(value, spec)
    return spec["adapter"].validate_python(normalized_value)


def _section_has_content(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return any(_section_has_content(item) for item in value)
    if isinstance(value, dict):
        return any(_section_has_content(item) for item in value.values())
    return value is not None


def _summarize_completed_sections(content: DocumentContent) -> str:
    lines: list[str] = []
    for name, title in _get_section_map(content.doc_type).items():
        value = _get_section_value(content, name)
        if not _section_has_content(value):
            continue
        preview = json.dumps(value, ensure_ascii=False)
        if len(preview) > 280:
            preview = preview[:280] + "..."
        lines.append(f"【{title}】{preview}")
    return "\n".join(lines) if lines else "暂无已完成内容"


def _get_section_value(content: DocumentContent, section_name: str) -> Any:
    data = content.model_dump(by_alias=True)
    if content.doc_type == "study_guide" and section_name in _LEARNING_PROCESS_SECTION_MAP:
        return data.get("learning_process", {}).get(_LEARNING_PROCESS_SECTION_MAP[section_name], [])
    return data.get(section_name)


def _set_section_value(
    content: DocumentContent,
    section_name: str,
    value: Any,
    references: list[CitationReference],
) -> DocumentContent:
    data = content.model_dump(by_alias=True)
    if content.doc_type == "study_guide" and section_name in _LEARNING_PROCESS_SECTION_MAP:
        learning_process = dict(data.get("learning_process") or {})
        learning_process[_LEARNING_PROCESS_SECTION_MAP[section_name]] = value
        data["learning_process"] = learning_process
    else:
        data[section_name] = value

    status_key = f"{section_name}_status"
    if status_key in data:
        data[status_key] = "pending"

    references_map = dict(data.get("section_references") or {})
    if references:
        references_map[section_name] = [reference.model_dump() for reference in references]
    else:
        references_map.pop(section_name, None)
    data["section_references"] = references_map

    if content.doc_type == "study_guide":
        return StudyGuideContent.model_validate(data)
    return LessonPlanContent.model_validate(data)


def _build_rag_status_payload(
    *,
    status: str,
    domain: str | None = None,
    matched_keywords: list[str] | None = None,
    chunk_count: int = 0,
    retrieved_count: int = 0,
    message: str,
) -> dict[str, Any]:
    return {
        "status": status,
        "domain": domain,
        "matched_keywords": matched_keywords or [],
        "chunk_count": chunk_count,
        "retrieved_count": retrieved_count,
        "message": message,
    }


def _build_asset_status_payload(
    *,
    status: str,
    matched_assets: list[dict[str, str]] | None = None,
    snippet_count: int = 0,
    message: str,
) -> dict[str, Any]:
    return {
        "status": status,
        "matched_assets": matched_assets or [],
        "snippet_count": snippet_count,
        "message": message,
    }


def _build_personal_reference_map(
    recommendations: list[PersonalAssetRecommendation],
) -> dict[str, CitationReference]:
    reference_map: dict[str, CitationReference] = {}
    for item in recommendations:
        reference_map.setdefault(
            item.asset_id,
            CitationReference(
                chunk_id=item.asset_id,
                source=f"我的资料库 · {item.file_type}",
                title=item.title,
                knowledge_type="personal_asset",
                chapter=item.section_title,
                content_snippet=item.content_snippet,
            ),
        )
    return reference_map


def _apply_citations_to_section(
    section_name: str,
    value: Any,
    session: Session,
    personal_references: dict[str, CitationReference] | None = None,
) -> tuple[Any, list[CitationReference]]:
    cleaned_wrapper, chunk_ids = strip_citations_from_content({"value": value})
    cleaned_value = cleaned_wrapper["value"]
    if not chunk_ids:
        return cleaned_value, []
    personal_references = personal_references or {}
    metadata = build_citation_metadata(chunk_ids, session)
    public_references = [
        CitationReference(
            chunk_id=item.chunk_id,
            source=item.source,
            title=item.title,
            knowledge_type=item.knowledge_type,
            chapter=item.chapter,
            content_snippet=item.content_snippet,
        )
        for item in metadata
    ]
    public_ids = {reference.chunk_id for reference in public_references}
    references = list(public_references)
    for chunk_id in chunk_ids:
        if chunk_id in public_ids:
            continue
        personal_reference = personal_references.get(chunk_id)
        if personal_reference is not None:
            references.append(personal_reference)
    return cleaned_value, references


async def stream_generation(
    *,
    session: Session,
    task: Task,
    request: Request | None = None,
    use_personal_assets: bool = False,
    personal_asset_ids: list[str] | None = None,
) -> AsyncIterator[str]:
    """按 section 顺序流式生成教案/学案。"""
    provider = get_provider()

    try:
        task.status = "generating"
        session.add(task)
        session.commit()

        yield format_sse("status", {"status": "generating"})

        doc_types: list[str] = []
        if task.lesson_type in ("lesson_plan", "both"):
            doc_types.append("lesson_plan")
        if task.lesson_type in ("study_guide", "both"):
            doc_types.append("study_guide")

        total_sections = sum(len(_get_section_specs(doc_type)) for doc_type in doc_types)
        completed_sections = 0

        settings = get_settings()
        rag_match = resolve_rag_domain_match(task.topic)
        knowledge_chunks = []
        knowledge_ctx = ""
        personal_asset_ctx = ""
        personal_references: dict[str, CitationReference] = {}
        if not settings.rag_enabled or settings.rag_trigger_mode == "disabled":
            yield format_sse(
                "rag_status",
                _build_rag_status_payload(
                    status="disabled",
                    message="知识增强当前已关闭，本次会按普通生成处理。",
                ),
            )
        elif rag_match is None:
            yield format_sse(
                "rag_status",
                _build_rag_status_payload(
                    status="unmatched",
                    message="当前课题暂未命中已配置的语文知识包，本次会按普通生成处理。",
                ),
            )
        else:
            chunk_count = count_knowledge_chunks(session, rag_match.domain)
            if chunk_count == 0:
                yield format_sse(
                    "rag_status",
                    _build_rag_status_payload(
                        status="matched_empty",
                        domain=rag_match.domain,
                        matched_keywords=rag_match.matched_keywords,
                        message="已命中知识域，但知识库里还没有对应资料，请先导入知识包。",
                    ),
                )
            else:
                rag_status_payload = _build_rag_status_payload(
                    status="degraded",
                    domain=rag_match.domain,
                    matched_keywords=rag_match.matched_keywords,
                    chunk_count=chunk_count,
                    message="已命中知识域，但本次检索未返回可用资料，已按普通生成处理。",
                )
                try:
                    knowledge_chunks = await retrieve_knowledge(
                        session,
                        topic=task.topic,
                        requirements=task.requirements or "",
                        max_tokens=settings.rag_max_knowledge_tokens,
                        top_k=settings.rag_top_k,
                        domain=rag_match.domain,
                        raise_on_embedding_error=True,
                    )
                    knowledge_ctx = format_knowledge_context(knowledge_chunks)
                    if knowledge_chunks:
                        logger.info(
                            "RAG 检索到 %d 条知识 (task=%s, domain=%s)",
                            len(knowledge_chunks),
                            task.id,
                            rag_match.domain,
                        )
                        rag_status_payload = _build_rag_status_payload(
                            status="ready",
                            domain=rag_match.domain,
                            matched_keywords=rag_match.matched_keywords,
                            chunk_count=chunk_count,
                            retrieved_count=len(knowledge_chunks),
                            message=f"已命中“{rag_match.domain}”知识包，本次会参考相关资料生成。",
                        )
                except Exception:
                    logger.warning("RAG 检索失败 (task=%s)，跳过", task.id, exc_info=True)
                    rag_status_payload = _build_rag_status_payload(
                        status="degraded",
                        domain=rag_match.domain,
                        matched_keywords=rag_match.matched_keywords,
                        chunk_count=chunk_count,
                        message="知识增强检索暂时不可用，本次已自动降级为普通生成。",
                    )

                yield format_sse("rag_status", rag_status_payload)

        selected_asset_ids = personal_asset_ids or []
        should_use_personal_assets = use_personal_assets or bool(selected_asset_ids)
        if not should_use_personal_assets:
            yield format_sse(
                "asset_status",
                _build_asset_status_payload(
                    status="disabled",
                    message="未开启个人资料参考，本次只按当前课题和已启用知识库生成。",
                ),
            )
        else:
            try:
                recommendations = recommend_personal_assets(
                    session,
                    task.user_id,
                    subject=task.subject,
                    grade=task.grade,
                    topic=task.topic,
                    keywords=task.requirements or "",
                    asset_ids=selected_asset_ids or None,
                    limit=6,
                )
                personal_asset_ctx = format_personal_asset_context(recommendations)
                personal_references = _build_personal_reference_map(recommendations)
                if recommendations:
                    matched_assets: list[dict[str, str]] = []
                    seen_asset_ids: set[str] = set()
                    for item in recommendations:
                        if item.asset_id in seen_asset_ids:
                            continue
                        seen_asset_ids.add(item.asset_id)
                        matched_assets.append(
                            {
                                "asset_id": item.asset_id,
                                "title": item.title,
                                "file_type": item.file_type,
                            }
                        )
                    yield format_sse(
                        "asset_status",
                        _build_asset_status_payload(
                            status="ready",
                            matched_assets=matched_assets,
                            snippet_count=len(recommendations),
                            message=f"已命中 {len(matched_assets)} 份我的资料，本次会参考相关片段生成。",
                        ),
                    )
                else:
                    yield format_sse(
                        "asset_status",
                        _build_asset_status_payload(
                            status="unmatched",
                            message="我的资料库暂未匹配到当前课题，本次会按普通生成处理。",
                        ),
                    )
            except Exception:
                logger.warning("个人资料检索失败 (task=%s)，跳过", task.id, exc_info=True)
                yield format_sse(
                    "asset_status",
                    _build_asset_status_payload(
                        status="degraded",
                        message="个人资料暂时无法检索，本次已自动降级为普通生成。",
                    ),
                )

        for doc_type in doc_types:
            await ensure_client_connected(request)
            doc = _get_or_create_document(session, task, doc_type)
            content = load_content(doc)
            prompt_hints = _load_prompt_hints(session, task.template_id, doc_type)
            specs = _get_section_specs(doc_type)

            for index, spec in enumerate(specs):
                await ensure_client_connected(request)
                yield format_sse(
                    "progress",
                    {
                        "progress": completed_sections / max(total_sections, 1),
                        "completed": completed_sections,
                        "total": total_sections,
                        "doc_type": doc_type,
                        "section_name": spec["name"],
                        "message": f"正在生成{spec['title']}...",
                    },
                )
                yield format_sse(
                    "section_start",
                    {
                        "doc_type": doc_type,
                        "section_name": spec["name"],
                        "title": spec["title"],
                    },
                )

                ctx = SectionGenerationContext(
                    doc_type=doc_type,
                    subject=task.subject,
                    grade=task.grade,
                    topic=task.topic,
                    requirements=task.requirements or "",
                    scene=task.scene,
                    class_hour=task.class_hour,
                    lesson_category=task.lesson_category,
                    prompt_hints=prompt_hints,
                    knowledge_context=knowledge_ctx,
                    personal_asset_context=personal_asset_ctx,
                    section_name=spec["name"],
                    section_title=spec["title"],
                    section_schema=spec["schema"],
                    existing_sections=_summarize_completed_sections(content),
                    section_rules=spec["rules"],
                )

                raw_parts: list[str] = []
                async for chunk in provider.generate_document_section(ctx):
                    raw_parts.append(chunk)
                    yield format_sse(
                        "section_delta",
                        {
                            "doc_type": doc_type,
                            "section_name": spec["name"],
                            "delta": chunk,
                        },
                    )

                raw_value = "".join(raw_parts)
                references: list[CitationReference] = []
                try:
                    parsed_value = _parse_section_value(raw_value, spec)
                    validated_value = _validate_section_value(parsed_value, spec)
                    validated_value, references = _apply_citations_to_section(
                        spec["name"],
                        validated_value,
                        session,
                        personal_references,
                    )
                except Exception:
                    logger.warning(
                        "Section 解析失败 (task=%s, doc_type=%s, section=%s)，使用空值回退",
                        task.id,
                        doc_type,
                        spec["name"],
                        exc_info=True,
                    )
                    validated_value = spec["fallback"]
                    yield format_sse(
                        "warning",
                        {
                            "doc_type": doc_type,
                            "section_name": spec["name"],
                            "message": f"{spec['title']}解析异常，已使用空内容回退。",
                        },
                    )

                content = _set_section_value(content, spec["name"], validated_value, references)
                doc = save_document(
                    session,
                    doc,
                    content,
                    snapshot_source="generate" if index == len(specs) - 1 else None,
                )

                yield format_sse(
                    "section_document",
                    {
                        "id": doc.id,
                        "task_id": doc.task_id,
                        "user_id": doc.user_id,
                        "doc_type": doc.doc_type,
                        "title": doc.title,
                        "content": doc.content,
                        "version": doc.version,
                        "created_at": doc.created_at.isoformat(),
                        "updated_at": doc.updated_at.isoformat(),
                        "section_name": spec["name"],
                        "section_title": spec["title"],
                    },
                )
                if references:
                    yield format_sse(
                        "citations",
                        {
                            "doc_type": doc_type,
                            "section_name": spec["name"],
                            "citations": [reference.model_dump() for reference in references],
                        },
                    )

                completed_sections += 1
                yield format_sse(
                    "section_done",
                    {
                        "doc_type": doc_type,
                        "section_name": spec["name"],
                        "completed": completed_sections,
                        "total": total_sections,
                    },
                )

            for warning_msg in _validate_generated_content(content):
                yield format_sse("warning", {"message": warning_msg, "doc_type": doc_type})

        task.status = "ready"
        session.add(task)
        session.commit()

        yield format_sse("status", {"status": "ready"})
        yield format_sse("document_done", {"message": "生成完成", "task_id": task.id})

    except ClientDisconnected:
        task.status = "ready"
        session.add(task)
        session.commit()
        return
    except Exception as exc:
        logger.exception("生成失败 (task=%s): %s", task.id, exc)
        task.status = "error"
        session.add(task)
        session.commit()
        yield format_sse("error", {"message": "生成过程中出现错误，请稍后重试。"})


def _get_or_create_document(
    session: Session,
    task: Task,
    doc_type: str,
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


def _validate_generated_content(content: DocumentContent) -> list[str]:
    """校验 AI 生成的教学内容质量，返回警告列表。"""
    warnings: list[str] = []
    data = content.model_dump(by_alias=True)

    if content.doc_type == "lesson_plan":
        objectives = data.get("objectives", [])
        if not objectives:
            warnings.append("教学目标为空，建议补充")

        process = data.get("teaching_process", [])
        if len(process) < 3:
            warnings.append(f"教学过程仅有 {len(process)} 个环节，建议至少 3 个")
        for index, phase in enumerate(process):
            if not phase.get("teacher_activity"):
                warnings.append(f"教学过程第 {index + 1} 个环节缺少教师活动")
            if not phase.get("student_activity"):
                warnings.append(f"教学过程第 {index + 1} 个环节缺少学生活动")

        key_points = data.get("keyPoints") or data.get("key_points") or {}
        kp_list = key_points.get("keyPoints") or key_points.get("key_points") or []
        if not kp_list:
            warnings.append("教学重点为空")

    elif content.doc_type == "study_guide":
        learning_objectives = data.get("learning_objectives", [])
        if not learning_objectives:
            warnings.append("学习目标为空，建议补充")

        learning_process = data.get("learning_process", {})
        self_study = learning_process.get("selfStudy", [])
        if not self_study:
            warnings.append("自主学习题目为空")

        assessment = data.get("assessment", [])
        if not assessment:
            warnings.append("达标测评题目为空")

    return warnings


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
