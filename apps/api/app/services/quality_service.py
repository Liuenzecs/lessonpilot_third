from __future__ import annotations

from app.models import Task
from app.schemas.content import DocumentContent, LessonPlanContent, StudyGuideContent
from app.schemas.quality import QualityCheckResponse, QualityIssue


def check_export_quality(task: Task, content: DocumentContent) -> QualityCheckResponse:
    if getattr(content, "doc_type", "") == "study_guide":
        return _check_study_guide(content)  # type: ignore[arg-type]
    return _check_lesson_plan(task, content)  # type: ignore[arg-type]


def _check_lesson_plan(task: Task, content: LessonPlanContent) -> QualityCheckResponse:
    issues: list[QualityIssue] = []
    warnings: list[QualityIssue] = []
    suggestions: list[QualityIssue] = []

    if not (content.header.title or task.title):
        issues.append(_issue("blocker", "header", "缺少教案标题。", "补齐标题后再导出。"))
    if not (content.header.subject or task.subject):
        issues.append(_issue("blocker", "header", "缺少学科。", "补齐学科信息。"))
    if not (content.header.grade or task.grade):
        issues.append(_issue("blocker", "header", "缺少年级。", "补齐年级信息。"))

    has_any_content = any(
        [
            content.objectives,
            content.key_points.key_points,
            content.key_points.difficulties,
            content.preparation,
            content.teaching_process,
            content.board_design,
            content.reflection,
        ]
    )
    if not has_any_content:
        issues.append(_issue("blocker", None, "当前文档几乎没有可导出的教案内容。", "先生成、导入或补写正文内容。"))

    _check_section_confirmation(issues, "objectives", "教学目标", content.objectives_status, bool(content.objectives))
    _check_section_confirmation(
        issues,
        "key_points",
        "教学重难点",
        content.key_points_status,
        bool(content.key_points.key_points or content.key_points.difficulties),
    )
    _check_section_confirmation(
        issues,
        "teaching_process",
        "教学过程",
        content.teaching_process_status,
        bool(content.teaching_process),
    )

    if content.teaching_process_status == "confirmed" and len(content.teaching_process) < 3:
        issues.append(
            _issue(
                "warning",
                "teaching_process",
                "教学过程少于 3 个环节，提交时可能显得过薄。",
                "补充导入、研读、拓展或小结等环节。",
            )
        )

    for index, step in enumerate(content.teaching_process, start=1):
        prefix = f"教学过程第 {index} 个环节"
        if not step.phase.strip():
            issues.append(_issue("warning", "teaching_process", f"{prefix}缺少环节名称。", "补齐环节名称。"))
        if step.duration <= 0:
            issues.append(_issue("warning", "teaching_process", f"{prefix}缺少时长。", "填写预计用时。"))
        if not step.teacher_activity.strip():
            issues.append(
                _issue("warning", "teaching_process", f"{prefix}缺少教师活动。", "补写教师如何提问、讲解或组织活动。")
            )
        if not step.student_activity.strip():
            issues.append(
                _issue(
                    "warning",
                    "teaching_process",
                    f"{prefix}缺少学生活动。",
                    "补写学生要读、想、说、写或合作完成的任务。",
                )
            )
        if task.scene != "tutor" and not step.design_intent.strip():
            warnings.append(
                _issue("warning", "teaching_process", f"{prefix}缺少设计意图。", "公立校或机构提交前建议补齐设计意图。")
            )

    expected_minutes = max(task.class_hour, 1) * 40
    total_minutes = sum(step.duration for step in content.teaching_process)
    if total_minutes and abs(total_minutes - expected_minutes) > 15 * max(task.class_hour, 1):
        warnings.append(
            _issue(
                "warning",
                "teaching_process",
                f"教学过程总时长约 {total_minutes} 分钟，与课时不太匹配。",
                "按学校课时调整各环节时长。",
            )
        )
    if not content.preparation:
        warnings.append(
            _issue("warning", "preparation", "教学准备为空。", "如需提交正式教案，建议补充课件、音频、学习单等准备。")
        )
    if not content.board_design:
        warnings.append(
            _issue("warning", "board_design", "板书设计为空。", "建议补充能直接写到黑板上的关键词或结构图。")
        )
    if not content.reflection:
        suggestions.append(
            _issue("suggestion", "reflection", "教学反思为空，导出时会保留填写区。", "课后可直接在 Word 中补写。")
        )

    return _response(issues, warnings, suggestions)


def _check_study_guide(content: StudyGuideContent) -> QualityCheckResponse:
    issues: list[QualityIssue] = []
    warnings: list[QualityIssue] = []
    suggestions: list[QualityIssue] = []

    if not content.header.title:
        issues.append(_issue("blocker", "header", "缺少学案标题。", "补齐标题后再导出。"))
    _check_section_confirmation(
        issues,
        "learning_objectives",
        "学习目标",
        content.learning_objectives_status,
        bool(content.learning_objectives),
    )
    has_learning_process = bool(
        content.learning_process.self_study
        or content.learning_process.collaboration
        or content.learning_process.presentation
    )
    if not has_learning_process:
        issues.append(
            _issue(
                "warning",
                "learning_process",
                "学习流程为空。",
                "至少补充自主学习、合作探究或展示提升中的一类任务。",
            )
        )
    _check_section_confirmation(issues, "assessment", "达标测评", content.assessment_status, bool(content.assessment))

    if not content.extension:
        suggestions.append(_issue("suggestion", "extension", "拓展延伸为空。", "可按 D 级选做题补充拓展任务。"))
    for index, item in enumerate(content.assessment, start=1):
        if item.item_type != "short_answer" and not item.answer:
            warnings.append(
                _issue("warning", "assessment", f"达标测评第 {index} 题缺少答案。", "补齐答案，方便老师核对。")
            )

    return _response(issues, warnings, suggestions)


def _check_section_confirmation(
    issues: list[QualityIssue],
    section: str,
    title: str,
    status: str,
    has_content: bool,
) -> None:
    if not has_content:
        issues.append(_issue("warning", section, f"{title}为空。", f"补齐{title}后再导出。"))
        return
    if status != "confirmed":
        issues.append(
            _issue(
                "warning",
                section,
                f"{title}仍处于待确认，当前 Word 导出不会包含这部分内容。",
                f"确认{title}或改为已确认后再导出。",
            )
        )


def _response(
    issues: list[QualityIssue],
    warnings: list[QualityIssue],
    suggestions: list[QualityIssue],
) -> QualityCheckResponse:
    blockers = [item for item in issues if item.severity == "blocker"]
    if blockers:
        readiness = "blocked"
        summary = f"有 {len(blockers)} 个阻断问题，暂不建议直接导出。"
    elif issues or warnings:
        readiness = "needs_fixes"
        summary = f"有 {len(issues) + len(warnings)} 个提交前建议处理的问题。"
    else:
        readiness = "ready"
        summary = "导出前体检通过，可以导出 Word。"
    return QualityCheckResponse(
        readiness=readiness,
        summary=summary,
        issues=issues,
        warnings=warnings,
        suggestions=suggestions,
    )


def _issue(severity: str, section: str | None, message: str, suggestion: str) -> QualityIssue:
    return QualityIssue(
        severity=severity,  # type: ignore[arg-type]
        section=section,
        message=message,
        suggestion=suggestion,
    )
