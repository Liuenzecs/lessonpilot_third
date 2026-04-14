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


def test_task_creation_with_new_fields(client, auth_headers):
    create_response = client.post(
        "/api/v1/tasks/",
        headers=auth_headers,
        json={
            "subject": "语文",
            "grade": "七年级",
            "topic": "春",
            "requirements": "侧重朗读训练",
            "scene": "public_school",
            "lesson_type": "lesson_plan",
            "class_hour": 1,
            "lesson_category": "new",
        },
    )
    assert create_response.status_code == 201
    task = create_response.json()
    assert task["subject"] == "语文"
    assert task["scene"] == "public_school"
    assert task["lesson_type"] == "lesson_plan"
    assert task["class_hour"] == 1
    assert task["lesson_category"] == "new"


def test_task_creation_with_both_generates_two_documents(client, auth_headers):
    create_response = client.post(
        "/api/v1/tasks/",
        headers=auth_headers,
        json={
            "subject": "语文",
            "grade": "七年级",
            "topic": "春",
            "lesson_type": "both",
        },
    )
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    documents_response = client.get(f"/api/v1/documents/?task_id={task_id}", headers=auth_headers)
    assert documents_response.status_code == 200
    docs = documents_response.json()["items"]
    assert len(docs) == 2
    doc_types = {doc["doc_type"] for doc in docs}
    assert "lesson_plan" in doc_types
    assert "study_guide" in doc_types


def test_task_document_generation_flow(client, auth_headers):
    create_response = client.post(
        "/api/v1/tasks/",
        headers=auth_headers,
        json={
            "subject": "语文",
            "grade": "七年级",
            "topic": "春",
            "requirements": "侧重朗读",
        },
    )
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    tasks_response = client.get("/api/v1/tasks/?page=1&page_size=20", headers=auth_headers)
    assert tasks_response.status_code == 200
    assert tasks_response.json()["total"] == 1

    documents_response = client.get(f"/api/v1/documents/?task_id={task_id}", headers=auth_headers)
    assert documents_response.status_code == 200
    doc = documents_response.json()["items"][0]
    document_id = doc["id"]
    assert doc["content"]["doc_type"] == "lesson_plan"

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
    assert "status" in event_names
    assert "progress" in event_names
    assert "done" in event_names
    # Sprint 3：流式 section 级事件
    assert "section_delta" in event_names
    assert "document" in event_names

    refreshed_document = client.get(f"/api/v1/documents/{document_id}", headers=auth_headers).json()
    assert refreshed_document["content"]["doc_type"] == "lesson_plan"
    assert refreshed_document["content"]["objectives_status"] == "pending"

    # 更新文档内容
    content = refreshed_document["content"]
    content["objectives_status"] = "confirmed"
    update_response = client.patch(
        f"/api/v1/documents/{document_id}",
        headers=auth_headers,
        json={
            "version": refreshed_document["version"],
            "content": content,
        },
    )
    assert update_response.status_code == 200

    conflict_response = client.patch(
        f"/api/v1/documents/{document_id}",
        headers=auth_headers,
        json={
            "version": refreshed_document["version"],
            "content": content,
        },
    )
    assert conflict_response.status_code == 409

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


def test_duplicate_task_copies_all_documents(client, auth_headers):
    create_response = client.post(
        "/api/v1/tasks/",
        headers=auth_headers,
        json={
            "subject": "语文",
            "grade": "七年级",
            "topic": "济南的冬天",
            "lesson_type": "both",
        },
    )
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    dup_response = client.post(
        f"/api/v1/tasks/{task_id}/duplicate",
        headers=auth_headers,
    )
    assert dup_response.status_code == 201
    dup_task = dup_response.json()
    assert dup_task["title"].endswith("（副本）")

    dup_docs = client.get(f"/api/v1/documents/?task_id={dup_task['id']}", headers=auth_headers)
    assert len(dup_docs.json()["items"]) == 2
