from __future__ import annotations

import hashlib
from datetime import UTC, datetime, timedelta

from sqlmodel import Session, select

from app.core.config import get_settings
from app.core.db import get_engine
from app.models import BillingOrder, User, UserSubscription


def _create_task(client, auth_headers, topic: str):
    response = client.post(
        "/api/v1/tasks/",
        headers=auth_headers,
        json={
            "subject": "数学",
            "grade": "八年级",
            "topic": topic,
            "requirements": "Phase 4 测试",
        },
    )
    return response


def _create_task_and_document(client, auth_headers, topic: str = "一元二次方程"):
    create_response = _create_task(client, auth_headers, topic)
    assert create_response.status_code == 201
    task = create_response.json()
    document = client.get(f"/api/v1/documents/?task_id={task['id']}", headers=auth_headers).json()["items"][0]
    return task, document


def _current_user_id() -> str:
    with Session(get_engine()) as session:
        user = session.exec(select(User).where(User.email == "teacher@example.com")).one()
        return user.id


def test_subscription_trial_checkout_and_expire_flow(client, auth_headers):
    free_subscription = client.get("/api/v1/account/subscription", headers=auth_headers)
    assert free_subscription.status_code == 200
    assert free_subscription.json()["status"] == "free"
    assert free_subscription.json()["quota_remaining"] == 5

    trial_response = client.post("/api/v1/account/subscription/trial", headers=auth_headers)
    assert trial_response.status_code == 200
    trial_payload = trial_response.json()
    assert trial_payload["subscription"]["status"] == "trialing"
    assert trial_payload["subscription"]["trial_used"] is True

    second_trial = client.post("/api/v1/account/subscription/trial", headers=auth_headers)
    assert second_trial.status_code == 409

    checkout_response = client.post(
        "/api/v1/account/subscription/checkout",
        headers=auth_headers,
        json={"plan": "professional", "billing_cycle": "monthly", "channel": "wechat"},
    )
    assert checkout_response.status_code == 200
    checkout_payload = checkout_response.json()
    assert checkout_payload["order"]["status"] == "paid"
    assert checkout_payload["subscription"]["status"] == "trialing"
    assert checkout_payload["order"]["effective_at"] == checkout_payload["subscription"]["trial_ends_at"]
    assert checkout_payload["subscription"]["current_period_start"] == checkout_payload["subscription"]["trial_ends_at"]

    with Session(get_engine()) as session:
        subscription = session.exec(
            select(UserSubscription).where(UserSubscription.user_id == _current_user_id())
        ).one()
        subscription.trial_started_at = datetime.now(UTC) - timedelta(days=8)
        subscription.trial_ends_at = datetime.now(UTC) - timedelta(days=1)
        subscription.updated_at = datetime.now(UTC)
        session.add(subscription)
        session.commit()

    expired_subscription = client.get("/api/v1/account/subscription", headers=auth_headers)
    assert expired_subscription.status_code == 200
    assert expired_subscription.json()["status"] == "expired"
    assert expired_subscription.json()["entitlements"]["ai_rewrite"] is False


def test_manual_renew_extends_active_period(client, auth_headers):
    checkout_response = client.post(
        "/api/v1/account/subscription/checkout",
        headers=auth_headers,
        json={"plan": "professional", "billing_cycle": "monthly", "channel": "alipay"},
    )
    assert checkout_response.status_code == 200
    first_payload = checkout_response.json()
    first_period_end = first_payload["subscription"]["current_period_end"]

    renew_response = client.post(
        "/api/v1/account/subscription/renew",
        headers=auth_headers,
        json={"plan": "professional", "billing_cycle": "monthly", "channel": "alipay"},
    )
    assert renew_response.status_code == 200
    renew_payload = renew_response.json()
    assert renew_payload["subscription"]["status"] == "active"
    assert renew_payload["order"]["status"] == "paid"
    assert renew_payload["order"]["effective_at"] == first_period_end
    assert renew_payload["subscription"]["current_period_end"] > first_period_end


def test_free_quota_limits_create_and_duplicate(client, auth_headers):
    created_task_ids: list[str] = []
    for index in range(5):
        response = _create_task(client, auth_headers, f"额度测试 {index}")
        assert response.status_code == 201
        created_task_ids.append(response.json()["id"])

    sixth_create = _create_task(client, auth_headers, "额度测试 5")
    assert sixth_create.status_code == 402
    assert sixth_create.json()["detail"]["code"] == "quota_exceeded"

    duplicate_response = client.post(
        f"/api/v1/tasks/{created_task_ids[0]}/duplicate",
        headers=auth_headers,
    )
    assert duplicate_response.status_code == 402
    assert duplicate_response.json()["detail"]["code"] == "quota_exceeded"


