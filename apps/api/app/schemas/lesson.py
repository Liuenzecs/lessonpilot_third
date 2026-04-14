"""教案 / 学案生成相关 schema。"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.content import LessonCategory, Scene


class GenerationContext(BaseModel):
    """AI 生成所需的上下文信息。"""

    subject: str
    grade: str
    topic: str
    requirements: str | None = None
    scene: Scene = "public_school"
    class_hour: int = 1
    lesson_category: LessonCategory = "new"


class SectionRewriteContext(BaseModel):
    """Section 级重写上下文。"""

    subject: str
    grade: str
    topic: str
    section_name: str
    current_content: str = Field(description="当前 section 的 JSON 内容")
    action: Literal["rewrite", "expand", "simplify"] = "rewrite"
    instruction: str | None = None
