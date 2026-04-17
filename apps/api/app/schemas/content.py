"""教案 / 学案结构化内容模型。

替代旧的 8-block 体系，用明确的教案/学案结构化模型表达教学内容。
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# 公共类型
# ---------------------------------------------------------------------------

SectionStatus = Literal["confirmed", "pending"]

Scene = Literal["public_school", "tutor", "institution"]

LessonType = Literal["lesson_plan", "study_guide", "both"]

LessonCategory = Literal["new", "review", "exercise", "comprehensive"]


class TeachingObjective(BaseModel):
    """教学目标（三维目标或核心素养）。"""

    dimension: Literal["knowledge", "ability", "emotion"] = "knowledge"
    content: str = ""


class KeyPoints(BaseModel):
    """教学重难点。"""

    key_points: list[str] = Field(default_factory=list)
    difficulties: list[str] = Field(default_factory=list)


class TeachingProcessStep(BaseModel):
    """教学过程的一个环节。"""

    phase: str = ""
    duration: int = Field(default=5, description="分钟")
    teacher_activity: str = ""
    student_activity: str = ""
    design_intent: str = ""
    status: SectionStatus = "pending"


class AssessmentItem(BaseModel):
    """学案中的测评/练习题。"""

    level: Literal["A", "B", "C", "D"] = "A"
    item_type: Literal["choice", "fill_blank", "short_answer"] = Field(
        default="short_answer", alias="itemType"
    )
    prompt: str = ""
    options: list[str] = Field(default_factory=list)
    answer: str = ""
    analysis: str = ""

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# 教案内容模型
# ---------------------------------------------------------------------------


class LessonPlanHeader(BaseModel):
    """教案基本信息。"""

    title: str = ""
    subject: str = ""
    grade: str = ""
    class_hour: int = Field(default=1, alias="classHour")
    lesson_category: LessonCategory = Field(default="new", alias="lessonCategory")
    teacher: str = ""

    model_config = {"populate_by_name": True}


class LessonPlanContent(BaseModel):
    """教案完整内容。"""

    doc_type: Literal["lesson_plan"] = "lesson_plan"
    header: LessonPlanHeader = Field(default_factory=LessonPlanHeader)
    objectives: list[TeachingObjective] = Field(default_factory=list)
    objectives_status: SectionStatus = "pending"
    key_points: KeyPoints = Field(default_factory=KeyPoints)
    key_points_status: SectionStatus = "pending"
    preparation: list[str] = Field(default_factory=list)
    preparation_status: SectionStatus = "pending"
    teaching_process: list[TeachingProcessStep] = Field(default_factory=list)
    teaching_process_status: SectionStatus = "pending"
    board_design: str = ""
    board_design_status: SectionStatus = "pending"
    reflection: str = ""
    reflection_status: SectionStatus = "pending"


# ---------------------------------------------------------------------------
# 学案内容模型
# ---------------------------------------------------------------------------


class StudyGuideHeader(BaseModel):
    """学案基本信息。"""

    title: str = ""
    subject: str = ""
    grade: str = ""
    class_name: str = Field(default="", alias="className")
    student_name: str = Field(default="", alias="studentName")
    date: str = ""

    model_config = {"populate_by_name": True}


class LearningProcess(BaseModel):
    """学案学习流程（三段式）。"""

    self_study: list[AssessmentItem] = Field(default_factory=list, alias="selfStudy")
    collaboration: list[AssessmentItem] = Field(default_factory=list)
    presentation: list[AssessmentItem] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


class StudyGuideContent(BaseModel):
    """学案完整内容。"""

    doc_type: Literal["study_guide"] = "study_guide"
    header: StudyGuideHeader = Field(default_factory=StudyGuideHeader)
    learning_objectives: list[str] = Field(default_factory=list)
    learning_objectives_status: SectionStatus = "pending"
    key_difficulties: list[str] = Field(default_factory=list)
    key_difficulties_status: SectionStatus = "pending"
    prior_knowledge: list[str] = Field(default_factory=list)
    prior_knowledge_status: SectionStatus = "pending"
    learning_process: LearningProcess = Field(default_factory=LearningProcess)
    self_study_status: SectionStatus = "pending"
    collaboration_status: SectionStatus = "pending"
    presentation_status: SectionStatus = "pending"
    assessment: list[AssessmentItem] = Field(default_factory=list)
    assessment_status: SectionStatus = "pending"
    extension: list[AssessmentItem] = Field(default_factory=list)
    extension_status: SectionStatus = "pending"
    self_reflection: str = ""
    self_reflection_status: SectionStatus = "pending"


# ---------------------------------------------------------------------------
# 联合类型
# ---------------------------------------------------------------------------

DocumentContent = LessonPlanContent | StudyGuideContent


def is_lesson_plan(doc: DocumentContent) -> bool:
    return getattr(doc, "doc_type", None) == "lesson_plan"


def is_study_guide(doc: DocumentContent) -> bool:
    return getattr(doc, "doc_type", None) == "study_guide"


def create_empty_lesson_plan(
    *,
    subject: str = "",
    grade: str = "",
    topic: str = "",
    class_hour: int = 1,
    lesson_category: LessonCategory = "new",
) -> LessonPlanContent:
    """创建空的教案模板。"""
    return LessonPlanContent(
        header=LessonPlanHeader(
            title=topic,
            subject=subject,
            grade=grade,
            class_hour=class_hour,
            lesson_category=lesson_category,
        ),
        objectives=[],
        objectives_status="pending",
        key_points=KeyPoints(),
        key_points_status="pending",
        preparation=[],
        preparation_status="pending",
        teaching_process=[],
        teaching_process_status="pending",
        board_design="",
        board_design_status="pending",
        reflection="",
        reflection_status="pending",
    )


def create_empty_study_guide(
    *,
    subject: str = "",
    grade: str = "",
    topic: str = "",
) -> StudyGuideContent:
    """创建空的学案模板。"""
    return StudyGuideContent(
        header=StudyGuideHeader(
            title=topic,
            subject=subject,
            grade=grade,
        ),
        learning_objectives=[],
        learning_objectives_status="pending",
        key_difficulties=[],
        key_difficulties_status="pending",
        prior_knowledge=[],
        prior_knowledge_status="pending",
        learning_process=LearningProcess(),
        self_study_status="pending",
        collaboration_status="pending",
        presentation_status="pending",
        assessment=[],
        assessment_status="pending",
        extension=[],
        extension_status="pending",
        self_reflection="",
        self_reflection_status="pending",
    )
