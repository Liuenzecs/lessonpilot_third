from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from app.core.config import get_settings

SENSITIVE_KEYS = {
    "authorization",
    "password",
    "token",
    "jwt",
    "secret",
    "content",
    "content_json",
    "prompt",
}


def _scrub(value: Any) -> Any:
    if isinstance(value, Mapping):
        cleaned: dict[str, Any] = {}
        for key, nested in value.items():
            lowered = str(key).lower()
            if any(token in lowered for token in SENSITIVE_KEYS):
                cleaned[str(key)] = "[Filtered]"
            else:
                cleaned[str(key)] = _scrub(nested)
        return cleaned
    if isinstance(value, list):
        return [_scrub(item) for item in value]
    if isinstance(value, str) and len(value) > 2000:
        return value[:2000]
    return value


def sentry_before_send(event: dict[str, Any], hint: dict[str, Any]) -> dict[str, Any]:
    _ = hint
    return _scrub(event)


def init_sentry_api() -> None:
    settings = get_settings()
    if not settings.sentry_dsn_api:
        return

    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
    except ImportError:
        return

    sentry_sdk.init(
        dsn=settings.sentry_dsn_api,
        environment=settings.sentry_environment,
        traces_sample_rate=settings.sentry_traces_sample_rate_api,
        before_send=sentry_before_send,
        integrations=[FastApiIntegration()],
        send_default_pii=False,
    )
