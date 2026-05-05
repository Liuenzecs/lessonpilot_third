"""Analytics event schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AnalyticsEventPayload(BaseModel):
    event_name: str = Field(max_length=80)
    source: str = Field(default="web", max_length=16)
    user_id: str | None = None
    anonymous_id: str | None = Field(default=None, max_length=64)
    session_id: str = Field(max_length=64)
    page_path: str = Field(default="/", max_length=500)
    referrer: str | None = None
    properties: dict = Field(default_factory=dict)
    client_event_id: str | None = Field(default=None, max_length=120)
