from __future__ import annotations

import json
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.core.security import hash_password, verify_password
from app.models import (
    AuthToken,
    BillingOrder,
    BillingWebhookEvent,
    Document,
    DocumentSnapshot,
    Feedback,
    InvoiceRequest,
    Task,
    User,
    UserSubscription,
)
from app.schemas.account import (
    AccountChangePasswordPayload,
    AccountDeletePayload,
    AccountRead,
    AccountUpdatePayload,
    FeedbackCreatePayload,
    FeedbackRead,
)
from app.services.auth_service import issue_verification_token, validate_password_strength
from app.services.billing_service import get_subscription_summary


def serialize_account(user: User) -> AccountRead:
    return AccountRead(
        id=user.id,
        email=user.email,
        name=user.name,
        email_verified=user.email_verified,
        email_verified_at=user.email_verified_at,
        created_at=user.created_at,
    )


def update_account_profile(session: Session, user: User, payload: AccountUpdatePayload) -> tuple[User, str | None]:
    next_name = payload.name.strip() if payload.name is not None else user.name
    next_email = payload.email.strip().lower() if payload.email is not None else user.email
    email_changed = next_email != user.email

    if email_changed:
        existing_user = session.exec(select(User).where(User.email == next_email, User.id != user.id)).first()
        if existing_user is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user.name = next_name
    user.email = next_email
    if email_changed:
        user.email_verified = False
        user.email_verified_at = None

    session.add(user)
    session.commit()
    session.refresh(user)

    verification_token = issue_verification_token(session, user) if email_changed else None
    return user, verification_token


def change_account_password(session: Session, user: User, payload: AccountChangePasswordPayload) -> None:
    if not verify_password(payload.current_password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Current password is incorrect")
    validate_password_strength(payload.new_password)
    if payload.current_password == payload.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from the current password",
        )

    user.password_hash = hash_password(payload.new_password)
    session.add(user)
    session.commit()


def create_feedback(session: Session, user: User, payload: FeedbackCreatePayload) -> Feedback:
    feedback = Feedback(
        user_id=user.id,
        mood=payload.mood,
        message=payload.message.strip(),
        page_path=payload.page_path.strip() if payload.page_path else None,
    )
    session.add(feedback)
    session.commit()
    session.refresh(feedback)
    return feedback


def serialize_feedback(feedback: Feedback) -> FeedbackRead:
    return FeedbackRead(
        id=feedback.id,
        user_id=feedback.user_id,
        mood=feedback.mood,
        message=feedback.message,
        page_path=feedback.page_path,
        created_at=feedback.created_at,
    )


