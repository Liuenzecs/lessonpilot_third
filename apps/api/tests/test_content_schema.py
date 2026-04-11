from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schemas.content import ContentDocument


def test_content_document_accepts_phase2_block_types():
    payload = {
        "version": 3,
        "blocks": [
            {
                "id": "section-1",
                "type": "section",
                "title": "练习巩固",
                "status": "confirmed",
                "source": "human",
                "children": [
                    {
                        "id": "group-1",
                        "type": "exercise_group",
                        "title": "基础题组",
                        "status": "confirmed",
                        "source": "human",
                        "children": [
                            {
                                "id": "choice-1",
                                "type": "choice_question",
                                "status": "confirmed",
                                "source": "human",
                                "prompt": "<p>题干</p>",
                                "options": ["A", "B", "C", "D"],
                                "answers": ["B"],
                                "analysis": "<p>解析</p>",
                            },
                            {
                                "id": "blank-1",
                                "type": "fill_blank_question",
                                "status": "confirmed",
                                "source": "human",
                                "prompt": "<p>填空</p>",
                                "answers": ["答案"],
                                "analysis": "<p>解析</p>",
                            },
                            {
                                "id": "short-1",
                                "type": "short_answer_question",
                                "status": "confirmed",
                                "source": "human",
                                "prompt": "<p>简答</p>",
                                "referenceAnswer": "<p>参考答案</p>",
                                "analysis": "<p>解析</p>",
                            },
                        ],
                    }
                ],
            }
        ],
    }

    document = ContentDocument.model_validate(payload)
    exercise_group = document.blocks[0].children[0]
    assert exercise_group.type == "exercise_group"
    assert exercise_group.children[0].type == "choice_question"
    assert exercise_group.children[1].type == "fill_blank_question"
    assert exercise_group.children[2].type == "short_answer_question"


def test_content_document_rejects_invalid_container_nesting():
    payload = {
        "version": 1,
        "blocks": [
            {
                "id": "section-1",
                "type": "section",
                "title": "错误结构",
                "status": "confirmed",
                "source": "human",
                "children": [
                    {
                        "id": "choice-1",
                        "type": "choice_question",
                        "status": "confirmed",
                        "source": "human",
                        "prompt": "<p>题干</p>",
                        "options": ["A", "B"],
                        "answers": ["A"],
                        "analysis": "<p>解析</p>",
                    }
                ],
            }
        ],
    }

    with pytest.raises(ValidationError):
        ContentDocument.model_validate(payload)


def test_replace_suggestion_requires_target_and_action():
    payload = {
        "version": 1,
        "blocks": [
            {
                "id": "section-1",
                "type": "section",
                "title": "教学目标",
                "status": "confirmed",
                "source": "human",
                "children": [
                    {
                        "id": "paragraph-1",
                        "type": "paragraph",
                        "status": "pending",
                        "source": "ai",
                        "content": "<p>建议内容</p>",
                        "suggestion": {"kind": "replace"},
                    }
                ],
            }
        ],
    }

    with pytest.raises(ValidationError):
        ContentDocument.model_validate(payload)


def test_selection_replace_suggestion_keeps_context_and_indent():
    payload = {
        "version": 2,
        "blocks": [
            {
                "id": "section-1",
                "type": "section",
                "title": "导入环节",
                "status": "confirmed",
                "source": "human",
                "children": [
                    {
                        "id": "paragraph-1",
                        "type": "paragraph",
                        "status": "confirmed",
                        "source": "human",
                        "content": "<p>原始段落</p>",
                        "indent": 2,
                    },
                    {
                        "id": "paragraph-2",
                        "type": "paragraph",
                        "status": "pending",
                        "source": "ai",
                        "content": "<p>AI 建议</p>",
                        "indent": 2,
                        "suggestion": {
                            "kind": "replace",
                            "targetBlockId": "paragraph-1",
                            "action": "polish",
                            "mode": "selection",
                            "selectionText": "原始段落",
                        },
                    },
                ],
            }
        ],
    }

    document = ContentDocument.model_validate(payload)
    source_block = document.blocks[0].children[0]
    suggestion_block = document.blocks[0].children[1]
    assert source_block.indent == 2
    assert suggestion_block.indent == 2
    assert suggestion_block.suggestion is not None
    assert suggestion_block.suggestion.mode == "selection"
    assert suggestion_block.suggestion.selection_text == "原始段落"
