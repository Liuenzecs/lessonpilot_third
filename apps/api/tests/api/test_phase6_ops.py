from __future__ import annotations

from sqlmodel import Session, select

from app.core.config import get_settings
from app.core.db import get_engine
from app.core.sentry import sentry_before_send
from app.models import AnalyticsEvent, EmailDeliveryLog, User
from app.services.billing_service import month_key
from app.services.mail_service import send_quota_warning_email


def _create_task(client, auth_headers, topic: str):
    return client.post(
        "/api/v1/tasks/",
        headers=auth_headers,
        json={
            "subject": "语文",
            "grade": "七年级",
            "topic": topic,
        },
    )


def test_register_and_forgot_password_create_email_delivery_logs(client):
    register_response = client.post(
        "/api/v1/auth/register",
        json={"email": "teacher@example.com", "name": "Teacher", "password": "Password123"},
    )
    assert register_response.status_code == 201

    forgot_response = client.post("/api/v1/auth/forgot-password", json={"email": "teacher@example.com"})
    assert forgot_response.status_code == 202

    with Session(get_engine()) as session:
        logs = session.exec(select(EmailDeliveryLog).order_by(EmailDeliveryLog.created_at.asc())).all()
        template_keys = [entry.template_key for entry in logs]
        assert "welcome_verify_email" in template_keys
        assert "password_reset" in template_keys
        assert all(entry.status == "sent" for entry in logs)


def test_quota_warning_email_uses_dedupe_log(auth_headers):
    with Session(get_engine()) as session:
        user = session.exec(select(User).where(User.email == "teacher@example.com")).one()

    assert send_quota_warning_email(user_id=user.id, remaining=1, month_key=month_key()) is True
    assert send_quota_warning_email(user_id=user.id, remaining=1, month_key=month_key()) is False

    with Session(get_engine()) as session:
        logs = session.exec(
            select(EmailDeliveryLog).where(EmailDeliveryLog.template_key == "quota_warning_almost_reached")
        ).all()
        assert len(logs) == 1


def test_analytics_batch_deduplicates_by_client_event_id(client):
    payload = {
        "events": [
            {
                "event_name": "page_view",
                "occurred_at": "2026-04-12T10:00:00Z",
                "source": "client",
                "anonymous_id": "anon-1",
                "session_id": "session-1",
                "page_path": "/pricing",
                "properties": {"section": "hero"},
                "client_event_id": "evt-1",
            }
        ]
    }
    first_response = client.post("/api/v1/analytics/events/batch", json=payload)
    assert first_response.status_code == 202
    assert first_response.json() == {"accepted": 1, "deduplicated": 0}

    second_response = client.post("/api/v1/analytics/events/batch", json=payload)
    assert second_response.status_code == 202
    assert second_response.json() == {"accepted": 0, "deduplicated": 1}


def test_admin_whitelist_and_quota_adjustment_affect_remaining_quota(client, auth_headers, monkeypatch):
    monkeypatch.setenv("ADMIN_ALLOWLIST_EMAILS", "teacher@example.com")
    get_settings.cache_clear()

    denied_response = client.get("/api/v1/admin/overview")
    assert denied_response.status_code == 401

    for index in range(5):
        assert _create_task(client, auth_headers, f"管理后台测试 {index}").status_code == 201

    sixth_before_adjustment = _create_task(client, auth_headers, "管理后台测试 5")
    assert sixth_before_adjustment.status_code == 402

    adjustment_response = client.post(
        "/api/v1/admin/users/teacher@example.com/quota-adjustments",
        headers=auth_headers,
        json={"delta": 2, "reason": "客服补偿"},
    )
    assert adjustment_response.status_code == 404

    with Session(get_engine()) as session:
        user = session.exec(select(User).where(User.email == "teacher@example.com")).one()

    adjustment_response = client.post(
        f"/api/v1/admin/users/{user.id}/quota-adjustments",
        headers=auth_headers,
        json={"delta": 2, "reason": "客服补偿"},
    )
    assert adjustment_response.status_code == 201

    subscription_response = client.get("/api/v1/account/subscription", headers=auth_headers)
    assert subscription_response.status_code == 200
    assert subscription_response.json()["monthly_task_limit"] == 7
    assert subscription_response.json()["quota_remaining"] == 2

    sixth_after_adjustment = _create_task(client, auth_headers, "管理后台测试 6")
    assert sixth_after_adjustment.status_code == 201

    admin_detail = client.get(f"/api/v1/admin/users/{user.id}", headers=auth_headers)
    assert admin_detail.status_code == 200
    assert admin_detail.json()["quota_adjustments"][0]["delta"] == 2


def test_server_events_are_recorded_for_task_creation_and_exports(client, auth_headers):
    create_response = _create_task(client, auth_headers, "运营埋点测试")
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    document = client.get(f"/api/v1/documents/?task_id={task_id}", headers=auth_headers).json()["items"][0]
    export_response = client.get(f"/api/v1/documents/{document['id']}/export?format=docx", headers=auth_headers)
    assert export_response.status_code == 200

    with Session(get_engine()) as session:
        event_names = {
            row.event_name
            for row in session.exec(select(AnalyticsEvent).where(AnalyticsEvent.source == "server")).all()
        }
        assert "task_created" in event_names
        assert "docx_export_succeeded" in event_names


def test_sentry_scrubber_filters_sensitive_fields():
    event = {
        "request": {
            "headers": {"Authorization": "Bearer secret-token"},
            "data": {"password": "Password123", "content": {"blocks": []}},
        },
        "extra": {"prompt": "secret prompt", "safe": "ok"},
    }
    cleaned = sentry_before_send(event, {})
    assert cleaned["request"]["headers"]["Authorization"] == "[Filtered]"
    assert cleaned["request"]["data"]["password"] == "[Filtered]"
    assert cleaned["request"]["data"]["content"] == "[Filtered]"
    assert cleaned["extra"]["prompt"] == "[Filtered]"
    assert cleaned["extra"]["safe"] == "ok"
