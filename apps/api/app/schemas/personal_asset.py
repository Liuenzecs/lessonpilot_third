from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

AssetType = Literal["lesson_plan", "study_guide", "ppt_outline", "teaching_note", "reference_material"]


class ExtractedAssetSection(BaseModel):
    title: str
    content: str
    section_type: str = "unknown"


class ReuseSuggestion(BaseModel):
    target: str
    label: str
    reason: str


class PersonalAssetPreview(BaseModel):
    source_filename: str
    file_type: Literal["docx", "pptx"]
    title: str
    subject: str = "语文"
    grade: str = ""
    topic: str = ""
    asset_type: AssetType
    extracted_sections: list[ExtractedAssetSection] = Field(default_factory=list)
    unmapped_sections: list[ExtractedAssetSection] = Field(default_factory=list)
    reuse_suggestions: list[ReuseSuggestion] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class PersonalAssetConfirmPayload(BaseModel):
    preview: PersonalAssetPreview
    title: str | None = None
    subject: str | None = None
    grade: str | None = None
    topic: str | None = None
    asset_type: AssetType | None = None


class PersonalAssetRead(BaseModel):
    id: str
    title: str
    asset_type: str
    source_filename: str
    file_type: str
    subject: str
    grade: str
    topic: str
    extracted_content: dict
    reuse_suggestions: list[dict]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