def export_account_data(session: Session, user: User) -> bytes:
    tasks = session.exec(select(Task).where(Task.user_id == user.id).order_by(Task.updated_at.desc())).all()
    documents = session.exec(
        select(Document).where(Document.user_id == user.id).order_by(Document.updated_at.desc())
    ).all()
    document_ids = [document.id for document in documents]
    if document_ids:
        snapshots = session.exec(
            select(DocumentSnapshot)
            .where(DocumentSnapshot.document_id.in_(document_ids))
            .order_by(DocumentSnapshot.created_at.desc())
        ).all()
    else:
        snapshots = []
    feedback_entries = session.exec(
        select(Feedback).where(Feedback.user_id == user.id).order_by(Feedback.created_at.desc())
    ).all()
    subscriptions = session.exec(
        select(UserSubscription).where(UserSubscription.user_id == user.id).order_by(UserSubscription.created_at.desc())
    ).all()
    billing_orders = session.exec(
        select(BillingOrder).where(BillingOrder.user_id == user.id).order_by(BillingOrder.created_at.desc())
    ).all()
    invoice_requests = session.exec(
        select(InvoiceRequest).where(InvoiceRequest.user_id == user.id).order_by(InvoiceRequest.created_at.desc())
    ).all()
    order_ids = {order.id for order in billing_orders}
    webhook_events = session.exec(select(BillingWebhookEvent).order_by(BillingWebhookEvent.created_at.desc())).all()

    payload = {
        "exported_at": datetime.now(UTC).isoformat(),
        "user": serialize_account(user).model_dump(mode="json"),
        "subscription": get_subscription_summary(session, user).model_dump(mode="json"),
        "tasks": [
            {
                "id": task.id,
                "title": task.title,
                "subject": task.subject,
                "grade": task.grade,
                "topic": task.topic,
                "requirements": task.requirements,
                "status": task.status,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
            }
            for task in tasks
        ],
        "documents": [
            {
                "id": document.id,
                "task_id": document.task_id,
                "title": document.title,
                "doc_type": document.doc_type,
                "version": document.version,
                "content": document.content,
                "created_at": document.created_at.isoformat(),
                "updated_at": document.updated_at.isoformat(),
            }
            for document in documents
        ],
        "snapshots": [
            {
                "id": snapshot.id,
                "document_id": snapshot.document_id,
                "version": snapshot.version,
                "source": snapshot.source,
                "content": snapshot.content,
                "created_at": snapshot.created_at.isoformat(),
            }
            for snapshot in snapshots
        ],
        "feedback": [serialize_feedback(entry).model_dump(mode="json") for entry in feedback_entries],
        "subscriptions": [
            {
                "id": subscription.id,
                "plan": subscription.plan,
                "status": subscription.status,
                "billing_cycle": subscription.billing_cycle,
                "trial_started_at": (
                    subscription.trial_started_at.isoformat() if subscription.trial_started_at else None
                ),
                "trial_ends_at": subscription.trial_ends_at.isoformat() if subscription.trial_ends_at else None,
                "current_period_start": subscription.current_period_start.isoformat()
                if subscription.current_period_start
                else None,
                "current_period_end": (
                    subscription.current_period_end.isoformat() if subscription.current_period_end else None
                ),
                "trial_used_at": subscription.trial_used_at.isoformat() if subscription.trial_used_at else None,
                "created_at": subscription.created_at.isoformat(),
                "updated_at": subscription.updated_at.isoformat(),
            }
            for subscription in subscriptions
        ],
        "billing_orders": [
            {
                "id": order.id,
                "plan": order.plan,
                "billing_cycle": order.billing_cycle,
                "channel": order.channel,
                "amount_cents": order.amount_cents,
                "status": order.status,
                "checkout_url": order.checkout_url,
                "external_order_id": order.external_order_id,
                "paid_at": order.paid_at.isoformat() if order.paid_at else None,
                "effective_at": order.effective_at.isoformat() if order.effective_at else None,
                "created_at": order.created_at.isoformat(),
                "updated_at": order.updated_at.isoformat(),
            }
            for order in billing_orders
        ],
        "invoice_requests": [
            {
                "id": entry.id,
                "order_id": entry.order_id,
                "title": entry.title,
                "tax_number": entry.tax_number,
                "email": entry.email,
                "remark": entry.remark,
                "status": entry.status,
                "created_at": entry.created_at.isoformat(),
            }
            for entry in invoice_requests
        ],
        "billing_webhook_events": [
            {
                "id": event.id,
                "event_id": event.event_id,
                "event_type": event.event_type,
                "channel": event.channel,
                "signature_valid": event.signature_valid,
                "payload": event.payload,
                "processed_at": event.processed_at.isoformat() if event.processed_at else None,
                "created_at": event.created_at.isoformat(),
            }
            for event in webhook_events
            if isinstance(event.payload, dict) and event.payload.get("order_id") in order_ids
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")


def delete_account(session: Session, user: User, payload: AccountDeletePayload) -> None:
    if payload.confirm_text.strip().upper() != "DELETE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Please confirm with "DELETE"',
        )

    feedback_entries = session.exec(select(Feedback).where(Feedback.user_id == user.id)).all()
    for entry in feedback_entries:
        session.delete(entry)

    auth_tokens = session.exec(select(AuthToken).where(AuthToken.user_id == user.id)).all()
    for token in auth_tokens:
        session.delete(token)

    subscriptions = session.exec(select(UserSubscription).where(UserSubscription.user_id == user.id)).all()
    for subscription in subscriptions:
        session.delete(subscription)

    orders = session.exec(select(BillingOrder).where(BillingOrder.user_id == user.id)).all()
    order_ids = {order.id for order in orders}
    for order in orders:
        session.delete(order)

    invoices = session.exec(select(InvoiceRequest).where(InvoiceRequest.user_id == user.id)).all()
    for invoice in invoices:
        session.delete(invoice)

    webhook_events = session.exec(select(BillingWebhookEvent)).all()
    for event in webhook_events:
        if isinstance(event.payload, dict) and event.payload.get("order_id") in order_ids:
            session.delete(event)

    tasks = session.exec(select(Task).where(Task.user_id == user.id)).all()
    for task in tasks:
        document = session.exec(select(Document).where(Document.task_id == task.id)).first()
        if document is not None:
            snapshots = session.exec(
                select(DocumentSnapshot).where(DocumentSnapshot.document_id == document.id)
            ).all()
            for snapshot in snapshots:
                session.delete(snapshot)
            session.delete(document)
        session.delete(task)

    session.delete(user)
    session.commit()
