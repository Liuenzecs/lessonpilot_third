from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field, model_validator


class BlockSuggestion(BaseModel):
    kind: Literal["append", "replace"]
    target_block_id: str | None = Field(default=None, alias="targetBlockId")
    action: Literal["rewrite", "polish", "expand"] | None = None

    model_config = {"populate_by_name": True}

    @model_validator(mode="after")
    def validate_replace_metadata(self) -> "BlockSuggestion":
        if self.kind == "replace":
            if not self.target_block_id:
                raise ValueError("replace suggestion requires targetBlockId")
            if self.action is None:
                raise ValueError("replace suggestion requires action")
        if self.kind == "append":
            self.target_block_id = None
            self.action = None
        return self


class BlockBase(BaseModel):
    id: str
    status: Literal["confirmed", "pending"]
    source: Literal["human", "ai"]
    suggestion: BlockSuggestion | None = None

    model_config = {"populate_by_name": True}


class ParagraphBlock(BlockBase):
    type: Literal["paragraph"] = "paragraph"
    content: str = ""


class ListBlock(BlockBase):
    type: Literal["list"] = "list"
    items: list[str] = Field(default_factory=list)


class ChoiceQuestionBlock(BlockBase):
    type: Literal["choice_question"] = "choice_question"
    prompt: str = ""
    options: list[str] = Field(default_factory=list)
    answers: list[str] = Field(default_factory=list)
    analysis: str = ""


class FillBlankQuestionBlock(BlockBase):
    type: Literal["fill_blank_question"] = "fill_blank_question"
    prompt: str = ""
    answers: list[str] = Field(default_factory=list)
    analysis: str = ""


class ShortAnswerQuestionBlock(BlockBase):
    type: Literal["short_answer_question"] = "short_answer_question"
    prompt: str = ""
    reference_answer: str = Field(default="", alias="referenceAnswer")
    analysis: str = ""

    model_config = {"populate_by_name": True}


TeachingStepChild = Annotated[
    ParagraphBlock | ListBlock,
    Field(discriminator="type"),
]


class TeachingStepBlock(BlockBase):
    type: Literal["teaching_step"] = "teaching_step"
    title: str
    duration_minutes: int | None = Field(default=None, alias="durationMinutes")
    children: list[TeachingStepChild] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


ExerciseQuestionBlock = Annotated[
    ChoiceQuestionBlock | FillBlankQuestionBlock | ShortAnswerQuestionBlock,
    Field(discriminator="type"),
]


class ExerciseGroupBlock(BlockBase):
    type: Literal["exercise_group"] = "exercise_group"
    title: str
    children: list[ExerciseQuestionBlock] = Field(default_factory=list)


SectionChild = Annotated[
    ParagraphBlock | ListBlock | TeachingStepBlock | ExerciseGroupBlock,
    Field(discriminator="type"),
]


class SectionBlock(BlockBase):
    type: Literal["section"] = "section"
    title: str
    children: list[SectionChild] = Field(default_factory=list)


Block = Annotated[
    SectionBlock
    | ParagraphBlock
    | ListBlock
    | TeachingStepBlock
    | ExerciseGroupBlock
    | ChoiceQuestionBlock
    | FillBlankQuestionBlock
    | ShortAnswerQuestionBlock,
    Field(discriminator="type"),
]


class ContentDocument(BaseModel):
    version: int = 1
    blocks: list[Block] = Field(default_factory=list)


class GeneratedBlocksPayload(BaseModel):
    blocks: list[Block] = Field(default_factory=list)
