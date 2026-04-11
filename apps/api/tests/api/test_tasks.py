from __future__ import annotations

import json


def _parse_sse_events(raw_text: str) -> list[tuple[str, dict]]:
    events: list[tuple[str, dict]] = []
    for chunk in raw_text.strip().split("\n\n"):
        if not chunk.strip():
            continue
        event_name = ""
        data_payload = ""
        for line in chunk.splitlines():
            if line.startswith("event: "):
                event_name = line.removeprefix("event: ").strip()
            if line.startswith("data: "):
                data_payload = line.removeprefix("data: ").strip()
        if event_name and data_payload:
            events.append((event_name, json.loads(data_payload)))
    return events


def test_task_document_generation_and_export_flow(client, auth_headers):
    create_response = client.post(
        "/api/v1/tasks/",
        headers=auth_headers,
        json={
            "subject": "数学",
            "grade": "八年级",
            "topic": "一元二次方程",
            "requirements": "突出配方法",
        },
    )
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    tasks_response = client.get("/api/v1/tasks/?page=1&page_size=20", headers=auth_headers)
    assert tasks_response.status_code == 200
    assert tasks_response.json()["total"] == 1

    documents_response = client.get(f"/api/v1/documents/?task_id={task_id}", headers=auth_headers)
    assert documents_response.status_code == 200
    document = documents_response.json()["items"][0]
    document_id = document["id"]
    assert len(document["content"]["blocks"]) == 6

    start_response = client.post(
        f"/api/v1/tasks/{task_id}/generate",
        headers=auth_headers,
        json={},
    )
    assert start_response.status_code == 200
    stream_url = start_response.json()["stream_url"]

    with client.stream("GET", stream_url, headers=auth_headers) as stream_response:
        payload = "".join(stream_response.iter_text())
    events = _parse_sse_events(payload)
    event_names = [event_name for event_name, _ in events]
    assert event_names[0] == "status"
    assert "progress" in event_names
    assert event_names[-1] == "done"

    refreshed_document = client.get(f"/api/v1/documents/{document_id}", headers=auth_headers).json()
    assert refreshed_document["version"] > 1
    assert any(
        child["status"] == "pending"
        for block in refreshed_document["content"]["blocks"]
        for child in block.get("children", [])
    )

    accepted_content = refreshed_document["content"]
    for block in accepted_content["blocks"]:
        block["children"] = [
            {**child, "status": "confirmed"} for child in block.get("children", [])
        ]

    update_response = client.patch(
        f"/api/v1/documents/{document_id}",
        headers=auth_headers,
        json={
            "version": refreshed_document["version"],
            "content": accepted_content,
        },
    )
    assert update_response.status_code == 200

    conflict_response = client.patch(
        f"/api/v1/documents/{document_id}",
        headers=auth_headers,
        json={
            "version": refreshed_document["version"],
            "content": accepted_content,
        },
    )
    assert conflict_response.status_code == 409

    export_response = client.get(
        f"/api/v1/documents/{document_id}/export?format=docx",
        headers=auth_headers,
    )
    assert export_response.status_code == 200
    assert export_response.content[:2] == b"PK"

    delete_response = client.delete(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert delete_response.status_code == 204

    list_after_delete = client.get(f"/api/v1/documents/?task_id={task_id}", headers=auth_headers)
    assert list_after_delete.json()["items"] == []


def test_task_access_is_isolated(client):
    register_a = client.post(
        "/api/v1/auth/register",
        json={"email": "a@example.com", "name": "Alice", "password": "Password123"},
    )
    token_a = register_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    task_response = client.post(
        "/api/v1/tasks/",
        headers=headers_a,
        json={"subject": "语文", "grade": "七年级", "topic": "散步"},
    )
    task_id = task_response.json()["id"]

    register_b = client.post(
        "/api/v1/auth/register",
        json={"email": "b@example.com", "name": "Bob", "password": "Password123"},
    )
    token_b = register_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    other_user_response = client.get(f"/api/v1/tasks/{task_id}", headers=headers_b)
    assert other_user_response.status_code == 404
