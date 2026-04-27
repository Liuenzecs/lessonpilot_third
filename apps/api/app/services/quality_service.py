from __future__ import annotations

from app.models import Task
from app.schemas.content import DocumentContent, LessonPlanContent, StudyGuideContent
from app.schemas.quality import AlignmentMapItem, QualityCheckResponse, QualityIssue

GENERIC_PHRASES = [
    "提高综合素养",
    "培养学习兴趣",
    "提升核心素养",
    "掌握相关知识",
    "提高能力",
]

ACTION_VERBS = [
    "说出",
    "概括",
    "分析",
    "比较",
    "解释",
    "品味",
    "朗读",
    "背诵",
    "运用",
    "表达",
    "评价",
    "理解",
    "掌握",
    "学习",
    "感受",
]


def check_export_quality(task: Task, content: DocumentContent) -> QualityCheckResponse:
    if getattr(content, "doc_type", "") == "study_guide":
        return _check_study_guide(content)  # type: ignore[arg-type]
    return _check_lesson_plan(task, content)  # type: ignore[arg-type]


def _check_lesson_plan(task: Task, content: LessonPlanContent) -> QualityCheckResponse:
    issues: list[QualityIssue] = []
    warnings: list[QualityIssue] = []
    suggestions: list[QualityIssue] = []
    alignment_map = _lesson_alignment_map(content)

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
    _check_objective_quality(warnings, suggestions, content)
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

    _check_alignment_quality(warnings, suggestions, content, alignment_map)
    _check_key_points_in_process(warnings, content)
    _check_student_activity_quality(warnings, content)

    return _response(issues, warnings, suggestions, alignment_map)


def _check_study_guide(content: StudyGuideContent) -> QualityCheckResponse:
    issues: list[QualityIssue] = []
    warnings: list[QualityIssue] = []
    suggestions: list[QualityIssue] = []
    alignment_map = _study_guide_alignment_map(content)

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
    _check_study_guide_alignment(warnings, suggestions, content, alignment_map)

    if not content.extension:
        suggestions.append(_issue("suggestion", "extension", "拓展延伸为空。", "可按 D 级选做题补充拓展任务。"))
    for index, item in enumerate(content.assessment, start=1):
        if item.item_type != "short_answer" and not item.answer:
            warnings.append(
                _issue("warning", "assessment", f"达标测评第 {index} 题缺少答案。", "补齐答案，方便老师核对。")
            )

    return _response(issues, warnings, suggestions, alignment_map)


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
    alignment_map: list[AlignmentMapItem] | None = None,
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
        alignment_map=alignment_map or [],
    )


def _issue(severity: str, section: str | None, message: str, suggestion: str) -> QualityIssue:
    return QualityIssue(
        severity=severity,  # type: ignore[arg-type]
        section=section,
        message=message,
        suggestion=suggestion,
    )


def _check_objective_quality(
    warnings: list[QualityIssue],
    suggestions: list[QualityIssue],
    content: LessonPlanContent,
) -> None:
    for index, objective in enumerate(content.objectives, start=1):
        text = objective.content.strip()
        if any(phrase in text for phrase in GENERIC_PHRASES):
            warnings.append(
                _issue(
                    "warning",
                    "objectives",
                    f"教学目标第 {index} 条表述偏空泛。",
                    "改成学生课后能说出、分析、朗读、表达的具体表现。",
                )
            )
        elif text and not any(verb in text for verb in ACTION_VERBS):
            suggestions.append(
                _issue(
                    "suggestion",
                    "objectives",
                    f"教学目标第 {index} 条可评价性较弱。",
                    "加入“说出、分析、比较、运用”等可观察动作。",
                )
            )


def _check_alignment_quality(
    warnings: list[QualityIssue],
    suggestions: list[QualityIssue],
    content: LessonPlanContent,
    alignment_map: list[AlignmentMapItem],
) -> None:
    if not content.objectives or not content.teaching_process:
        return
    missing = [item for item in alignment_map if item.status == "missing"]
    if len(missing) == len(alignment_map):
        warnings.append(
            _issue(
                "warning",
                "teaching_process",
                "教学过程没有明显承接教学目标。",
                "在教学过程的提问、朗读、讨论或练习中对应写出每条目标如何落实。",
            )
        )
    elif missing:
        suggestions.append(
            _issue(
                "suggestion",
                "teaching_process",
                f"有 {len(missing)} 条教学目标在过程中对应不够明显。",
                "给相关环节补一句具体任务或评价方式。",
            )
        )


