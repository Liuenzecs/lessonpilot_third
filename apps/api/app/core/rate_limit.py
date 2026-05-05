"""限流中间件 — 支持内存和 Redis 两种后端。

默认使用内存级 sliding window，适合单实例部署。
设置 RATE_LIMIT_BACKEND=redis 并提供 REDIS_URL 即可切换为 Redis 后端。
"""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Protocol

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.core.config import get_settings


# ---------------------------------------------------------------------------
# Sliding Window 接口
# ---------------------------------------------------------------------------


class RateLimitBackend(Protocol):
    def is_allowed(self, key: str, limit: int, window_seconds: int) -> bool: ...


# ---------------------------------------------------------------------------
# 内存后端
# ---------------------------------------------------------------------------


@dataclass
class _SlidingWindow:
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


class MemoryRateLimitBackend:
    """内存级限流后端（单实例，重启丢失）。"""

    def __init__(self) -> None:
        self._buckets: dict[str, _SlidingWindow] = defaultdict(lambda: _SlidingWindow(0, 0))
        self._last_cleanup = time.monotonic()

    def is_allowed(self, key: str, limit: int, window_seconds: int) -> bool:
        self._maybe_cleanup()
        bucket = self._buckets.get(key)
        if bucket is None or bucket.limit != limit or bucket.window_seconds != window_seconds:
            bucket = _SlidingWindow(limit=limit, window_seconds=window_seconds)
            self._buckets[key] = bucket
        return bucket.is_allowed()

    def _maybe_cleanup(self) -> None:
        now = time.monotonic()
        if now - self._last_cleanup < 300:
            return
        self._last_cleanup = now
        stale = [k for k, v in self._buckets.items() if not v.timestamps]
        for k in stale:
            del self._buckets[k]

    def reset(self) -> None:
        self._buckets.clear()


# ---------------------------------------------------------------------------
# Redis 后端
# ---------------------------------------------------------------------------


class RedisRateLimitBackend:
    """Redis 限流后端（多实例共享）。"""

    def __init__(self, redis_url: str) -> None:
        self._redis_url = redis_url
        self._client: object | None = None

    def _get_client(self):
        if self._client is not None:
            return self._client
        try:
            import redis
        except ImportError:
            raise ImportError("redis-py is required for Redis rate limit backend. Install with: pip install redis[hiredis]")
        self._client = redis.from_url(self._redis_url, decode_responses=True)
        return self._client

    def is_allowed(self, key: str, limit: int, window_seconds: int) -> bool:
        client = self._get_client()
        now = time.monotonic()
        member = f"{now}:{now}"
        pipe = client.pipeline()
        pipe.zremrangebyscore(key, 0, now - window_seconds)
        pipe.zcard(key)
        pipe.zadd(key, {member: now})
        pipe.expire(key, window_seconds * 2)
        _, count, _, _ = pipe.execute()
        return int(count) < limit


# ---------------------------------------------------------------------------
# 后端工厂
# ---------------------------------------------------------------------------

_backend: RateLimitBackend | None = None


def _get_backend() -> RateLimitBackend:
    global _backend
    if _backend is not None:
        return _backend
    settings = get_settings()
    backend_mode = getattr(settings, "rate_limit_backend", "memory")
    if backend_mode == "redis":
        redis_url = getattr(settings, "redis_url", "redis://localhost:6379/0")
        _backend = RedisRateLimitBackend(redis_url)
    else:
        _backend = MemoryRateLimitBackend()
    return _backend


def reset_buckets() -> None:
    """清空所有限流计数器（测试用）。"""
    global _backend
    backend = _get_backend()
    if isinstance(backend, MemoryRateLimitBackend):
        backend.reset()
    _backend = None


# ---------------------------------------------------------------------------
# 路由 → 限流规则映射
# ---------------------------------------------------------------------------


@dataclass
class _RateLimitRule:
    key_prefix: str
    limit: int
    window_seconds: int


def _build_rules() -> list[_RateLimitRule]:
    settings = get_settings()
    return [
        _RateLimitRule(key_prefix="login", limit=settings.rate_limit_login_per_minute, window_seconds=60),
        _RateLimitRule(key_prefix="generation", limit=settings.rate_limit_generation_per_hour, window_seconds=3600),
        _RateLimitRule(key_prefix="general", limit=settings.rate_limit_general_per_minute, window_seconds=60),
    ]


def _match_rule(path: str, method: str) -> tuple[_RateLimitRule, str] | None:
    rules = _build_rules()
    if path == "/api/v1/auth/login" and method == "POST":
        return rules[0], "login"
    if "/generate/stream" in path:
        return rules[1], "generation"
    if path.startswith("/api/"):
        return rules[2], "general"
    return None


# ---------------------------------------------------------------------------
# 中间件
# ---------------------------------------------------------------------------


class RateLimitMiddleware(BaseHTTPMiddleware):
    """限流中间件：按 IP 或 user_id 计数，支持内存/Redis 双后端。"""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        settings = get_settings()
        if not settings.rate_limit_enabled:
            return await call_next(request)

        matched = _match_rule(request.url.path, request.method)
        if matched is None:
            return await call_next(request)

        rule, key_prefix = matched

        client_key = request.client.host if request.client else "unknown"
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            client_key = f"user:{hash(auth_header)}"

        bucket_key = f"lp:rl:{key_prefix}:{client_key}"
        backend = _get_backend()

        if not backend.is_allowed(bucket_key, rule.limit, rule.window_seconds):
            return JSONResponse(
                status_code=429,
                content={"detail": "请求过于频繁，请稍后再试。"},
                headers={"Retry-After": str(rule.window_seconds)},
            )

        return await call_next(request)