def test_professional_feature_gates_return_402(client, auth_headers):
    task, document = _create_task_and_document(client, auth_headers)
    section_id = document["content"]["blocks"][0]["id"]

    rewrite_response = client.post(
        f"/api/v1/documents/{document['id']}/rewrite",
        headers=auth_headers,
        json={
            "document_version": document["version"],
            "mode": "block",
            "target_block_id": section_id,
            "action": "rewrite",
        },
    )
    assert rewrite_response.status_code == 402
    assert rewrite_response.json()["detail"]["code"] == "plan_required"

    append_response = client.post(
        f"/api/v1/documents/{document['id']}/append",
        headers=auth_headers,
        json={
            "document_version": document["version"],
            "section_id": section_id,
            "instruction": "补充导入语",
        },
    )
    assert append_response.status_code == 402
    assert append_response.json()["detail"]["code"] == "plan_required"

    history_response = client.get(f"/api/v1/documents/{document['id']}/history?limit=10", headers=auth_headers)
    assert history_response.status_code == 402
    assert history_response.json()["detail"]["code"] == "plan_required"

    restore_response = client.post(
        f"/api/v1/documents/{document['id']}/history/snapshot-placeholder/restore",
        headers=auth_headers,
    )
    assert restore_response.status_code == 402
    assert restore_response.json()["detail"]["code"] == "plan_required"

    pdf_response = client.get(f"/api/v1/documents/{document['id']}/export?format=pdf", headers=auth_headers)
    assert pdf_response.status_code == 402
    assert pdf_response.json()["detail"]["code"] == "plan_required"

    section_regenerate_response = client.post(
        f"/api/v1/tasks/{task['id']}/generate",
        headers=auth_headers,
        json={"section_id": section_id},
    )
    assert section_regenerate_response.status_code == 402
    assert section_regenerate_response.json()["detail"]["code"] == "plan_required"


def test_invoice_request_persists_after_paid_order(client, auth_headers):
    checkout_response = client.post(
        "/api/v1/account/subscription/checkout",
        headers=auth_headers,
        json={"plan": "professional", "billing_cycle": "yearly", "channel": "wechat"},
    )
    assert checkout_response.status_code == 200
    order_id = checkout_response.json()["order"]["id"]

    invoice_response = client.post(
        "/api/v1/account/invoice-requests",
        headers=auth_headers,
        json={
            "order_id": order_id,
            "title": "杭州某学校",
            "tax_number": "91330100MA00000000",
            "email": "finance@example.com",
            "remark": "请开电子发票",
        },
    )
    assert invoice_response.status_code == 201
    assert invoice_response.json()["status"] == "submitted"

    list_response = client.get("/api/v1/account/invoice-requests", headers=auth_headers)
    assert list_response.status_code == 200
    assert len(list_response.json()["items"]) == 1
    assert list_response.json()["items"][0]["order_id"] == order_id


def test_gateway_webhook_signature_and_idempotency(client, auth_headers, monkeypatch):
    monkeypatch.setenv("BILLING_MODE", "gateway")
    monkeypatch.setenv("BILLING_WEBHOOK_SECRET", "phase4-test-secret")
    get_settings.cache_clear()

    checkout_response = client.post(
        "/api/v1/account/subscription/checkout",
        headers=auth_headers,
        json={"plan": "professional", "billing_cycle": "monthly", "channel": "wechat"},
    )
    assert checkout_response.status_code == 200
    order = checkout_response.json()["order"]
    assert order["status"] == "pending"

    event_id = "evt_phase4_success"
    event_type = "payment.succeeded"
    secret = get_settings().billing_webhook_secret
    signature = hashlib.sha256(f"{event_id}:{event_type}:{order['id']}:{secret}".encode("utf-8")).hexdigest()

    webhook_payload = {
        "event_id": event_id,
        "event_type": event_type,
        "order_id": order["id"],
        "channel": "wechat",
        "signature": signature,
        "payload": {"source": "pytest"},
    }

    first_webhook = client.post("/api/v1/billing/webhooks/gateway", json=webhook_payload)
    assert first_webhook.status_code == 200
    assert first_webhook.json()["processed"] is True

    second_webhook = client.post("/api/v1/billing/webhooks/gateway", json=webhook_payload)
    assert second_webhook.status_code == 200
    assert second_webhook.json()["processed"] is False

    with Session(get_engine()) as session:
        stored_order = session.get(BillingOrder, order["id"])
        assert stored_order is not None
        assert stored_order.status == "paid"
