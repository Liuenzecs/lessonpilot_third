"""课件服务测试。"""

from __future__ import annotations

import pytest

from app.schemas.content import (
    KeyPoints,
    LessonPlanContent,
    TeachingObjective,
    TeachingProcessStep,
)
from app.services.courseware_service import build_pptx, generate_slide_outline


def _make_task(**kwargs):
    """构造一个模拟 Task 对象用于测试。"""

    class FakeTask:
        pass

    t = FakeTask()
    t.subject = kwargs.get("subject", "语文")
    t.grade = kwargs.get("grade", "七年级上")
    t.class_hour = kwargs.get("class_hour", 1)
    t.title = kwargs.get("title", "测试课题")
    t.topic = kwargs.get("topic", "测试课题")
    t.lesson_category = kwargs.get("lesson_category", "new")
    t.scene = kwargs.get("scene", "public_school")
    return t


def _make_minimal_content() -> LessonPlanContent:
    return LessonPlanContent(
        doc_type="lesson_plan",
        header={
            "title": "春",
            "subject": "语文",
            "grade": "七年级上",
            "classHour": 1,
            "lessonCategory": "new",
            "teacher": "测试老师",
        },
        objectives=[TeachingObjective(dimension="knowledge", content="理解文章结构和写景手法")],
        objectives_status="confirmed",
        key_points=KeyPoints(key_points=["写景手法分析"], difficulties=["修辞手法的体会"]),
        key_points_status="confirmed",
        preparation=["多媒体课件"],
        preparation_status="confirmed",
        teaching_process=[
            TeachingProcessStep(
                phase="导入",
                duration=5,
                teacher_activity="展示春天图片。提问：你眼中的春天是什么样的？",
                student_activity="学生观察图片并自由发言。",
                design_intent="激发学生兴趣，引入课文。",
            ),
            TeachingProcessStep(
                phase="初读感知",
                duration=10,
                teacher_activity="引导学生朗读课文。",
                student_activity="学生自由朗读并圈画生字词。",
                design_intent="整体感知课文内容。",
            ),
        ],
        teaching_process_status="confirmed",
        board_design="春\n一、春草图\n二、春花图\n三、春风图",
        board_design_status="confirmed",
        reflection="",
        reflection_status="pending",
        section_references={},
    )


class TestGenerateSlideOutline:
    def test_generates_title_slide(self):
        task = _make_task()
        content = _make_minimal_content()
        slides = generate_slide_outline(task, content)
        assert any(s.slide_type == "title" for s in slides)
        title_slide = next(s for s in slides if s.slide_type == "title")
        assert "春" in title_slide.title

    def test_generates_objectives_slide(self):
        task = _make_task()
        content = _make_minimal_content()
        slides = generate_slide_outline(task, content)
        assert any(s.slide_type == "objectives" for s in slides)

    def test_teaching_process_creates_one_slide_per_step(self):
        task = _make_task()
        content = _make_minimal_content()
        slides = generate_slide_outline(task, content)
        step_slides = [s for s in slides if s.slide_type == "teaching_step"]
        assert len(step_slides) == len(content.teaching_process)

    def test_includes_summary_slide(self):
        task = _make_task()
        content = _make_minimal_content()
        slides = generate_slide_outline(task, content)
        assert any(s.slide_type == "summary" for s in slides)

    def test_includes_homework_slide(self):
        task = _make_task()
        content = _make_minimal_content()
        slides = generate_slide_outline(task, content)
        assert any(s.slide_type == "homework" for s in slides)

    def test_extracts_questions_from_process(self):
        task = _make_task()
        content = _make_minimal_content()
        slides = generate_slide_outline(task, content)
        q_slides = [s for s in slides if s.slide_type == "questions"]
        assert len(q_slides) == 1
        assert len(q_slides[0].bullet_points) > 0

    def test_skips_pending_sections(self):
        task = _make_task()
        content = _make_minimal_content()
        content.objectives_status = "pending"
        content.key_points_status = "pending"
        content.teaching_process_status = "pending"
        content.board_design_status = "pending"
        slides = generate_slide_outline(task, content)
        # 只有 title + homework 始终存在
        types = {s.slide_type for s in slides}
        assert types == {"title", "homework"}


class TestBuildPptx:
    def test_builds_pptx_bytes(self):
        task = _make_task()
        content = _make_minimal_content()
        result = build_pptx(task, content)
        assert isinstance(result, bytes)
        assert len(result) > 0
        # PPTX 文件以 ZIP 格式开头（PK 签名）
        assert result[:2] == b"PK"

    def test_pptx_rejects_study_guide(self):
        from app.schemas.content import StudyGuideContent

        task = _make_task()
        sg = StudyGuideContent(
            doc_type="study_guide",
            header={
                "title": "测试学案",
                "subject": "语文",
                "grade": "七年级上",
                "className": "一班",
                "studentName": "",
                "date": "",
            },
            learning_objectives=[],
            learning_objectives_status="pending",
            key_difficulties=[],
            key_difficulties_status="pending",
            prior_knowledge=[],
            prior_knowledge_status="pending",
            learning_process={"selfStudy": [], "collaboration": [], "presentation": []},
            self_study_status="pending",
            collaboration_status="pending",
            presentation_status="pending",
            assessment=[],
            assessment_status="pending",
            extension=[],
            extension_status="pending",
            self_reflection="",
            self_reflection_status="pending",
            section_references={},
        )
        with pytest.raises(ValueError, match="only supported for lesson plans"):
            build_pptx(task, sg)
