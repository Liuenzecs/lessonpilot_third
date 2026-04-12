from __future__ import annotations

from urllib.parse import quote

from fastapi import APIRouter, BackgroundTasks, Body, Depends, Response, status
from fastapi.responses import Response as FastAPIResponse
from sqlmodel import Session

from app.core.db import get_session
from app.core.security import get_current_user
from app.models import User
from app.schemas.account import (
    AccountChangePasswordPayload,
    AccountDeletePayload,
    AccountRead,
    AccountUpdatePayload,
    FeedbackCreatePayload,
    FeedbackRead,
)
from app.schemas.auth import MessageResponse
from app.schemas.billing import (
    AccountSubscriptionRead,
    BillingOrderListResponse,
    InvoiceRequestCreatePayload,
    InvoiceRequestListResponse,
    InvoiceRequestRead,
    SubscriptionActionResponse,
    SubscriptionCheckoutPayload,
)
from app.services.account_service import (
    change_account_password,
    create_feedback,
    delete_account,
    export_account_data,
    serialize_account,
    serialize_feedback,
    update_account_profile,
)
from app.services.analytics_service import record_server_event
from app.services.billing_service import (
    create_checkout,
    create_invoice_request,
    get_subscription_summary,
    list_invoice_requests,
    list_subscription_orders,
    renew_subscription,
    start_trial,
)
from app.services.mail_service import (
    send_feedback_notification,
    send_invoice_request_notification,
    send_verification_email,
)

router = APIRouter(prefix="/account", tags=["account"])


@router.get("", response_model=AccountRead)
def get_account(current_user: User = Depends(get_current_user)) -> AccountRead:
    return serialize_account(current_user)


@router.patch("", response_model=AccountRead)
def patch_account(
    payload: AccountUpdatePayload,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> AccountRead:
    user, verification_token = update_account_profile(session, current_user, payload)
    if verification_token:
        background_tasks.add_task(send_verification_email, user.email, user.name, verification_token, user_id=user.id)
    return serialize_account(user)


@router.post("/change-password", response_model=MessageResponse)
def change_password(
    payload: AccountChangePasswordPayload,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    change_account_password(session, current_user, payload)
    return MessageResponse(message="密码修改成功。")


@router.get("/subscription", response_model=AccountSubscriptionRead)
def get_subscription(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> AccountSubscriptionRead:
    return get_subscription_summary(session, current_user)


@router.post("/subscription/trial", response_model=SubscriptionActionResponse)
def start_subscription_trial(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> SubscriptionActionResponse:
    response = start_trial(session, current_user)
    record_server_event(
        session,
        event_name="trial_started",
        user=current_user,
        page_path="/settings",
        properties={"billing_cycle": response.subscription.billing_cycle},
    )
    return response


@router.post("/subscription/checkout", response_model=SubscriptionActionResponse)
def create_subscription_checkout(
    payload: SubscriptionCheckoutPayload,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> SubscriptionActionResponse:
    response = create_checkout(session, current_user, payload)
    record_server_event(
        session,
        event_name="checkout_started",
        user=current_user,
        page_path="/settings",
        properties={"billing_cycle": payload.billing_cycle, "channel": payload.channel},
    )
    return response


@router.post("/subscription/renew", response_model=SubscriptionActionResponse)
def renew_professional_subscription(
    payload: SubscriptionCheckoutPayload,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> SubscriptionActionResponse:
    response = renew_subscription(session, current_user, payload)
    record_server_event(
        session,
        event_name="checkout_started",
        user=current_user,
        page_path="/settings",
        properties={"billing_cycle": payload.billing_cycle, "channel": payload.channel, "mode": "renew"},
    )
    return response


@router.get("/subscription/orders", response_model=BillingOrderListResponse)
def get_subscription_orders(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> BillingOrderListResponse:
    return list_subscription_orders(session, current_user)


@router.get("/invoice-requests", response_model=InvoiceRequestListResponse)
def get_account_invoice_requests(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> InvoiceRequestListResponse:
    return list_invoice_requests(session, current_user)


@router.post("/invoice-requests", response_model=InvoiceRequestRead, status_code=status.HTTP_201_CREATED)
def post_invoice_request(
    payload: InvoiceRequestCreatePayload,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> InvoiceRequestRead:
    invoice_request = create_invoice_request(session, current_user, payload)
    background_tasks.add_task(
        send_invoice_request_notification,
        user_id=current_user.id,
        user_name=current_user.name,
        user_email=current_user.email,
        order_id=payload.order_id,
        title=payload.title,
        tax_number=payload.tax_number,
        invoice_email=payload.email,
        remark=payload.remark,
    )
    return invoice_request


@router.post("/export")
def export_account(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> FastAPIResponse:
    payload = export_account_data(session, current_user)
    filename = quote(f"lessonpilot-account-{current_user.id}.json")
    return FastAPIResponse(
        content=payload,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"},
    )


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def remove_account(
    payload: AccountDeletePayload = Body(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Response:
    delete_account(session, current_user, payload)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/feedback", response_model=FeedbackRead, status_code=status.HTTP_201_CREATED)
def post_feedback(
    payload: FeedbackCreatePayload,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> FeedbackRead:
    feedback = create_feedback(session, current_user, payload)
    record_server_event(
        session,
        event_name="feedback_submitted",
        user=current_user,
        page_path=payload.page_path or "/feedback",
        properties={"mood": payload.mood},
    )
    background_tasks.add_task(
        send_feedback_notification,
        user_id=current_user.id,
        user_name=current_user.name,
        user_email=current_user.email,
        mood=payload.mood,
        message=payload.message,
        page_path=payload.page_path,
    )
    return serialize_feedback(feedback)
