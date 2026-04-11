from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

import httpx
from fastapi import HTTPException, status

from app.core.config import get_settings
from app.schemas.content import (
    Block,
    ChoiceQuestionBlock,
    ExerciseGroupBlock,
    FillBlankQuestionBlock,
    GeneratedBlocksPayload,
    ListBlock,
    ParagraphBlock,
    ShortAnswerQuestionBlock,
    TeachingStepBlock,
)

SECTION_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "lesson_section_generation_prompt.md"
REWRITE_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "lesson_rewrite_prompt.md"
APPEND_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "lesson_append_prompt.md"


@dataclass(slots=True)
class SectionGenerationContext:
    subject: str
    grade: str
    topic: str
    requirements: str | None
    section_title: str


@dataclass(slots=True)
class RewriteContext:
    subject: str
    grade: str
    topic: str
    requirements: str | None
    section_title: str | None
    mode: str
    action: str
    target_block_id: str
    target_block_type: str
    target_block_payload: dict
    selection_text: str | None


@dataclass(slots=True)
class AppendContext:
    subject: str
    grade: str
    topic: str
    requirements: str | None
    section_title: str
    instruction: str


def _normalize_block_payload(block: dict) -> dict:
    normalized = dict(block)
    normalized.setdefault("id", str(uuid4()))
    normalized.setdefault("status", "pending")
    normalized.setdefault("source", "ai")

    if normalized.get("type") == "paragraph":
        normalized.setdefault("content", "")
    elif normalized.get("type") == "list":
        normalized["items"] = [str(item) for item in (normalized.get("items") or [])]
    elif normalized.get("type") == "teaching_step":
        if "duration_minutes" in normalized and "durationMinutes" not in normalized:
            normalized["durationMinutes"] = normalized.pop("duration_minutes")
        normalized.setdefault("title", "")
    elif normalized.get("type") == "exercise_group":
        normalized.setdefault("title", "")
    elif normalized.get("type") == "choice_question":
        normalized.setdefault("prompt", "")
        normalized["options"] = [str(item) for item in (normalized.get("options") or [])]
        normalized["answers"] = [str(item) for item in (normalized.get("answers") or [])]
        normalized.setdefault("analysis", "")
    elif normalized.get("type") == "fill_blank_question":
        normalized.setdefault("prompt", "")
        normalized["answers"] = [str(item) for item in (normalized.get("answers") or [])]
        normalized.setdefault("analysis", "")
    elif normalized.get("type") == "short_answer_question":
        if "reference_answer" in normalized and "referenceAnswer" not in normalized:
            normalized["referenceAnswer"] = normalized.pop("reference_answer")
        normalized.setdefault("prompt", "")
        normalized.setdefault("referenceAnswer", "")
        normalized.setdefault("analysis", "")

    if normalized.get("type") in {"section", "teaching_step", "exercise_group"}:
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


def _apply_suggestion(block_payload: dict, suggestion: dict) -> dict:
    normalized = dict(block_payload)
    normalized["suggestion"] = suggestion
    if normalized.get("type") in {"section", "teaching_step", "exercise_group"}:
        normalized["children"] = [
            _apply_suggestion(child, suggestion) for child in normalized.get("children", [])
        ]
    return normalized


def apply_suggestion_metadata(
    blocks: list[Block],
    *,
    kind: str,
    target_block_id: str | None = None,
    action: str | None = None,
) -> list[Block]:
    suggestion: dict[str, str] = {"kind": kind}
    if target_block_id:
        suggestion["targetBlockId"] = target_block_id
    if action:
        suggestion["action"] = action

    payload = {
        "blocks": [
            _apply_suggestion(block.model_dump(mode="json", by_alias=True), suggestion) for block in blocks
        ]
    }
    return GeneratedBlocksPayload.model_validate(payload).blocks


def _strip_code_fence(value: str) -> str:
    return value.strip().removeprefix("```json").removesuffix("```").strip()


