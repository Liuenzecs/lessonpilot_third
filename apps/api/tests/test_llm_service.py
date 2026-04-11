from __future__ import annotations

import json

from app.services.llm_service import _normalize_generated_payload


def test_normalize_generated_payload_adds_missing_metadata():
    payload = _normalize_generated_payload(
        {
            "blocks": [
                {
                    "type": "teaching_step",
                    "title": "情境导入",
                    "durationMinutes": 5,
                    "children": [
                        {
                            "type": "paragraph",
                            "content": "<p>引导学生回顾旧知。</p>",
                        }
                    ],
                }
            ]
        }
    )

    block = payload["blocks"][0]
    assert block["id"]
    assert block["status"] == "pending"
    assert block["source"] == "ai"
    assert block["children"][0]["id"]
    assert block["children"][0]["status"] == "pending"
    assert block["children"][0]["source"] == "ai"


def test_normalize_generated_payload_accepts_bare_blocks_array():
    payload = _normalize_generated_payload(
        json.loads(
            '[{"type":"list","items":["A","B"],"status":"pending","source":"ai"}]'
        )
    )

    assert len(payload["blocks"]) == 1
    assert payload["blocks"][0]["type"] == "list"
    assert payload["blocks"][0]["id"]
