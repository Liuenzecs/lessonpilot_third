from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.db import get_session
from app.schemas.billing import BillingWebhookPayload, BillingWebhookResponse
from app.services.billing_service import process_billing_webhook

router = APIRouter(prefix="/billing", tags=["billing"])


@router.post("/webhooks/gateway", response_model=BillingWebhookResponse)
def gateway_webhook(
    payload: BillingWebhookPayload,
    session: Session = Depends(get_session),
) -> BillingWebhookResponse:
    processed = process_billing_webhook(session, payload)
    return BillingWebhookResponse(
        processed=processed,
        message="Webhook processed" if processed else "Webhook already processed",
    )
