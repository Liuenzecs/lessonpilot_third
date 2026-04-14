from __future__ import annotations

from app.schemas.content import (
    LessonPlanContent,
    StudyGuideContent,
    create_empty_lesson_plan,
    create_empty_study_guide,
    is_lesson_plan,
    is_study_guide,
)


def test_lesson_plan_content_validates():
    payload = {
        "doc_type": "lesson_plan",
        "header": {
            "title": "春",
            "subject": "语文",
            "grade": "七年级",
            "classHour": 1,
            "lessonCategory": "new",
            "teacher": "",
        },
        "objectives": [
            {"dimension": "knowledge", "content": "理解课文内容"},
            {"dimension": "ability", "content": "掌握分析方法"},
        ],
        "objectives_status": "pending",
        "key_points": {
            "keyPoints": ["重点1"],
            "difficulties": ["难点1"],
        },
        "key_points_status": "pending",
        "preparation": ["课件"],
        "preparation_status": "pending",
        "teaching_process": [
            {
                "phase": "导入新课",
                "duration": 5,
                "teacher_activity": "引入课题",
                "student_activity": "思考",
                "design_intent": "激发兴趣",
            }
        ],
        "teaching_process_status": "pending",
        "board_design": "板书",
        "board_design_status": "pending",
        "reflection": "",
        "reflection_status": "pending",
    }
    content = LessonPlanContent.model_validate(payload)
    assert content.doc_type == "lesson_plan"
    assert len(content.objectives) == 2
    assert content.teaching_process[0].phase == "导入新课"
    assert content.objectives_status == "pending"


def test_study_guide_content_validates():
    payload = {
        "doc_type": "study_guide",
        "header": {
            "title": "春",
            "subject": "语文",
            "grade": "七年级",
            "className": "",
            "studentName": "",
            "date": "",
        },
        "learning_objectives": ["我能理解课文内容"],
        "learning_objectives_status": "pending",
        "key_difficulties": ["重点1"],
        "key_difficulties_status": "pending",
        "prior_knowledge": ["旧知识"],
        "prior_knowledge_status": "pending",
        "learning_process": {
            "selfStudy": [
                {
                    "level": "A",
                    "itemType": "short_answer",
                    "prompt": "概括主要内容",
                    "options": [],
                    "answer": "",
                    "analysis": "",
                }
            ],
            "collaboration": [],
            "presentation": [],
        },
        "self_study_status": "pending",
        "collaboration_status": "pending",
        "presentation_status": "pending",
        "assessment": [],
        "assessment_status": "pending",
        "extension": [],
        "extension_status": "pending",
        "self_reflection": "",
        "self_reflection_status": "pending",
    }
    content = StudyGuideContent.model_validate(payload)
    assert content.doc_type == "study_guide"
    assert len(content.learning_objectives) == 1
    assert content.learning_process.self_study[0].level == "A"


def test_create_empty_lesson_plan():
    content = create_empty_lesson_plan(
        subject="语文", grade="七年级", topic="春"
    )
    assert content.header.title == "春"
    assert content.header.subject == "语文"
    assert content.doc_type == "lesson_plan"
    assert is_lesson_plan(content)
    assert not is_study_guide(content)


def test_create_empty_study_guide():
    content = create_empty_study_guide(
        subject="语文", grade="七年级", topic="春"
    )
    assert content.header.title == "春"
    assert content.doc_type == "study_guide"
    assert is_study_guide(content)
    assert not is_lesson_plan(content)
