"""Analytics events ingestion endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from fastapi.responses import Response
from sqlmodel import Session

from app.core.db import get_session
from app.models import AnalyticsEvent
from app.schemas.analytics import AnalyticsEventPayload

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.post("/events", status_code=status.HTTP_204_NO_CONTENT)
def ingest_events(
    payload: list[AnalyticsEventPayload],
    session: Session = Depends(get_session),
) -> Response:
    """接收前端批量埋点事件。"""
    for item in payload:
        event = AnalyticsEvent(
            event_name=item.event_name,
            source=item.source,
            user_id=item.user_id,
            anonymous_id=item.anonymous_id,
            session_id=item.session_id,
            page_path=item.page_path,
            referrer=item.referrer,
            properties=item.properties,
            client_event_id=item.client_event_id,
        )
        session.add(event)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
