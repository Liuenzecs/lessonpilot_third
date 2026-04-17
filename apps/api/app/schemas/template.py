from datetime import datetime

from pydantic import BaseModel, Field


class TemplateSectionBase(BaseModel):
    section_name: str
    order: int
    description: str | None = None
    prompt_hints: str | None = None
    schema_constraints: dict | None = None

class TemplateSectionCreate(TemplateSectionBase):
    pass

class TemplateSectionRead(TemplateSectionBase):
    id: str
    template_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TemplateBase(BaseModel):
    name: str
    subject: str
    grade: str
    description: str | None = None
    template_type: str = "lesson_plan"
    content: dict = Field(default_factory=dict)
    is_public: bool = False

class TemplateCreate(TemplateBase):
    sections: list[TemplateSectionCreate] | None = None

class TemplateRead(TemplateBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TemplateUpdate(BaseModel):
    name: str | None = None
    subject: str | None = None
    grade: str | None = None
    description: str | None = None
    template_type: str | None = None
    content: dict | None = None
    is_public: bool | None = None
