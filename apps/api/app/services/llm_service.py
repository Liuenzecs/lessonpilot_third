from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

import httpx
from fastapi import HTTPException, status

from app.core.config import get_settings
from app.schemas.content import GeneratedBlocksPayload, ListBlock, ParagraphBlock, TeachingStepBlock

PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "lesson_section_generation_prompt.md"


@dataclass(slots=True)
class SectionGenerationContext:
    subject: str
    grade: str
    topic: str
    requirements: str | None
    section_title: str


def _normalize_block_payload(block: dict) -> dict:
    normalized = dict(block)
    normalized.setdefault("id", str(uuid4()))
    normalized.setdefault("status", "pending")
    normalized.setdefault("source", "ai")

    if normalized.get("type") in {"section", "teaching_step"}:
        children = normalized.get("children") or []
        normalized["children"] = [
            _normalize_block_payload(child)
            for child in children
            if isinstance(child, dict)
        ]

    return normalized


def _normalize_generated_payload(raw_payload: object) -> dict:
    if isinstance(raw_payload, list):
        blocks = raw_payload
    elif isinstance(raw_payload, dict):
        if isinstance(raw_payload.get("blocks"), list):
            blocks = raw_payload["blocks"]
        elif isinstance(raw_payload.get("data"), dict) and isinstance(raw_payload["data"].get("blocks"), list):
            blocks = raw_payload["data"]["blocks"]
        else:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="LLM response is missing blocks payload",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="LLM response payload is not valid JSON",
        )

    return {
        "blocks": [_normalize_block_payload(block) for block in blocks if isinstance(block, dict)],
    }


class FakeProvider:
    async def generate_section(self, context: SectionGenerationContext):
        if context.section_title == "教学目标":
            return [
                ListBlock(
                    id=str(uuid4()),
                    status="pending",
                    source="ai",
                    items=[
                        f"理解《{context.topic}》的核心知识点与基本概念。",
                        f"能够结合{context.subject}课堂情境完成基础练习。",
                        "在课堂表达和合作中形成清晰的解题或表达思路。",
                    ],
                )
            ]

        if context.section_title == "教学重难点":
            return [
                ParagraphBlock(
                    id=str(uuid4()),
                    status="pending",
                    source="ai",
                    content=(
                        f"<p><strong>教学重点：</strong>围绕“{context.topic}”建立核心概念和基础方法。</p>"
                        "<p><strong>教学难点：</strong>帮助学生把抽象知识迁移到真实题目或课堂任务中。</p>"
                    ),
                )
            ]

        if context.section_title == "导入环节":
            return [
                TeachingStepBlock(
                    id=str(uuid4()),
                    status="pending",
                    source="ai",
                    title="情境导入",
                    durationMinutes=5,
                    children=[
                        ParagraphBlock(
                            id=str(uuid4()),
                            status="pending",
                            source="ai",
                            content=(
                                f"<p>教师通过贴近学生生活的案例引出“{context.topic}”，"
                                "先唤醒已有经验，再抛出本节核心问题。</p>"
                            ),
                        )
                    ],
                )
            ]

        if context.section_title == "新授环节":
            return [
                TeachingStepBlock(
                    id=str(uuid4()),
                    status="pending",
                    source="ai",
                    title="概念建构",
                    durationMinutes=12,
                    children=[
                        ParagraphBlock(
                            id=str(uuid4()),
                            status="pending",
                            source="ai",
                            content=(
                                f"<p>教师聚焦“{context.topic}”的关键概念，通过例子、板书和追问帮助学生完成初步理解。</p>"
                            ),
                        )
                    ],
                ),
                TeachingStepBlock(
                    id=str(uuid4()),
                    status="pending",
                    source="ai",
                    title="方法应用",
                    durationMinutes=15,
                    children=[
                        ListBlock(
                            id=str(uuid4()),
                            status="pending",
                            source="ai",
                            items=[
                                "教师示范一题，强调思路与步骤。",
                                "学生同桌讨论并尝试独立完成一题。",
                                "教师组织反馈，纠正常见错误。",
                            ],
                        )
                    ],
                ),
            ]

        if context.section_title == "练习巩固":
            return [
                ListBlock(
                    id=str(uuid4()),
                    status="pending",
                    source="ai",
                    items=[
                        "基础题：检验学生是否掌握核心概念。",
                        "变式题：考查学生迁移与比较能力。",
                        "提高题：鼓励学生用完整语言说明思路。",
                    ],
                )
            ]

        return [
            ParagraphBlock(
                id=str(uuid4()),
                status="pending",
                source="ai",
                content=(
                    f"<p>教师引导学生回顾本节围绕“{context.topic}”学习到的重点内容，并布置课后巩固任务。</p>"
                ),
            )
        ]


class DeepSeekProvider:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def generate_section(self, context: SectionGenerationContext):
        if not self.settings.deepseek_api_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="DeepSeek API key is not configured",
            )

        prompt = PROMPT_PATH.read_text(encoding="utf-8").format(
            subject=context.subject,
            grade=context.grade,
            topic=context.topic,
            requirements=context.requirements or "无",
            section_title=context.section_title,
        )
        endpoint = f"{self.settings.deepseek_base_url.rstrip('/')}/chat/completions"
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                endpoint,
                headers={"Authorization": f"Bearer {self.settings.deepseek_api_key}"},
                json={
                    "model": self.settings.deepseek_model,
                    "messages": [
                        {"role": "system", "content": "You generate structured teaching plan JSON only."},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.5,
                },
            )
            response.raise_for_status()

        content = response.json()["choices"][0]["message"]["content"]
        cleaned = content.strip().removeprefix("```json").removesuffix("```").strip()
        payload = GeneratedBlocksPayload.model_validate(
            _normalize_generated_payload(json.loads(cleaned))
        )
        return payload.blocks


def get_provider():
    settings = get_settings()
    if settings.llm_provider == "deepseek":
        return DeepSeekProvider()
    return FakeProvider()
