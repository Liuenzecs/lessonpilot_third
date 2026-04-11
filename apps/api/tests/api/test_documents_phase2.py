from __future__ import annotations

import json
from types import SimpleNamespace

from app.schemas.content import ContentDocument
from app.services.export_service import _build_export_html


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


def _create_task_and_document(client, auth_headers):
    create_response = client.post(
        "/api/v1/tasks/",
        headers=auth_headers,
        json={
            "subject": "数学",
            "grade": "八年级",
            "topic": "一元二次方程",
            "requirements": "突出题组训练",
        },
    )
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]
    document_response = client.get(f"/api/v1/documents/?task_id={task_id}", headers=auth_headers)
    document = document_response.json()["items"][0]
    return task_id, document


def _seed_paragraph_block(client, auth_headers, document):
    content = document["content"]
    first_section = content["blocks"][0]
    paragraph_id = "paragraph-seed-1"
    first_section["children"] = [
        {
            "id": paragraph_id,
            "type": "paragraph",
            "status": "confirmed",
            "source": "human",
            "content": "<p>原始段落内容</p>",
        }
    ]
    update_response = client.patch(
        f"/api/v1/documents/{document['id']}",
        headers=auth_headers,
        json={"version": document["version"], "content": content},
    )
    assert update_response.status_code == 200
    return update_response.json(), paragraph_id


def test_generation_supports_exercise_groups_and_questions(client, auth_headers):
    task_id, document = _create_task_and_document(client, auth_headers)

    start_response = client.post(
        f"/api/v1/tasks/{task_id}/generate",
        headers=auth_headers,
        json={},
    )
    stream_url = start_response.json()["stream_url"]

    with client.stream("GET", stream_url, headers=auth_headers) as stream_response:
        payload = "".join(stream_response.iter_text())
    events = _parse_sse_events(payload)
    assert events[-1][0] == "done"

    refreshed = client.get(f"/api/v1/documents/{document['id']}", headers=auth_headers).json()
    exercise_groups = [
        child
        for section in refreshed["content"]["blocks"]
        for child in section.get("children", [])
        if child["type"] == "exercise_group"
    ]
    assert exercise_groups
    assert exercise_groups[0]["children"][0]["type"] in {
        "choice_question",
        "fill_blank_question",
        "short_answer_question",
    }


def test_rewrite_flow_and_history_restore(client, auth_headers):
    _, document = _create_task_and_document(client, auth_headers)
    updated_document, paragraph_id = _seed_paragraph_block(client, auth_headers, document)

    rewrite_start = client.post(
        f"/api/v1/documents/{updated_document['id']}/rewrite",
        headers=auth_headers,
        json={
            "document_version": updated_document["version"],
            "mode": "block",
            "target_block_id": paragraph_id,
            "action": "rewrite",
        },
    )
    assert rewrite_start.status_code == 200

    with client.stream("GET", rewrite_start.json()["stream_url"], headers=auth_headers) as stream_response:
        events = _parse_sse_events("".join(stream_response.iter_text()))
    assert events[-1][0] == "done"

    rewritten_document = client.get(
        f"/api/v1/documents/{updated_document['id']}",
        headers=auth_headers,
    ).json()
    children = rewritten_document["content"]["blocks"][0]["children"]
    assert children[0]["id"] == paragraph_id
    assert children[1]["status"] == "pending"
    assert children[1]["suggestion"]["kind"] == "replace"
    assert children[1]["suggestion"]["targetBlockId"] == paragraph_id

    selection_start = client.post(
        f"/api/v1/documents/{updated_document['id']}/rewrite",
        headers=auth_headers,
        json={
            "document_version": rewritten_document["version"],
            "mode": "selection",
            "target_block_id": paragraph_id,
            "action": "polish",
            "selection_text": "原始段落内容",
        },
    )
    assert selection_start.status_code == 200

    with client.stream("GET", selection_start.json()["stream_url"], headers=auth_headers) as stream_response:
        selection_events = _parse_sse_events("".join(stream_response.iter_text()))
    assert selection_events[-1][0] == "done"

    current_document = client.get(
        f"/api/v1/documents/{updated_document['id']}",
        headers=auth_headers,
    ).json()

    for index in range(11):
        content = current_document["content"]
        content["blocks"][0]["children"][0]["content"] = f"<p>第 {index} 次保存</p>"
        patch_response = client.patch(
            f"/api/v1/documents/{updated_document['id']}",
            headers=auth_headers,
            json={"version": current_document["version"], "content": content},
        )
        assert patch_response.status_code == 200
        current_document = patch_response.json()

    history_response = client.get(
        f"/api/v1/documents/{updated_document['id']}/history?limit=10",
        headers=auth_headers,
    )
    assert history_response.status_code == 200
    history_items = history_response.json()["items"]
    assert len(history_items) == 10
    assert history_items[0]["version"] == current_document["version"]

    snapshot_id = history_items[-1]["id"]
    snapshot_response = client.get(
        f"/api/v1/documents/{updated_document['id']}/history/{snapshot_id}",
        headers=auth_headers,
    )
    assert snapshot_response.status_code == 200

    restored = client.post(
        f"/api/v1/documents/{updated_document['id']}/history/{snapshot_id}/restore",
        headers=auth_headers,
    )
    assert restored.status_code == 200
    assert restored.json()["version"] > current_document["version"]

    latest_history = client.get(
        f"/api/v1/documents/{updated_document['id']}/history?limit=1",
        headers=auth_headers,
    ).json()["items"][0]
    assert latest_history["source"] == "restore"


