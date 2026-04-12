from __future__ import annotations

from collections.abc import Iterable
from datetime import UTC, datetime
from typing import Any

from sqlmodel import Session, select

from app.models import AnalyticsEvent, User
from app.schemas.analytics import AnalyticsBatchPayload, AnalyticsBatchResponse

SENSITIVE_PROPERTY_TOKENS = {
    "password",
    "token",
    "authorization",
    "content",
    "prompt",
    "selection_text",
    "document",
    "email",
    "jwt",
    "secret",
}


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _is_sensitive_key(key: str) -> bool:
    normalized = key.strip().lower()
    return any(token in normalized for token in SENSITIVE_PROPERTY_TOKENS)


def _sanitize_value(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        if isinstance(value, str):
            return value[:500]
        return value
    if isinstance(value, dict):
        sanitized: dict[str, Any] = {}
        for key, nested in value.items():
            if _is_sensitive_key(str(key)):
                continue
            sanitized[str(key)[:80]] = _sanitize_value(nested)
        return sanitized
    if isinstance(value, Iterable) and not isinstance(value, (bytes, bytearray)):
        return [_sanitize_value(item) for item in list(value)[:20]]
    return str(value)[:500]


def sanitize_properties(properties: dict[str, Any] | None) -> dict[str, Any]:
    return _sanitize_value(properties or {})


def ingest_client_events(
    session: Session,
    *,
    current_user: User | None,
    payload: AnalyticsBatchPayload,
) -> AnalyticsBatchResponse:
    accepted = 0
    deduplicated = 0

    for item in payload.events:
        existing = session.exec(
            select(AnalyticsEvent).where(AnalyticsEvent.client_event_id == item.client_event_id)
        ).first()
        if existing is not None:
            deduplicated += 1
            continue

        event = AnalyticsEvent(
            event_name=item.event_name,
            occurred_at=_ensure_utc(item.occurred_at),
            source="client",
            user_id=current_user.id if current_user else None,
            anonymous_id=item.anonymous_id,
            session_id=item.session_id,
            page_path=item.page_path,
            referrer=item.referrer,
            properties=sanitize_properties(item.properties),
            client_event_id=item.client_event_id,
        )
        session.add(event)
        accepted += 1

    session.commit()
    return AnalyticsBatchResponse(accepted=accepted, deduplicated=deduplicated)


def record_server_event(
    session: Session,
    *,
    event_name: str,
    user: User | None,
    page_path: str,
    session_id: str | None = None,
    anonymous_id: str | None = None,
    referrer: str | None = None,
    properties: dict[str, Any] | None = None,
    occurred_at: datetime | None = None,
) -> AnalyticsEvent:
    event = AnalyticsEvent(
        event_name=event_name,
        occurred_at=_ensure_utc(occurred_at or datetime.now(UTC)),
        source="server",
        user_id=user.id if user else None,
        anonymous_id=anonymous_id,
        session_id=session_id or (user.id if user else "server"),
        page_path=page_path,
        referrer=referrer,
        properties=sanitize_properties(properties),
    )
    session.add(event)
    session.commit()
    session.refresh(event)
    return event
