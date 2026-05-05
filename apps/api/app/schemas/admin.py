"""Admin API schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class AdminUserSummary(BaseModel):
    id: str
    email: str
    name: str
    role: str
    is_disabled: bool
    email_verified: bool
    created_at: datetime
    gens_today: int = 0
    gens_this_month: int = 0
    cost_this_month: float = 0.0


class AdminUserListResponse(BaseModel):
    users: list[AdminUserSummary]
    total: int
    page: int
    limit: int


class AdminDisableUserPayload(BaseModel):
    reason: str = ""


class AdminStatsResponse(BaseModel):
    total_users: int
    active_users_7d: int
    active_users_30d: int
    total_generations_today: int
    total_generations_this_month: int
    cost_today: float
    cost_this_month: float
    budget_status: dict
