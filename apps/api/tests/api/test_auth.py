from __future__ import annotations


def test_register_login_me_and_logout(client):
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "teacher@example.com",
            "name": "Teacher",
            "password": "Password123",
        },
    )
    assert register_response.status_code == 201
    register_body = register_response.json()
    assert register_body["user"]["email"] == "teacher@example.com"
    token = register_body["access_token"]

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "teacher@example.com", "password": "Password123"},
    )
    assert login_response.status_code == 200

    headers = {"Authorization": f"Bearer {token}"}
    me_response = client.get("/api/v1/auth/me", headers=headers)
    assert me_response.status_code == 200
    assert me_response.json()["name"] == "Teacher"

    logout_response = client.post("/api/v1/auth/logout", headers=headers)
    assert logout_response.status_code == 204


def test_duplicate_register_rejected(client):
    payload = {
        "email": "teacher@example.com",
        "name": "Teacher",
        "password": "Password123",
    }
    assert client.post("/api/v1/auth/register", json=payload).status_code == 201
    duplicate_response = client.post("/api/v1/auth/register", json=payload)
    assert duplicate_response.status_code == 409

