"""Word 回导服务 — 解析修改后的 .docx、diff、合并。"""

from __future__ import annotations

import difflib
from io import BytesIO
from typing import Any

from docx import Document as DocxDocument
from fastapi import HTTPException
from sqlmodel import Session

from app.models import Document
from app.schemas.content import (
    KeyPoints,
    LessonPlanContent,
    LessonPlanHeader,
    TeachingObjective,
    TeachingProcessStep,
)
from app.schemas.document import DocumentRead
from app.schemas.reimport import (
    DiffSegment,
    ReimportMergePayload,
    ReimportPreview,
    SectionDiff,
)
from app.services.document_service import (
    load_content,
    record_current_snapshot,
    serialize_document,
)
from app.services.import_service import (
    _build_lesson_plan_content,
    _bucket_document_items,
    _clean_text,
    _extract_metadata,
)

_SECTION_TITLES: dict[str, str] = {
    "objectives": "教学目标",
    "key_points": "教学重难点",
    "preparation": "教学准备",
    "teaching_process": "教学过程",
    "board_design": "板书设计",
    "reflection": "教学反思",
}

_TEXT_SECTIONS = {"board_design", "reflection"}
_LIST_SECTIONS = {"objectives", "preparation"}


def preview_reimport(
    file_bytes: bytes,
    filename: str,
    document: Document,
) -> ReimportPreview:
    """解析上传的 .docx 并与当前文档逐 section diff。"""
    current = load_content(document)

    # Parse imported docx using existing import parser
    try:
        docx = DocxDocument(BytesIO(file_bytes))
    except Exception:
        raise HTTPException(status_code=400, detail="无法解析该文件，请确认是有效的 .docx 文件")

    paragraphs = [_clean_text(p.text) for p in docx.paragraphs if _clean_text(p.text)]
    metadata = _extract_metadata(paragraphs, filename)
    buckets, unmapped, warnings = _bucket_document_items(docx, paragraphs)
    imported = _build_lesson_plan_content(metadata, buckets, warnings)

    sections = _diff_sections(current, imported)

    return ReimportPreview(
        source_filename=filename,
        original_document_id=document.id,
        original_version=document.version,
        sections=sections,
    )


def apply_reimport_merge(
    session: Session,
    document: Document,
    payload: ReimportMergePayload,
    imported: LessonPlanContent,
) -> DocumentRead:
    """合并选中的 section 到当前文档。"""
    if payload.document_version != document.version:
        raise HTTPException(status_code=409, detail="文档版本冲突，请刷新后重试")

    # Snapshot before merge
    record_current_snapshot(session, document, source="reimport_pre")

    current = load_content(document)

    for section_name in payload.sections_to_accept:
        if not hasattr(imported, section_name):
            continue
        value = getattr(imported, section_name)
        setattr(current, section_name, value)
        # Mark as pending so teacher can review
        status_field = f"{section_name}_status"
        if hasattr(current, status_field):
            setattr(current, status_field, "pending")

    document.content = current.model_dump(by_alias=True)  # type: ignore[assignment]
    document.version += 1
    session.add(document)
    session.commit()
    session.refresh(document)

    return serialize_document(document)


def _diff_sections(
    current: LessonPlanContent,
    imported: LessonPlanContent,
) -> list[SectionDiff]:
    """逐 section 比较，生成 diff 列表。"""
    sections: list[SectionDiff] = []

    for section_name, title in _SECTION_TITLES.items():
        original = getattr(current, section_name, None)
        new = getattr(imported, section_name, None)

        diff = _compute_section_diff(section_name, title, original, new)
        sections.append(diff)

    return sections


def _compute_section_diff(
    section_name: str,
    title: str,
    original: Any,
    new: Any,
) -> SectionDiff:
    """计算单个 section 的 diff。"""

    # Both empty / None
    if _is_empty(original) and _is_empty(new):
        return SectionDiff(
            section_name=section_name,
            section_title=title,
            status="unchanged",
        )

    # Only original exists (deleted in import)
    if not _is_empty(original) and _is_empty(new):
        return SectionDiff(
            section_name=section_name,
            section_title=title,
            status="deleted",
            original_content=_serialize_for_diff(original),
            imported_content=None,
        )

    # Only new exists (new in import)
    if _is_empty(original) and not _is_empty(new):
        return SectionDiff(
            section_name=section_name,
            section_title=title,
            status="new",
            original_content=None,
            imported_content=_serialize_for_diff(new),
        )

    # Both exist — compare
    if section_name in _TEXT_SECTIONS:
        return _diff_text_section(section_name, title, str(original), str(new))
    elif section_name in _LIST_SECTIONS:
        return _diff_list_section(section_name, title, original, new)
    elif section_name == "teaching_process":
        return _diff_teaching_process(section_name, title, original, new)
    elif section_name == "key_points":
        return _diff_key_points(section_name, title, original, new)
    else:
        # Generic: compare as string
        if str(original) != str(new):
            return _diff_text_section(section_name, title, str(original), str(new))
        return SectionDiff(
            section_name=section_name,
            section_title=title,
            status="unchanged",
        )


