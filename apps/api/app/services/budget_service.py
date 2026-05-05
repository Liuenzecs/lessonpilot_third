"""月度成本预算监控服务。"""

from __future__ import annotations

import logging

from sqlmodel import Session

from app.core.config import get_settings
from app.services.cost_tracker import get_total_cost_this_month

logger = logging.getLogger(__name__)


def check_budget_status(*, session: Session) -> dict:
    """检查本月成本预算状态，返回 { status, cost_month, budget, percent }。"""
    settings = get_settings()
    budget = settings.cost_monthly_budget_cny
    if budget <= 0:
        return {"status": "ok", "cost_month": 0, "budget": 0, "percent": 0}

    cost_month = get_total_cost_this_month(session=session)
    percent = (cost_month / budget) * 100 if budget > 0 else 0

    if percent >= 95:
        status = "critical"
    elif percent >= 80:
        status = "warning"
    else:
        status = "ok"

    if status != "ok":
        logger.warning(
            "Budget %s: ¥%.2f / ¥%.2f (%.1f%%)",
            status,
            cost_month,
            budget,
            percent,
        )

    return {
        "status": status,
        "cost_month": round(cost_month, 4),
        "budget": budget,
        "percent": round(percent, 1),
    }


def is_generation_throttled(*, session: Session) -> bool:
    """预算达到 critical 时，建议限制新生成。"""
    status = check_budget_status(session=session)
    return status["status"] == "critical"
