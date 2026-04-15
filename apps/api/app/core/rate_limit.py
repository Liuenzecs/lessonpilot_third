"""轻量内存级限流中间件。

基于 sliding window 计数，无需外部依赖（Redis 等）。
适合单实例部署；多实例部署需替换为 Redis 后端。
"""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.core.config import get_settings

# ---------------------------------------------------------------------------
# Sliding Window 计数器
# ---------------------------------------------------------------------------


@dataclass
class _SlidingWindow:
    """简单滑动窗口计数器。"""

    limit: int
    window_seconds: int
    timestamps: list[float] = field(default_factory=list)

    def is_allowed(self) -> bool:
        now = time.monotonic()
        cutoff = now - self.window_seconds
        self.timestamps = [ts for ts in self.timestamps if ts > cutoff]
        if len(self.timestamps) >= self.limit:
            return False
        self.timestamps.append(now)
        return True


@dataclass
class _RateLimitRule:
    """限流规则：按 key 前缀 + limit + window。"""

    key_prefix: str
    limit: int
    window_seconds: int


# ---------------------------------------------------------------------------
# 限流存储
# ---------------------------------------------------------------------------

_buckets: dict[str, _SlidingWindow] = defaultdict(lambda: _SlidingWindow(0, 0))


def _get_or_create_bucket(key: str, limit: int, window_seconds: int) -> _SlidingWindow:
    bucket = _buckets.get(key)
    if bucket is None:
        bucket = _SlidingWindow(limit=limit, window_seconds=window_seconds)
        _buckets[key] = bucket
    return bucket


def reset_buckets() -> None:
    """清空所有限流计数器（测试用）。"""
    _buckets.clear()


# ---------------------------------------------------------------------------
# 路由 → 限流规则映射
# ---------------------------------------------------------------------------


def _build_rules() -> list[_RateLimitRule]:
    settings = get_settings()
    return [
        _RateLimitRule(
            key_prefix="login",
            limit=settings.rate_limit_login_per_minute,
            window_seconds=60,
        ),
        _RateLimitRule(
            key_prefix="generation",
            limit=settings.rate_limit_generation_per_hour,
            window_seconds=3600,
        ),
        _RateLimitRule(
            key_prefix="general",
            limit=settings.rate_limit_general_per_minute,
            window_seconds=60,
        ),
    ]


def _match_rule(path: str, method: str) -> tuple[_RateLimitRule, str] | None:
    """根据请求路径和 method 匹配限流规则，返回 (rule, key_prefix)。"""
    rules = _build_rules()

    # 登录端点：POST /api/v1/auth/login
    if path == "/api/v1/auth/login" and method == "POST":
        return rules[0], "login"

    # AI 生成端点：*/generate/stream
    if "/generate/stream" in path:
        return rules[1], "generation"

    # 通用 API（排除 health check）
    if path.startswith("/api/"):
        return rules[2], "general"

    return None


# ---------------------------------------------------------------------------
# 中间件
# ---------------------------------------------------------------------------


class RateLimitMiddleware(BaseHTTPMiddleware):
    """限流中间件：按 IP 或 user_id 计数。"""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        settings = get_settings()
        if not settings.rate_limit_enabled:
            return await call_next(request)

        # 仅对有 body 的写操作 + SSE 流做限流
        matched = _match_rule(request.url.path, request.method)
        if matched is None:
            return await call_next(request)

        rule, key_prefix = matched

        # 限流 key：优先用 user_id（从 header 中提取），否则用 IP
        client_key = request.client.host if request.client else "unknown"
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            # 不解析 JWT，直接用 token hash 做 key（避免限流层依赖 JWT 解析）
            client_key = f"user:{hash(auth_header)}"

        bucket_key = f"{key_prefix}:{client_key}"
        bucket = _get_or_create_bucket(bucket_key, rule.limit, rule.window_seconds)

        if not bucket.is_allowed():
            return JSONResponse(
                status_code=429,
                content={"detail": "请求过于频繁，请稍后再试。"},
                headers={"Retry-After": str(rule.window_seconds)},
            )

        return await call_next(request)
