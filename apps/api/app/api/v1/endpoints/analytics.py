from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.core.db import get_session
from app.core.security import get_optional_current_user
from app.models import User
from app.schemas.analytics import AnalyticsBatchPayload, AnalyticsBatchResponse
from app.services.analytics_service import ingest_client_events

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.post("/events/batch", response_model=AnalyticsBatchResponse, status_code=status.HTTP_202_ACCEPTED)
def post_analytics_events(
    payload: AnalyticsBatchPayload,
    session: Session = Depends(get_session),
    current_user: User | None = Depends(get_optional_current_user),
) -> AnalyticsBatchResponse:
    return ingest_client_events(session, current_user=current_user, payload=payload)
