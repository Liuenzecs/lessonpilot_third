from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


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

    model_config = ConfigDict(from_attributes=True)

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
    user_id: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TemplateUpdate(BaseModel):
    name: str | None = None
    subject: str | None = None
    grade: str | None = None
    description: str | None = None
    template_type: str | None = None
    content: dict | None = None
    is_public: bool | None = None


class TemplateFieldMapping(BaseModel):
    template_label: str
    content_field: str
    confidence: float = 1.0
    location: str = "paragraph"


class TemplateTableLayout(BaseModel):
    name: str
    columns: list[str] = Field(default_factory=list)
    field_mappings: list[TemplateFieldMapping] = Field(default_factory=list)


class TemplatePreview(BaseModel):
    source_filename: str
    name: str
    subject: str = "语文"
    grade: str = ""
    template_type: str = "lesson_plan"
    field_mappings: list[TemplateFieldMapping] = Field(default_factory=list)
    section_order: list[str] = Field(default_factory=list)
    table_layouts: list[TemplateTableLayout] = Field(default_factory=list)
    blank_areas: list[str] = Field(default_factory=list)
    unsupported_items: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class TemplateConfirmPayload(BaseModel):
    preview: TemplatePreview
    name: str | None = None
    subject: str | None = None
    grade: str | None = None