def _json_dump(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)


def _render_prompt_template(template_path: Path, **values: object) -> str:
    prompt = template_path.read_text(encoding="utf-8")
    for key, value in values.items():
        prompt = prompt.replace(f"{{{key}}}", str(value))
    return prompt


class FakeProvider:
    async def generate_section(self, context: SectionGenerationContext):
        if context.section_title == "教学目标":
            return [
                ListBlock(
                    id=str(uuid4()),
                    status="pending",
                    source="ai",
                    items=[
                        f"理解《{context.topic}》中的核心知识点与基本概念。",
                        f"能够结合{context.subject}课堂情境完成基础练习。",
                        "能用清晰语言表达本节课的关键思路与学习收获。",
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
                        f"<p><strong>教学重点：</strong>围绕“{context.topic}”建立核心概念和方法。</p>"
                        "<p><strong>教学难点：</strong>帮助学生将抽象知识迁移到真实题目和课堂任务中。</p>"
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
                                f"<p>教师从贴近学生生活的案例切入“{context.topic}”，先唤醒已有经验，再提出本课核心问题。</p>"
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
                                f"<p>教师聚焦“{context.topic}”的关键概念，通过例子、板书和追问帮助学生建立初步理解。</p>"
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
                                "教师示范一道例题，强调思路与步骤。",
                                "学生同伴讨论并尝试独立完成一题。",
                                "教师组织反馈并纠正常见错误。",
                            ],
                        )
                    ],
                ),
            ]

        if context.section_title == "练习巩固":
            return [
                ExerciseGroupBlock(
                    id=str(uuid4()),
                    status="pending",
                    source="ai",
                    title="分层练习",
                    children=[
                        ChoiceQuestionBlock(
                            id=str(uuid4()),
                            status="pending",
                            source="ai",
                            prompt=f"<p>下列选项中，最符合“{context.topic}”核心判断的是哪一项？</p>",
                            options=["选项 A", "选项 B", "选项 C", "选项 D"],
                            answers=["选项 B"],
                            analysis="<p>先抓住概念关键词，再排除干扰项。</p>",
                        ),
                        FillBlankQuestionBlock(
                            id=str(uuid4()),
                            status="pending",
                            source="ai",
                            prompt=f"<p>请根据本节课所学，补全与“{context.topic}”相关的关键结论：______。</p>",
                            answers=["示例答案"],
                            analysis="<p>提醒学生回到课堂板书中的核心结论。</p>",
                        ),
                        ShortAnswerQuestionBlock(
                            id=str(uuid4()),
                            status="pending",
                            source="ai",
                            prompt=f"<p>请结合本节课内容，简要说明“{context.topic}”在实际问题中的应用。</p>",
                            referenceAnswer="<p>先说明概念，再结合题目或生活情境举例。</p>",
                            analysis="<p>重点看学生是否说清思路，而不是只写结果。</p>",
                        ),
                    ],
                )
            ]

        return [
            ParagraphBlock(
                id=str(uuid4()),
                status="pending",
                source="ai",
                content=(
                    f"<p>教师带领学生回顾围绕“{context.topic}”学习到的重点内容，并布置课后巩固任务。</p>"
                ),
            )
        ]

    async def rewrite_block(self, context: RewriteContext):
        action_label = {
            "rewrite": "重写",
            "polish": "润色",
            "expand": "扩写",
        }[context.action]
        selection_text = context.selection_text.strip() if context.selection_text else ""

        if context.mode == "selection":
            return ParagraphBlock(
                id=str(uuid4()),
                status="pending",
                source="ai",
                content=(
                    f"<p>以下内容已经过AI{action_label}：{selection_text or '所选内容'}。"
                    f"建议将表述进一步贴近“{context.topic}”的课堂语境。</p>"
                ),
            )

        if context.target_block_type == "paragraph":
            return ParagraphBlock(
                id=str(uuid4()),
                status="pending",
                source="ai",
                content=(
                    f"<p>AI已对该段落进行{action_label}，内容更聚焦“{context.topic}”的教学目标、课堂活动与学生产出。</p>"
                ),
            )

        if context.target_block_type == "list":
            return ListBlock(
                id=str(uuid4()),
                status="pending",
                source="ai",
                items=[
                    f"围绕“{context.topic}”补充更清晰的步骤说明。",
                    "突出学生操作和教师反馈的对应关系。",
                    "保留可直接进入课堂使用的表达方式。",
                ],
            )

        if context.target_block_type == "teaching_step":
            return TeachingStepBlock(
                id=str(uuid4()),
                status="pending",
                source="ai",
                title=f"{action_label}后的教学步骤",
                durationMinutes=8,
                children=[
                    ParagraphBlock(
                        id=str(uuid4()),
                        status="pending",
                        source="ai",
                        content="<p>教师先明确任务，再组织学生观察、讨论与反馈，保证步骤更加完整。</p>",
                    ),
                    ListBlock(
                        id=str(uuid4()),
                        status="pending",
                        source="ai",
                        items=[
                            "明确任务目标",
                            "组织学生实践",
                            "集中讲评与纠错",
                        ],
                    ),
                ],
            )

        if context.target_block_type == "exercise_group":
            return ExerciseGroupBlock(
                id=str(uuid4()),
                status="pending",
                source="ai",
                title=f"{action_label}后的题组",
                children=[
                    ChoiceQuestionBlock(
                        id=str(uuid4()),
                        status="pending",
                        source="ai",
                        prompt=f"<p>下列哪一项最能体现“{context.topic}”的关键判断？</p>",
                        options=["选项 A", "选项 B", "选项 C", "选项 D"],
                        answers=["选项 C"],
                        analysis="<p>注意抓住题干中的限制条件。</p>",
                    ),
                    ShortAnswerQuestionBlock(
                        id=str(uuid4()),
                        status="pending",
                        source="ai",
                        prompt=f"<p>请说明“{context.topic}”在课堂练习中的应用步骤。</p>",
                        referenceAnswer="<p>先概括知识点，再给出应用过程，最后说明结果。</p>",
                        analysis="<p>学生只要能说清步骤即可。</p>",
                    ),
                ],
            )

        if context.target_block_type == "choice_question":
            return ChoiceQuestionBlock(
                id=str(uuid4()),
                status="pending",
                source="ai",
                prompt=f"<p>AI已{action_label}这道选择题，请判断哪一项更符合“{context.topic}”的教学目标。</p>",
                options=["选项 A", "选项 B", "选项 C", "选项 D"],
                answers=["选项 A"],
                analysis="<p>新的题干更强调课堂目标和思维过程。</p>",
            )

        if context.target_block_type == "fill_blank_question":
            return FillBlankQuestionBlock(
                id=str(uuid4()),
                status="pending",
                source="ai",
                prompt=f"<p>请补全与“{context.topic}”相关的关键表达：______。</p>",
                answers=["AI建议答案"],
                analysis="<p>关注学生是否写出课堂核心概念。</p>",
            )

        return ShortAnswerQuestionBlock(
            id=str(uuid4()),
            status="pending",
            source="ai",
            prompt=f"<p>请围绕“{context.topic}”回答这道经过AI{action_label}的简答题。</p>",
            referenceAnswer="<p>答案应包含核心概念、操作步骤和简要说明。</p>",
            analysis="<p>评价时重点关注表达是否完整。</p>",
        )

    async def generate_append(self, context: AppendContext):
        instruction = context.instruction.strip()

        if any(keyword in instruction for keyword in ["练习", "题", "习题"]):
            return [
                ExerciseGroupBlock(
                    id=str(uuid4()),
                    status="pending",
                    source="ai",
                    title="AI 补充练习",
                    children=[
                        ChoiceQuestionBlock(
                            id=str(uuid4()),
                            status="pending",
                            source="ai",
                            prompt=f"<p>围绕“{context.topic}”，请判断哪一项最符合本节课的关键理解。</p>",
                            options=["选项 A", "选项 B", "选项 C", "选项 D"],
                            answers=["选项 B"],
                            analysis="<p>先回到课堂中的核心概念，再排除明显干扰项。</p>",
                        )
                    ],
                )
            ]

        if any(keyword in instruction for keyword in ["步骤", "流程", "活动"]):
            return [
                TeachingStepBlock(
                    id=str(uuid4()),
                    status="pending",
                    source="ai",
                    title="AI 补充教学活动",
                    durationMinutes=8,
                    children=[
                        ParagraphBlock(
                            id=str(uuid4()),
                            status="pending",
                            source="ai",
                            content=(
                                f"<p>教师根据“{context.topic}”补充一个可直接进入课堂执行的活动，"
                                "先明确任务，再组织学生反馈。</p>"
                            ),
                        ),
                        ListBlock(
                            id=str(uuid4()),
                            status="pending",
                            source="ai",
                            items=[
                                "说明任务目标与评价标准。",
                                "组织学生独立或同伴完成活动。",
                                "用板书或口头反馈收束关键结论。",
                            ],
                        ),
                    ],
                )
            ]

        if any(keyword in instruction for keyword in ["要点", "列表", "清单"]):
            return [
                ListBlock(
                    id=str(uuid4()),
                    status="pending",
                    source="ai",
                    items=[
                        f"围绕“{context.topic}”补充一条更贴近课堂的操作要点。",
                        "明确学生需要完成的观察、表达或计算任务。",
                        "提示教师在点评时重点抓住常见易错点。",
                    ],
                )
            ]

        return [
            ParagraphBlock(
                id=str(uuid4()),
                status="pending",
                source="ai",
                content=(
                    f"<p>根据补充要求“{instruction}”，AI 为“{context.section_title}”追加了一段更贴近课堂使用的内容，"
                    f"帮助教师继续完善“{context.topic}”这节课的教案。</p>"
                ),
            )
        ]


