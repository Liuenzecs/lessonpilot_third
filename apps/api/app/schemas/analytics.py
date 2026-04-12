from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

AnalyticsSource = Literal["client", "server"]


class AnalyticsEventCreate(BaseModel):
    event_name: str = Field(min_length=2, max_length=80)
    occurred_at: datetime
    source: AnalyticsSource = "client"
    anonymous_id: str | None = Field(default=None, max_length=64)
    session_id: str = Field(min_length=8, max_length=64)
    page_path: str = Field(min_length=1, max_length=500)
    referrer: str | None = Field(default=None, max_length=2000)
    properties: dict[str, Any] = Field(default_factory=dict)
    client_event_id: str = Field(min_length=4, max_length=120)


class AnalyticsBatchPayload(BaseModel):
    events: list[AnalyticsEventCreate] = Field(min_length=1, max_length=100)


class AnalyticsBatchResponse(BaseModel):
    accepted: int
    deduplicated: int
