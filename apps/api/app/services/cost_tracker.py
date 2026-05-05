"""LLM 调用成本追踪服务。"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from sqlmodel import Session, func, select

from app.core.config import get_settings
from app.models.cost_log import CostLog

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class _CostRate:
    prompt_per_1k: float
    completion_per_1k: float


def _get_cost_rates(provider: str) -> _CostRate:
    s = get_settings()
    if provider == "deepseek":
        return _CostRate(
            prompt_per_1k=s.cost_rate_deepseek_prompt_per_1k,
            completion_per_1k=s.cost_rate_deepseek_completion_per_1k,
        )
    if provider == "minimax":
        return _CostRate(
            prompt_per_1k=s.cost_rate_minimax_prompt_per_1k,
            completion_per_1k=s.cost_rate_minimax_completion_per_1k,
        )
    return _CostRate(prompt_per_1k=0.0, completion_per_1k=0.0)


def _calculate_cost_cny(provider: str, prompt_tokens: int, completion_tokens: int) -> float:
    rates = _get_cost_rates(provider)
    cost = (prompt_tokens / 1000.0) * rates.prompt_per_1k
    cost += (completion_tokens / 1000.0) * rates.completion_per_1k
    return round(cost, 6)


def log_llm_usage(
    *,
    session: Session,
    user_id: str,
    provider: str,
    model: str,
    operation: str,
    prompt_tokens: int,
    completion_tokens: int,
    total_tokens: int,
    task_id: str | None = None,
    doc_type: str | None = None,
    section_name: str | None = None,
    error: str | None = None,
) -> CostLog:
    """记录一次 LLM 调用的 token 消耗和估算成本。"""
    cost_cny = _calculate_cost_cny(provider, prompt_tokens, completion_tokens)
    entry = CostLog(
        user_id=user_id,
        provider=provider,
        model=model,
        operation=operation,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        cost_cny=cost_cny,
        task_id=task_id,
        doc_type=doc_type,
        section_name=section_name,
        error=error,
    )
    session.add(entry)
    logger.debug(
        "LLM cost: user=%s op=%s tokens=%d cost=¥%.4f",
        user_id,
        operation,
        total_tokens,
        cost_cny,
    )
    return entry


def get_user_usage_today(*, session: Session, user_id: str) -> int:
    """返回用户今日生成次数（按 cost_logs 记录计数）。"""
    from datetime import UTC, datetime

    start_of_day = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    count_stmt = select(func.count(CostLog.id)).where(
        CostLog.user_id == user_id,
        CostLog.created_at >= start_of_day,
        CostLog.operation == "generate_section",
    )
    return session.exec(count_stmt).one()


def get_user_usage_this_month(*, session: Session, user_id: str) -> int:
    """返回用户本月生成次数。"""
    from datetime import UTC, datetime

    now = datetime.now(UTC)
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    count_stmt = select(func.count(CostLog.id)).where(
        CostLog.user_id == user_id,
        CostLog.created_at >= start_of_month,
        CostLog.operation == "generate_section",
    )
    return session.exec(count_stmt).one()


def get_user_cost_this_month(*, session: Session, user_id: str) -> float:
    """返回用户本月的 AI 调用总成本。"""
    from datetime import UTC, datetime

    now = datetime.now(UTC)
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    cost_stmt = select(func.coalesce(func.sum(CostLog.cost_cny), 0.0)).where(
        CostLog.user_id == user_id,
        CostLog.created_at >= start_of_month,
    )
    return float(session.exec(cost_stmt).one())


def get_total_cost_this_month(*, session: Session) -> float:
    """返回本月所有用户的 AI 调用总成本。"""
    from datetime import UTC, datetime

    now = datetime.now(UTC)
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    cost_stmt = select(func.coalesce(func.sum(CostLog.cost_cny), 0.0)).where(
        CostLog.created_at >= start_of_month,
    )
    return float(session.exec(cost_stmt).one())
