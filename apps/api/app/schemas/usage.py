"""Usage stats schemas."""

from __future__ import annotations

from pydantic import BaseModel


class UserUsageResponse(BaseModel):
    generations_today: int
    generations_this_month: int
    daily_limit: int
    monthly_limit: int
    cost_this_month: float
