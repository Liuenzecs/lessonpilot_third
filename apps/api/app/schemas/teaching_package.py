from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.content import StudyGuideContent


class PptSlideDraft(BaseModel):
    title: str
    bullets: list[str] = Field(default_factory=list)
    activity: str = ""
    speaker_note: str = ""
    status: str = "pending"


class TalkScriptDraft(BaseModel):
    opening: str = ""
    questions: list[str] = Field(default_factory=list)
    transitions: list[str] = Field(default_factory=list)
    closing: str = ""
    status: str = "pending"


class TeachingPackageContent(BaseModel):
    study_guide: StudyGuideContent
    ppt_outline: list[PptSlideDraft] = Field(default_factory=list)
    talk_script: TalkScriptDraft = Field(default_factory=TalkScriptDraft)


class TeachingPackageRead(BaseModel):
    id: str
    task_id: str
    document_id: str
    title: str
    status: str
    content: TeachingPackageContent
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
