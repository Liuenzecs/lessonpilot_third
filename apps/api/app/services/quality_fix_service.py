from __future__ import annotations

from fastapi import HTTPException, status
from sqlmodel import Session

from app.models import Document, Task
from app.schemas.content import AssessmentItem, LessonPlanContent, StudyGuideContent, TeachingObjective
from app.schemas.quality import QualityFixPayload
from app.services.document_service import load_content, save_document


def apply_quality_fix(
    session: Session,
    document: Document,
    task: Task,
    payload: QualityFixPayload,
) -> Document:
    content = load_content(document)
    if isinstance(content, StudyGuideContent):
        fixed_content = _fix_study_guide(content, payload)
    else:
        fixed_content = _fix_lesson_plan(content, task, payload)
    return save_document(session, document, fixed_content, snapshot_source="quality_fix")


def _fix_lesson_plan(
    content: LessonPlanContent,
    task: Task,
    payload: QualityFixPayload,
) -> LessonPlanContent:
    message = payload.message
    if payload.section == "objectives" or "目标" in message:
        return _fix_lesson_objectives(content, task)
    if payload.section == "key_points" or "重难点" in message:
        return _fix_key_points_in_process(content)
    if payload.section == "teaching_process" or "过程" in message or "学生活动" in message:
        return _fix_teaching_process(content)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前问题暂不支持自动调整")


def _fix_study_guide(content: StudyGuideContent, payload: QualityFixPayload) -> StudyGuideContent:
    message = payload.message
    if payload.section == "learning_objectives" or "学习目标" in message:
        objectives = [
            item if item.startswith("我能") else f"我能{item}"
            for item in content.learning_objectives
            if item.strip()
        ]
        return content.model_copy(
            update={
                "learning_objectives": objectives or ["我能说出本课核心内容", "我能完成课堂学习任务"],
                "learning_objectives_status": "pending",
            }
        )
    if payload.section == "assessment" or "测评" in message or "评价" in message:
        assessment = list(content.assessment)
        covered_text = " ".join(item.prompt for item in assessment)
        for objective in content.learning_objectives:
            if objective and objective not in covered_text:
                assessment.append(
                    AssessmentItem(
                        level="A",
                        itemType="short_answer",
                        prompt=f"围绕“{objective}”，写出你的课堂学习收获。",
                        answer="能结合本课内容作答即可。",
                        analysis="检测学习目标是否真正达成。",
                    )
                )
                break
        return content.model_copy(update={"assessment": assessment, "assessment_status": "pending"})
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前问题暂不支持自动调整")


def _fix_lesson_objectives(content: LessonPlanContent, task: Task) -> LessonPlanContent:
    topic = content.header.title or task.topic
    replacements = []
    defaults = [
        ("knowledge", f"朗读并概括《{topic}》的主要内容和关键细节"),
        ("ability", f"结合具体语句分析《{topic}》的表达特点"),
        ("emotion", f"用一段话表达学习《{topic}》后的阅读感受"),
    ]
    for index, objective in enumerate(content.objectives):
        text = objective.content.strip()
        if _is_generic_objective(text):
            dimension, content_text = defaults[min(index, len(defaults) - 1)]
            replacements.append(objective.model_copy(update={"dimension": dimension, "content": content_text}))
        else:
            replacements.append(objective)
    if not replacements:
        replacements = [
            TeachingObjective(dimension=dimension, content=content_text)
            for dimension, content_text in defaults[:2]
        ]
    return content.model_copy(update={"objectives": replacements, "objectives_status": "pending"})


def _fix_teaching_process(content: LessonPlanContent) -> LessonPlanContent:
    objectives_text = "；".join(item.content for item in content.objectives[:2] if item.content)
    key_terms = "、".join(content.key_points.key_points + content.key_points.difficulties)
    updated_steps = []
    for index, step in enumerate(content.teaching_process):
        student_activity = step.student_activity.strip()
        if not student_activity or student_activity in {"听讲", "认真听讲", "思考", "回答问题"}:
            student_activity = "朗读课文，圈画关键词，小组交流后用完整句表达发现。"
        teacher_activity = step.teacher_activity.strip() or "提出核心问题，组织学生朗读、圈画、交流和展示。"
        design_intent = step.design_intent.strip() or "让目标在课堂任务中被看见、能检查。"
        if index == 0 and objectives_text and objectives_text not in teacher_activity:
            teacher_activity = f"{teacher_activity} 明确本环节对应目标：{objectives_text}。"
        if key_terms and key_terms not in design_intent:
            design_intent = f"{design_intent} 承接本课重难点：{key_terms}。"
        updated_steps.append(
            step.model_copy(
                update={
                    "teacher_activity": teacher_activity,
                    "student_activity": student_activity,
                    "design_intent": design_intent,
                    "status": "pending",
                }
            )
        )
    if not updated_steps:
        updated_steps = []
    return content.model_copy(update={"teaching_process": updated_steps, "teaching_process_status": "pending"})


def _fix_key_points_in_process(content: LessonPlanContent) -> LessonPlanContent:
    if not content.teaching_process:
        return _fix_teaching_process(content)
    key_terms = "、".join(content.key_points.key_points + content.key_points.difficulties)
    first_step = content.teaching_process[0]
    updated_first = first_step.model_copy(
        update={
            "teacher_activity": f"{first_step.teacher_activity} 聚焦本课重难点：{key_terms}。",
            "design_intent": f"{first_step.design_intent} 让学生先整体感知重难点，再进入细读。",
            "status": "pending",
        }
    )
    return content.model_copy(
        update={
            "teaching_process": [updated_first, *content.teaching_process[1:]],
            "teaching_process_status": "pending",
        }
    )


def _is_generic_objective(value: str) -> bool:
    if not value:
        return True
    generic_phrases = ["提高综合素养", "培养学习兴趣", "提升核心素养", "掌握相关知识", "提高能力"]
    action_verbs = ["说出", "概括", "分析", "比较", "解释", "品味", "朗读", "背诵", "运用", "表达"]
    return any(phrase in value for phrase in generic_phrases) or not any(verb in value for verb in action_verbs)
