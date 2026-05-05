"""用户生成配额服务。"""

from __future__ import annotations

from app.core.config import get_settings
from app.services.cost_tracker import get_user_usage_today, get_user_usage_this_month


class QuotaExceededError(Exception):
    def __init__(self, message: str, remaining: int = 0):
        super().__init__(message)
        self.remaining = remaining


def check_user_quota(*, session, user_id: str) -> None:
    """检查用户是否超过日/月生成配额。超限时抛 QuotaExceededError。"""
    settings = get_settings()
    if not settings.quota_enabled:
        return

    today_count = get_user_usage_today(session=session, user_id=user_id)
    if today_count >= settings.daily_generation_limit:
        raise QuotaExceededError(
            f"今日生成次数已达上限（{settings.daily_generation_limit} 次），请明天再试。",
            remaining=0,
        )

    month_count = get_user_usage_this_month(session=session, user_id=user_id)
    if month_count >= settings.monthly_generation_limit:
        raise QuotaExceededError(
            f"本月生成次数已达上限（{settings.monthly_generation_limit} 次），请下月再试。",
            remaining=0,
        )


def get_user_quota_summary(*, session, user_id: str) -> dict:
    """返回用户当前配额使用情况。"""
    settings = get_settings()
    return {
        "generations_today": get_user_usage_today(session=session, user_id=user_id),
        "generations_this_month": get_user_usage_this_month(session=session, user_id=user_id),
        "daily_limit": settings.daily_generation_limit,
        "monthly_limit": settings.monthly_generation_limit,
    }
