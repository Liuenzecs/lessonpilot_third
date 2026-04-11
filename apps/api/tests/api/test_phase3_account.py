from __future__ import annotations

import json

from sqlmodel import Session, select

from app.core.db import get_engine
from app.models import AuthToken, Document, Feedback, Task, User


def _create_task(client, auth_headers, *, topic: str = "一元二次方程"):
    response = client.post(
        "/api/v1/tasks/",
        headers=auth_headers,
        json={
            "subject": "数学",
            "grade": "八年级",
            "topic": topic,
            "requirements": "突出重难点",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_account_profile_password_and_subscription(client, auth_headers):
    profile_response = client.get("/api/v1/account", headers=auth_headers)
    assert profile_response.status_code == 200
    assert profile_response.json()["email_verified"] is False

    update_response = client.patch(
        "/api/v1/account",
        headers=auth_headers,
        json={"name": "张老师", "email": "teacher+new@example.com"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "张老师"
    assert update_response.json()["email"] == "teacher+new@example.com"
    assert update_response.json()["email_verified"] is False

    _create_task(client, auth_headers)
    subscription_response = client.get("/api/v1/account/subscription", headers=auth_headers)
    assert subscription_response.status_code == 200
    assert subscription_response.json()["plan"] == "free"
    assert subscription_response.json()["tasks_used_this_month"] == 1

    change_password_response = client.post(
        "/api/v1/account/change-password",
        headers=auth_headers,
        json={
            "current_password": "Password123",
            "new_password": "ChangedPassword123",
            "confirm_password": "ChangedPassword123",
        },
    )
    assert change_password_response.status_code == 200

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "teacher+new@example.com", "password": "ChangedPassword123"},
    )
    assert login_response.status_code == 200


def test_task_duplicate_feedback_and_export(client, auth_headers):
    original_task = _create_task(client, auth_headers, topic="二次函数")

    duplicate_response = client.post(
        f"/api/v1/tasks/{original_task['id']}/duplicate",
        headers=auth_headers,
    )
    assert duplicate_response.status_code == 201
    duplicated_task = duplicate_response.json()
    assert duplicated_task["title"].endswith("（副本）")

    original_document = client.get(
        f"/api/v1/documents/?task_id={original_task['id']}",
        headers=auth_headers,
    ).json()["items"][0]
    duplicated_document = client.get(
        f"/api/v1/documents/?task_id={duplicated_task['id']}",
        headers=auth_headers,
    ).json()["items"][0]
    assert duplicated_document["version"] == 1
    assert duplicated_document["content"]["blocks"] == original_document["content"]["blocks"]

    feedback_response = client.post(
        "/api/v1/account/feedback",
        headers=auth_headers,
        json={
            "mood": "happy",
            "message": "备课台的卡片操作很顺手。",
            "page_path": "/tasks",
        },
    )
    assert feedback_response.status_code == 201
    assert feedback_response.json()["mood"] == "happy"

    export_response = client.post("/api/v1/account/export", headers=auth_headers)
    assert export_response.status_code == 200
    assert export_response.headers["content-type"].startswith("application/json")
    exported_payload = json.loads(export_response.content.decode("utf-8"))
    assert exported_payload["user"]["email"] == "teacher@example.com"
    assert len(exported_payload["tasks"]) == 2
    assert len(exported_payload["feedback"]) == 1


def test_delete_account_cascades_data(client, auth_headers):
    _create_task(client, auth_headers)
    client.post(
        "/api/v1/account/feedback",
        headers=auth_headers,
        json={"mood": "neutral", "message": "测试反馈", "page_path": "/settings"},
    )

    with Session(get_engine()) as session:
        user = session.exec(select(User).where(User.email == "teacher@example.com")).one()
        auth_token = AuthToken(
            user_id=user.id,
            token_hash="manual-token-hash",
            token_type="verify_email",
            expires_at=user.created_at,
        )
        session.add(auth_token)
        session.commit()

    delete_response = client.request(
        "DELETE",
        "/api/v1/account",
        headers=auth_headers,
        json={"confirm_text": "DELETE"},
    )
    assert delete_response.status_code == 204

    with Session(get_engine()) as session:
        assert session.exec(select(User)).all() == []
        assert session.exec(select(Task)).all() == []
        assert session.exec(select(Document)).all() == []
        assert session.exec(select(Feedback)).all() == []
        assert session.exec(select(AuthToken)).all() == []