def _check_key_points_in_process(warnings: list[QualityIssue], content: LessonPlanContent) -> None:
    if not content.teaching_process:
        return
    process_text = _lesson_process_text(content)
    key_terms = _keywords(" ".join(content.key_points.key_points + content.key_points.difficulties))
    if key_terms and not any(term in process_text for term in key_terms):
        warnings.append(
            _issue(
                "warning",
                "key_points",
                "教学重难点没有在教学过程中明显展开。",
                "把重点和难点放进对应环节的问题、活动或板书中。",
            )
        )


def _check_student_activity_quality(warnings: list[QualityIssue], content: LessonPlanContent) -> None:
    if not content.teaching_process:
        return
    passive = 0
    for step in content.teaching_process:
        activity = step.student_activity.strip()
        if not activity or activity in {"听讲", "认真听讲", "思考", "回答问题"}:
            passive += 1
    if passive == len(content.teaching_process):
        warnings.append(
            _issue(
                "warning",
                "teaching_process",
                "学生活动整体偏被动。",
                "至少补充朗读、圈画、讨论、写作、展示等可观察任务。",
            )
        )


def _check_study_guide_alignment(
    warnings: list[QualityIssue],
    suggestions: list[QualityIssue],
    content: StudyGuideContent,
    alignment_map: list[AlignmentMapItem],
) -> None:
    for index, objective in enumerate(content.learning_objectives, start=1):
        if objective and not objective.startswith("我能"):
            warnings.append(
                _issue("warning", "learning_objectives", f"学习目标第 {index} 条不是学生口吻。", "改为“我能...”表述。")
            )
    missing = [item for item in alignment_map if item.status == "missing"]
    if content.learning_objectives and content.assessment and len(missing) == len(alignment_map):
        warnings.append(
            _issue(
                "warning",
                "assessment",
                "达标测评没有明显覆盖学习目标。",
                "为每条核心目标配置一道检测题或课堂任务。",
            )
        )
    elif missing:
        suggestions.append(
            _issue("suggestion", "assessment", f"有 {len(missing)} 条学习目标测评覆盖不够明显。", "补充对应检测题。")
        )


def _lesson_alignment_map(content: LessonPlanContent) -> list[AlignmentMapItem]:
    process_text = _lesson_process_text(content)
    items: list[AlignmentMapItem] = []
    for objective in content.objectives:
        keywords = _keywords(objective.content)
        matches = [step.phase for step in content.teaching_process if _text_has_keyword(_step_text(step), keywords)]
        status = "covered" if matches else "missing"
        items.append(
            AlignmentMapItem(
                objective=objective.content,
                process_matches=matches,
                assessment_matches=[],
                status=status if _text_has_keyword(process_text, keywords) else "missing",
            )
        )
    return items


def _study_guide_alignment_map(content: StudyGuideContent) -> list[AlignmentMapItem]:
    process_text = " ".join(
        item.prompt
        for item in content.learning_process.self_study
        + content.learning_process.collaboration
        + content.learning_process.presentation
    )
    assessment_text = " ".join(item.prompt for item in content.assessment)
    items: list[AlignmentMapItem] = []
    for objective in content.learning_objectives:
        keywords = _keywords(objective)
        process_matches = ["学习流程"] if _text_has_keyword(process_text, keywords) else []
        assessment_matches = ["达标测评"] if _text_has_keyword(assessment_text, keywords) else []
        status = "covered" if assessment_matches else "partial" if process_matches else "missing"
        items.append(
            AlignmentMapItem(
                objective=objective,
                process_matches=process_matches,
                assessment_matches=assessment_matches,
                status=status,
            )
        )
    return items


def _lesson_process_text(content: LessonPlanContent) -> str:
    return " ".join(_step_text(step) for step in content.teaching_process)


def _step_text(step) -> str:
    return " ".join([step.phase, step.teacher_activity, step.student_activity, step.design_intent])


def _keywords(value: str) -> list[str]:
    cleaned = value
    for word in ["学生", "能够", "通过", "学习", "理解", "掌握", "提高", "培养", "我能", "本课", "课文", "内容"]:
        cleaned = cleaned.replace(word, " ")
    tokens = re_split_keywords(cleaned)
    return [token for token in tokens if len(token) >= 2][:6]


def _text_has_keyword(text: str, keywords: list[str]) -> bool:
    return bool(keywords) and any(keyword in text for keyword in keywords)


def re_split_keywords(value: str) -> list[str]:
    import re

    return [item for item in re.split(r"[\s，。、“”《》；;：:、,.]+", value) if item]
