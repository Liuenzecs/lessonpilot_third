from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field


class BlockBase(BaseModel):
    id: str
    status: Literal["confirmed", "pending"]
    source: Literal["human", "ai"]


class ParagraphBlock(BlockBase):
    type: Literal["paragraph"] = "paragraph"
    content: str = ""


class ListBlock(BlockBase):
    type: Literal["list"] = "list"
    items: list[str] = Field(default_factory=list)


class SectionBlock(BlockBase):
    type: Literal["section"] = "section"
    title: str
    children: list["Block"] = Field(default_factory=list)


class TeachingStepBlock(BlockBase):
    type: Literal["teaching_step"] = "teaching_step"
    title: str
    duration_minutes: int | None = Field(default=None, alias="durationMinutes")
    children: list["Block"] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


Block = Annotated[
    ParagraphBlock | ListBlock | SectionBlock | TeachingStepBlock,
    Field(discriminator="type"),
]

SectionBlock.model_rebuild()
TeachingStepBlock.model_rebuild()


class ContentDocument(BaseModel):
    version: int = 1
    blocks: list[Block] = Field(default_factory=list)


class GeneratedBlocksPayload(BaseModel):
    blocks: list[Block] = Field(default_factory=list)

