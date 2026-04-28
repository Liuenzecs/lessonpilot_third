from __future__ import annotations

from fastapi.testclient import TestClient

from app.models import TeacherStyleProfile
from app.services.style_profile_service import format_teacher_style_context


def test_get_style_profile_returns_default(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.get("/api/v1/style-profile", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] is None
    assert data["enabled"] is True
    assert data["objective_style"] == ""
    assert data["sample_count"] == 0


def test_put_style_profile_persists_private_style(client: TestClient, auth_headers: dict[str, str]) -> None:
    payload = {
        "enabled": True,
        "objective_style": "目标使用“通过……学生能够……”句式。",
        "process_style": "教学过程要写清教师追问和学生批注。",
        "school_wording": "使用核心素养、学习任务群等学校常用措辞。",
        "activity_preferences": "圈点批注、同桌互说、板书归纳。",
        "avoid_phrases": "避免提高综合素质等空泛表达。",
    }

    response = client.put("/api/v1/style-profile", headers=auth_headers, json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["id"]
    assert data["objective_style"] == payload["objective_style"]

    get_response = client.get("/api/v1/style-profile", headers=auth_headers)
    assert get_response.json()["process_style"] == payload["process_style"]


def test_style_profile_is_user_isolated(client: TestClient, auth_headers: dict[str, str]) -> None:
    client.put(
        "/api/v1/style-profile",
        headers=auth_headers,
        json={
            "enabled": True,
            "objective_style": "我的目标写法",
            "process_style": "",
            "school_wording": "",
            "activity_preferences": "",
            "avoid_phrases": "",
        },
    )
    register_response = client.post(
        "/api/v1/auth/register",
        json={"email": "other@example.com", "name": "Other", "password": "Password123"},
    )
    other_headers = {"Authorization": f"Bearer {register_response.json()['access_token']}"}

    other_response = client.get("/api/v1/style-profile", headers=other_headers)

    assert other_response.status_code == 200
    assert other_response.json()["id"] is None
    assert other_response.json()["objective_style"] == ""


def test_format_teacher_style_context_respects_enabled() -> None:
    profile = TeacherStyleProfile(
        user_id="u1",
        enabled=True,
        objective_style="目标要具体可评价。",
        process_style="过程要写出追问。",
    )

    context = format_teacher_style_context(profile)

    assert "老师个人风格记忆" in context
    assert "目标要具体可评价" in context
    assert "不得覆盖结构化 JSON" in context

    profile.enabled = False
    assert format_teacher_style_context(profile) == ""
