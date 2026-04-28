"""班级组 schema。"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ClassGroupCreate(BaseModel):
    name: str = Field(max_length=120)
    level: str = Field(default="standard", max_length=32)
    notes: str | None = Field(default=None, max_length=2000)


class ClassGroupUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=120)
    level: str | None = Field(default=None, max_length=32)
    notes: str | None = Field(default=None, max_length=2000)


class ClassGroupRead(BaseModel):
    id: str
    user_id: str
    name: str
    level: str
    notes: str | None = None
    created_at: datetime
    updated_at: datetime


class CreateVariantRequest(BaseModel):
    class_group_id: str
    differentiation_level: str = Field(
        default="moderate",
        description="轻度(light) / 中度(moderate) / 重度(heavy)",
    )