def _diff_text_section(
    section_name: str,
    title: str,
    original: str,
    new: str,
) -> SectionDiff:
    """文本 section 的逐字符 diff。"""
    if original == new:
        return SectionDiff(
            section_name=section_name,
            section_title=title,
            status="unchanged",
        )

    matcher = difflib.SequenceMatcher(None, original, new)
    segments: list[DiffSegment] = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            segments.append(DiffSegment(type="equal", text=original[i1:i2]))
        elif tag == "delete":
            segments.append(DiffSegment(type="delete", text=original[i1:i2]))
        elif tag == "insert":
            segments.append(DiffSegment(type="insert", text=new[j1:j2]))
        elif tag == "replace":
            segments.append(DiffSegment(type="delete", text=original[i1:i2]))
            segments.append(DiffSegment(type="insert", text=new[j1:j2]))

    return SectionDiff(
        section_name=section_name,
        section_title=title,
        status="modified",
        original_content=original,
        imported_content=new,
        diff_segments=segments,
    )


def _diff_list_section(
    section_name: str,
    title: str,
    original: list,
    new: list,
) -> SectionDiff:
    """字符串列表 section 的逐项比对。"""
    orig_set = set(str(o) for o in original)
    new_set = set(str(n) for n in new)

    if orig_set == new_set:
        return SectionDiff(
            section_name=section_name,
            section_title=title,
            status="unchanged",
        )

    return SectionDiff(
        section_name=section_name,
        section_title=title,
        status="modified",
        original_content=original,
        imported_content=new,
    )


def _diff_key_points(
    section_name: str,
    title: str,
    original: KeyPoints,
    new: KeyPoints,
) -> SectionDiff:
    """教学重难点 diff。"""
    changed = False

    # Compare key_points lists
    if set(original.key_points) != set(new.key_points):
        changed = True
    if set(original.difficulties) != set(new.difficulties):
        changed = True

    if not changed:
        return SectionDiff(
            section_name=section_name,
            section_title=title,
            status="unchanged",
        )

    return _diff_text_section(
        section_name,
        title,
        _format_key_points(original),
        _format_key_points(new),
    )


def _diff_teaching_process(
    section_name: str,
    title: str,
    original: list[TeachingProcessStep],
    new: list[TeachingProcessStep],
) -> SectionDiff:
    """教学过程逐环节 diff。"""
    if len(original) != len(new):
        return SectionDiff(
            section_name=section_name,
            section_title=title,
            status="modified",
            original_content=[_step_to_dict(s) for s in original],
            imported_content=[_step_to_dict(s) for s in new],
        )

    for o_step, n_step in zip(original, new):
        if (
            o_step.phase != n_step.phase
            or o_step.teacher_activity != n_step.teacher_activity
            or o_step.student_activity != n_step.student_activity
            or o_step.design_intent != n_step.design_intent
            or o_step.duration != n_step.duration
        ):
            return SectionDiff(
                section_name=section_name,
                section_title=title,
                status="modified",
                original_content=[_step_to_dict(s) for s in original],
                imported_content=[_step_to_dict(s) for s in new],
            )

    return SectionDiff(
        section_name=section_name,
        section_title=title,
        status="unchanged",
    )


def _is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    if isinstance(value, (list, dict)) and len(value) == 0:
        return True
    if isinstance(value, KeyPoints) and not value.key_points and not value.difficulties:
        return True
    return False


def _serialize_for_diff(value: Any) -> Any:
    if isinstance(value, KeyPoints):
        return _format_key_points(value)
    if isinstance(value, list) and value and isinstance(value[0], TeachingProcessStep):
        return [_step_to_dict(s) for s in value]
    if isinstance(value, list) and value and isinstance(value[0], TeachingObjective):
        return [{"dimension": o.dimension, "content": o.content} for o in value]
    if isinstance(value, list):
        return value
    return str(value)


def _step_to_dict(step: TeachingProcessStep) -> dict:
    return {
        "phase": step.phase,
        "duration": step.duration,
        "teacher_activity": step.teacher_activity,
        "student_activity": step.student_activity,
        "design_intent": step.design_intent,
    }


def _format_key_points(kp: KeyPoints) -> str:
    parts = []
    if kp.key_points:
        parts.append("教学重点：\n" + "\n".join(f"• {p}" for p in kp.key_points))
    if kp.difficulties:
        parts.append("教学难点：\n" + "\n".join(f"• {d}" for d in kp.difficulties))
    return "\n\n".join(parts)
