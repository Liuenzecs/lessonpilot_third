from __future__ import annotations

import json
from pathlib import Path

from app.schemas.content import ExerciseGroupBlock
from app.services.llm_service import (
    _normalize_generated_payload,
    _render_prompt_template,
    apply_suggestion_metadata,
)


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


def test_apply_suggestion_metadata_marks_nested_blocks():
    blocks = _normalize_generated_payload(
        {
            "blocks": [
                {
                    "type": "exercise_group",
                    "title": "题组",
                    "children": [
                        {
                            "type": "choice_question",
                            "prompt": "<p>题干</p>",
                            "options": ["A", "B"],
                            "answers": ["A"],
                            "analysis": "<p>解析</p>",
                        }
                    ],
                }
            ]
        }
    )["blocks"]

    payload = {"blocks": blocks}
    validated = apply_suggestion_metadata(
        [ExerciseGroupBlock.model_validate(payload["blocks"][0])],
        kind="replace",
        target_block_id="target-1",
        action="rewrite",
    )

    assert validated[0].suggestion is not None
    assert validated[0].suggestion.kind == "replace"
    assert validated[0].suggestion.target_block_id == "target-1"
    assert validated[0].children[0].suggestion is not None
    assert validated[0].children[0].suggestion.target_block_id == "target-1"


def test_render_prompt_template_preserves_literal_json_braces():
    api_root = Path(__file__).resolve().parents[1]
    prompt = _render_prompt_template(
        api_root / "app" / "prompts" / "lesson_section_generation_prompt.md",
        subject="数学",
        grade="八年级",
        topic="一元二次方程",
        requirements="重点讲解配方法",
        section_title="导入环节",
    )

    assert '{"blocks":[...]}' in prompt
    assert "Subject: 数学" in prompt
    assert "{subject}" not in prompt