def test_append_flow_and_error_cases(client, auth_headers):
    _, document = _create_task_and_document(client, auth_headers)
    section_id = document["content"]["blocks"][0]["id"]

    unauthorized = client.post(
        f"/api/v1/documents/{document['id']}/append",
        json={
            "document_version": document["version"],
            "section_id": section_id,
            "instruction": "补充一段导入语",
        },
    )
    assert unauthorized.status_code == 401

    version_conflict = client.post(
        f"/api/v1/documents/{document['id']}/append",
        headers=auth_headers,
        json={
            "document_version": document["version"] + 1,
            "section_id": section_id,
            "instruction": "补充一段导入语",
        },
    )
    assert version_conflict.status_code == 409

    append_start = client.post(
        f"/api/v1/documents/{document['id']}/append",
        headers=auth_headers,
        json={
            "document_version": document["version"],
            "section_id": section_id,
            "instruction": "补充一段导入语",
        },
    )
    assert append_start.status_code == 200

    with client.stream("GET", append_start.json()["stream_url"], headers=auth_headers) as stream_response:
        events = _parse_sse_events("".join(stream_response.iter_text()))
    assert [name for name, _ in events] == ["status", "progress", "document", "progress", "document", "status", "done"]

    appended_document = client.get(
        f"/api/v1/documents/{document['id']}",
        headers=auth_headers,
    ).json()
    appended_children = appended_document["content"]["blocks"][0]["children"]
    assert appended_children
    assert appended_children[-1]["status"] == "pending"
    assert appended_children[-1]["source"] == "ai"
    assert appended_children[-1]["suggestion"]["kind"] == "append"

    latest_history = client.get(
        f"/api/v1/documents/{document['id']}/history?limit=1",
        headers=auth_headers,
    ).json()["items"][0]
    assert latest_history["source"] == "append_ai"

    invalid_section_start = client.post(
        f"/api/v1/documents/{document['id']}/append",
        headers=auth_headers,
        json={
            "document_version": appended_document["version"],
            "section_id": "missing-section",
            "instruction": "补充一段导入语",
        },
    )
    assert invalid_section_start.status_code == 200
    with client.stream("GET", invalid_section_start.json()["stream_url"], headers=auth_headers) as stream_response:
        invalid_events = _parse_sse_events("".join(stream_response.iter_text()))
    assert invalid_events[-1][0] == "error"
    assert invalid_events[-1][1]["message"] == "404: Section not found"


def test_pdf_export_returns_pdf_and_excludes_pending(client, auth_headers):
    task_id, document = _create_task_and_document(client, auth_headers)
    updated_document, _ = _seed_paragraph_block(client, auth_headers, document)

    content = updated_document["content"]
    content["blocks"][0]["children"].append(
        {
            "id": "pending-1",
            "type": "paragraph",
            "status": "pending",
            "source": "ai",
            "content": "<p>这段待确认内容不应导出</p>",
            "suggestion": {"kind": "append"},
        }
    )
    patch_response = client.patch(
        f"/api/v1/documents/{updated_document['id']}",
        headers=auth_headers,
        json={"version": updated_document["version"], "content": content},
    )
    assert patch_response.status_code == 200

    task = client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers).json()
    html = _build_export_html(
        SimpleNamespace(**task),
        ContentDocument.model_validate(patch_response.json()["content"]),
    )
    assert "这段待确认内容不应导出" not in html

    export_response = client.get(
        f"/api/v1/documents/{updated_document['id']}/export?format=pdf",
        headers=auth_headers,
    )
    assert export_response.status_code == 200
    assert export_response.headers["content-type"] == "application/pdf"
    assert export_response.content[:4] == b"%PDF"