class DeepSeekProvider:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def _complete_json(self, prompt: str) -> list[Block]:
        if not self.settings.deepseek_api_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="DeepSeek API key is not configured",
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
        payload = GeneratedBlocksPayload.model_validate(
            _normalize_generated_payload(json.loads(_strip_code_fence(content)))
        )
        return payload.blocks

    async def generate_section(self, context: SectionGenerationContext):
        prompt = _render_prompt_template(
            SECTION_PROMPT_PATH,
            subject=context.subject,
            grade=context.grade,
            topic=context.topic,
            requirements=context.requirements or "无",
            section_title=context.section_title,
        )
        return await self._complete_json(prompt)

    async def rewrite_block(self, context: RewriteContext):
        prompt = _render_prompt_template(
            REWRITE_PROMPT_PATH,
            subject=context.subject,
            grade=context.grade,
            topic=context.topic,
            requirements=context.requirements or "无",
            section_title=context.section_title or "未定位章节",
            mode=context.mode,
            action=context.action,
            target_block_id=context.target_block_id,
            target_block_type=context.target_block_type,
            target_block_payload=_json_dump(context.target_block_payload),
            selection_text=context.selection_text or "无",
        )
        blocks = await self._complete_json(prompt)
        if not blocks:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="LLM rewrite response is empty",
            )
        return blocks[0]

    async def generate_append(self, context: AppendContext):
        prompt = _render_prompt_template(
            APPEND_PROMPT_PATH,
            subject=context.subject,
            grade=context.grade,
            topic=context.topic,
            requirements=context.requirements or "无",
            section_title=context.section_title,
            instruction=context.instruction,
        )
        return await self._complete_json(prompt)


def get_provider():
    settings = get_settings()
    if settings.llm_provider == "deepseek":
        return DeepSeekProvider()
    return FakeProvider()
