"""LLM Provider 架构 + 真正 token-by-token 流式输出。

支持 DeepSeek / MiniMax / Fake 三种 Provider。
所有 Provider 统一返回 AsyncIterator[str]，每个 yield 是一个 JSON delta。
"""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator
from dataclasses import dataclass
from pathlib import Path

import httpx

from app.core.config import Settings, get_settings

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


# ---------------------------------------------------------------------------
# 上下文 dataclass
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class LessonPlanContext:
    """教案生成上下文。"""

    subject: str = ""
    grade: str = ""
    topic: str = ""
    requirements: str = ""
    scene: str = "public_school"
    class_hour: int = 1
    lesson_category: str = "new"
    prompt_hints: str = ""


@dataclass(slots=True)
class StudyGuideContext:
    """学案生成上下文。"""

    subject: str = ""
    grade: str = ""
    topic: str = ""
    requirements: str = ""
    scene: str = "public_school"
    class_hour: int = 1
    prompt_hints: str = ""


@dataclass(slots=True)
class RewriteSectionContext:
    """Section 级重写上下文。"""

    subject: str = ""
    grade: str = ""
    topic: str = ""
    section_name: str = ""
    current_content: str = ""
    action: str = "rewrite"
    instruction: str = ""


# ---------------------------------------------------------------------------
# Prompt 模板渲染
# ---------------------------------------------------------------------------


def _load_prompt(name: str) -> str:
    path = PROMPTS_DIR / name
    return path.read_text(encoding="utf-8")


def _render(template: str, **kwargs: str) -> str:
    """简单的 {key} 占位替换。"""
    result = template
    for key, value in kwargs.items():
        result = result.replace("{" + key + "}", value)
    return result


# ---------------------------------------------------------------------------
# JSON delta 解析
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Provider Protocol
# ---------------------------------------------------------------------------


class LLMProvider:
    """所有 Provider 的基类。子类必须实现 generate / rewrite。"""

    async def generate_lesson_plan(
        self, ctx: LessonPlanContext
    ) -> AsyncIterator[str]:
        """流式生成教案 JSON。每次 yield 一段文本 delta。"""
        raise NotImplementedError
        # make this an async generator for type-checking
        yield ""  # type: ignore[unreachable]  # noqa: E501

    async def generate_study_guide(
        self, ctx: StudyGuideContext
    ) -> AsyncIterator[str]:
        """流式生成学案 JSON。每次 yield 一段文本 delta。"""
        raise NotImplementedError
        yield ""  # type: ignore[unreachable]

    async def rewrite_section(
        self, ctx: RewriteSectionContext
    ) -> AsyncIterator[str]:
        """流式重写某个 section。每次 yield 一段文本 delta。"""
        raise NotImplementedError
        yield ""  # type: ignore[unreachable]


# ---------------------------------------------------------------------------
# FakeProvider（开发测试用）
# ---------------------------------------------------------------------------


class FakeProvider(LLMProvider):
    """模拟逐 token 输出，返回预定义的教案/学案 JSON。"""

    async def generate_lesson_plan(
        self, ctx: LessonPlanContext
    ) -> AsyncIterator[str]:
        fake_json = json.dumps(
            {
                "doc_type": "lesson_plan",
                "header": {
                    "title": ctx.topic,
                    "subject": ctx.subject,
                    "grade": ctx.grade,
                    "classHour": ctx.class_hour,
                    "lessonCategory": ctx.lesson_category,
                    "teacher": "",
                },
                "objectives": [
                    {"dimension": "knowledge", "content": f"掌握{ctx.topic}的基本概念和核心知识点"},
                    {"dimension": "ability", "content": f"能够运用{ctx.topic}相关知识分析和解决问题"},
                    {"dimension": "emotion", "content": f"在学习{ctx.topic}过程中培养学科兴趣和探究精神"},
                ],
                "objectives_status": "pending",
                "key_points": {
                    "keyPoints": [f"{ctx.topic}的核心概念与原理", f"{ctx.topic}的重点分析方法"],
                    "difficulties": [f"{ctx.topic}中容易混淆的概念辨析", f"如何引导学生理解{ctx.topic}的深层含义"],
                },
                "key_points_status": "pending",
                "preparation": ["多媒体课件", "课文朗读音频", "学生学习任务单"],
                "preparation_status": "pending",
                "teaching_process": [
                    {
                        "phase": "导入新课",
                        "duration": 5,
                        "teacher_activity": f"通过提问或情境创设引入{ctx.topic}，激发学生兴趣",
                        "student_activity": "积极思考，回答教师提问，进入学习状态",
                        "design_intent": "创设情境，激活学生已有知识经验，为新课学习做铺垫",
                    },
                    {
                        "phase": "新授知识",
                        "duration": 20,
                        "teacher_activity": f"系统讲解{ctx.topic}的核心内容，引导学生探究",
                        "student_activity": "认真听讲，做好笔记，积极参与讨论",
                        "design_intent": "通过讲解和互动，帮助学生理解和掌握核心知识",
                    },
                    {
                        "phase": "巩固练习",
                        "duration": 10,
                        "teacher_activity": f"设计分层练习，巩固{ctx.topic}的学习效果",
                        "student_activity": "独立完成练习，小组交流讨论",
                        "design_intent": "通过练习检测学习效果，巩固所学知识",
                    },
                    {
                        "phase": "课堂小结",
                        "duration": 5,
                        "teacher_activity": f"总结{ctx.topic}的重点知识，布置课后作业",
                        "student_activity": "梳理本课所学，记录作业要求",
                        "design_intent": "帮助学生构建知识体系，为后续学习做准备",
                    },
                ],
                "teaching_process_status": "pending",
                "board_design": f"{ctx.topic}\n├── 核心概念\n├── 重点分析\n└── 方法总结",
                "board_design_status": "pending",
                "reflection": "",
                "reflection_status": "pending",
            },
            ensure_ascii=False,
            indent=2,
        )
        # 模拟逐 token 输出
        chunk_size = 20
        for i in range(0, len(fake_json), chunk_size):
            yield fake_json[i : i + chunk_size]
            await asyncio.sleep(0.02)

    async def generate_study_guide(
        self, ctx: StudyGuideContext
    ) -> AsyncIterator[str]:
        fake_json = json.dumps(
            {
                "doc_type": "study_guide",
                "header": {
                    "title": ctx.topic,
                    "subject": ctx.subject,
                    "grade": ctx.grade,
                    "className": "",
                    "studentName": "",
                    "date": "",
                },
                "learning_objectives": [
                    f"我能理解{ctx.topic}的基本概念",
                    f"我能运用{ctx.topic}的方法进行分析",
                    "我能独立完成相关练习题",
                ],
                "learning_objectives_status": "pending",
                "key_difficulties": [
                    f"{ctx.topic}的核心概念理解",
                    f"{ctx.topic}的方法应用",
                ],
                "key_difficulties_status": "pending",
                "prior_knowledge": ["已学过的基础知识回顾"],
                "prior_knowledge_status": "pending",
                "learning_process": {
                    "selfStudy": [
                        {
                            "level": "A",
                            "itemType": "short_answer",
                            "prompt": f"阅读课文，用自己的话概括{ctx.topic}的主要内容",
                            "options": [],
                            "answer": "",
                            "analysis": "",
                        },
                        {
                            "level": "B",
                            "itemType": "fill_blank",
                            "prompt": f"{ctx.topic}的核心定义是______",
                            "options": [],
                            "answer": "",
                            "analysis": "",
                        },
                    ],
                    "collaboration": [
                        {
                            "level": "B",
                            "itemType": "short_answer",
                            "prompt": f"小组讨论：{ctx.topic}对你有什么启发？",
                            "options": [],
                            "answer": "",
                            "analysis": "",
                        },
                    ],
                    "presentation": [
                        {
                            "level": "C",
                            "itemType": "short_answer",
                            "prompt": f"结合{ctx.topic}，谈谈你的理解和感悟",
                            "options": [],
                            "answer": "",
                            "analysis": "",
                        },
                    ],
                },
                "self_study_status": "pending",
                "collaboration_status": "pending",
                "presentation_status": "pending",
                "assessment": [
                    {
                        "level": "A",
                        "itemType": "choice",
                        "prompt": f"以下关于{ctx.topic}的说法正确的是",
                        "options": ["A. 说法一", "B. 说法二", "C. 说法三", "D. 说法四"],
                        "answer": "A",
                        "analysis": "解析内容",
                    },
                ],
                "assessment_status": "pending",
                "extension": [
                    {
                        "level": "D",
                        "itemType": "short_answer",
                        "prompt": f"课外拓展：深入了解{ctx.topic}的更多内容",
                        "options": [],
                        "answer": "",
                        "analysis": "",
                    },
                ],
                "extension_status": "pending",
                "self_reflection": "",
                "self_reflection_status": "pending",
            },
            ensure_ascii=False,
            indent=2,
        )
        chunk_size = 20
        for i in range(0, len(fake_json), chunk_size):
            yield fake_json[i : i + chunk_size]
            await asyncio.sleep(0.02)

    async def rewrite_section(
        self, ctx: RewriteSectionContext
    ) -> AsyncIterator[str]:
        rewritten = f"（已{ctx.action}）{ctx.current_content[:100]}..."
        chunk_size = 15
        for i in range(0, len(rewritten), chunk_size):
            yield rewritten[i : i + chunk_size]
            await asyncio.sleep(0.02)


# ---------------------------------------------------------------------------
# DeepSeek / MiniMax 共用流式逻辑
# ---------------------------------------------------------------------------


async def _stream_chat_completion(
    *,
    base_url: str,
    api_key: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
) -> AsyncIterator[str]:
    """通用的 chat completion 流式调用。"""
    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": True,
        "temperature": 0.6,
        "max_tokens": 8192,
    }

    async with httpx.AsyncClient(timeout=httpx.Timeout(120.0)) as client:
        async with client.stream("POST", url, json=payload, headers=headers) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                line = line.strip()
                if not line or not line.startswith("data: "):
                    continue
                data = line[6:]  # strip "data: "
                if data == "[DONE]":
                    break
                try:
                    chunk = json.loads(data)
                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                    content = delta.get("content", "")
                    if content:
                        yield content
                except json.JSONDecodeError:
                    continue


# ---------------------------------------------------------------------------
# DeepSeekProvider
# ---------------------------------------------------------------------------


class DeepSeekProvider(LLMProvider):
    def __init__(self, settings: Settings | None = None) -> None:
        s = settings or get_settings()
        self._base_url = s.deepseek_base_url
        self._api_key = s.deepseek_api_key
        self._model = s.deepseek_model

    async def generate_lesson_plan(
        self, ctx: LessonPlanContext
    ) -> AsyncIterator[str]:
        template = _load_prompt("lesson_plan_generation_prompt.md")
        user_prompt = _render(
            template,
            subject=ctx.subject,
            grade=ctx.grade,
            topic=ctx.topic,
            requirements=ctx.requirements or "无特殊要求",
            scene=ctx.scene,
            class_hour=str(ctx.class_hour),
            lesson_category=ctx.lesson_category,
            prompt_hints=ctx.prompt_hints or "",
        )
        async for chunk in _stream_chat_completion(
            base_url=self._base_url,
            api_key=self._api_key,
            model=self._model,
            system_prompt="你是 LessonPilot 的教案生成引擎。请严格按照要求输出结构化 JSON，不要输出其他内容。",
            user_prompt=user_prompt,
        ):
            yield chunk

    async def generate_study_guide(
        self, ctx: StudyGuideContext
    ) -> AsyncIterator[str]:
        template = _load_prompt("study_guide_generation_prompt.md")
        user_prompt = _render(
            template,
            subject=ctx.subject,
            grade=ctx.grade,
            topic=ctx.topic,
            requirements=ctx.requirements or "无特殊要求",
            scene=ctx.scene,
            class_hour=str(ctx.class_hour),
            prompt_hints=ctx.prompt_hints or "",
        )
        async for chunk in _stream_chat_completion(
            base_url=self._base_url,
            api_key=self._api_key,
            model=self._model,
            system_prompt="你是 LessonPilot 的学案生成引擎。请严格按照要求输出结构化 JSON，不要输出其他内容。",
            user_prompt=user_prompt,
        ):
            yield chunk

    async def rewrite_section(
        self, ctx: RewriteSectionContext
    ) -> AsyncIterator[str]:
        template = _load_prompt("section_rewrite_prompt.md")
        user_prompt = _render(
            template,
            subject=ctx.subject,
            grade=ctx.grade,
            topic=ctx.topic,
            section_name=ctx.section_name,
            current_content=ctx.current_content,
            action=ctx.action,
            instruction=ctx.instruction or "无额外指示",
        )
        async for chunk in _stream_chat_completion(
            base_url=self._base_url,
            api_key=self._api_key,
            model=self._model,
            system_prompt="你是 LessonPilot 的教案/学案内容重写引擎。请输出重写后的 JSON 片段，不要输出其他内容。",
            user_prompt=user_prompt,
        ):
            yield chunk


# ---------------------------------------------------------------------------
# MiniMaxProvider
# ---------------------------------------------------------------------------


class MiniMaxProvider(LLMProvider):
    def __init__(self, settings: Settings | None = None) -> None:
        s = settings or get_settings()
        self._base_url = s.minimax_base_url
        self._api_key = s.minimax_api_key
        self._model = s.minimax_model

    async def generate_lesson_plan(
        self, ctx: LessonPlanContext
    ) -> AsyncIterator[str]:
        template = _load_prompt("lesson_plan_generation_prompt.md")
        user_prompt = _render(
            template,
            subject=ctx.subject,
            grade=ctx.grade,
            topic=ctx.topic,
            requirements=ctx.requirements or "无特殊要求",
            scene=ctx.scene,
            class_hour=str(ctx.class_hour),
            lesson_category=ctx.lesson_category,
            prompt_hints=ctx.prompt_hints or "",
        )
        async for chunk in _stream_chat_completion(
            base_url=self._base_url,
            api_key=self._api_key,
            model=self._model,
            system_prompt="你是 LessonPilot 的教案生成引擎。请严格按照要求输出结构化 JSON，不要输出其他内容。",
            user_prompt=user_prompt,
        ):
            yield chunk

    async def generate_study_guide(
        self, ctx: StudyGuideContext
    ) -> AsyncIterator[str]:
        template = _load_prompt("study_guide_generation_prompt.md")
        user_prompt = _render(
            template,
            subject=ctx.subject,
            grade=ctx.grade,
            topic=ctx.topic,
            requirements=ctx.requirements or "无特殊要求",
            scene=ctx.scene,
            class_hour=str(ctx.class_hour),
            prompt_hints=ctx.prompt_hints or "",
        )
        async for chunk in _stream_chat_completion(
            base_url=self._base_url,
            api_key=self._api_key,
            model=self._model,
            system_prompt="你是 LessonPilot 的学案生成引擎。请严格按照要求输出结构化 JSON，不要输出其他内容。",
            user_prompt=user_prompt,
        ):
            yield chunk

    async def rewrite_section(
        self, ctx: RewriteSectionContext
    ) -> AsyncIterator[str]:
        template = _load_prompt("section_rewrite_prompt.md")
        user_prompt = _render(
            template,
            subject=ctx.subject,
            grade=ctx.grade,
            topic=ctx.topic,
            section_name=ctx.section_name,
            current_content=ctx.current_content,
            action=ctx.action,
            instruction=ctx.instruction or "无额外指示",
        )
        async for chunk in _stream_chat_completion(
            base_url=self._base_url,
            api_key=self._api_key,
            model=self._model,
            system_prompt="你是 LessonPilot 的教案/学案内容重写引擎。请输出重写后的 JSON 片段，不要输出其他内容。",
            user_prompt=user_prompt,
        ):
            yield chunk


# ---------------------------------------------------------------------------
# 工厂函数
# ---------------------------------------------------------------------------


def get_provider() -> LLMProvider:
    """根据配置返回对应的 LLM Provider 实例。"""
    settings = get_settings()
    if settings.llm_provider == "deepseek":
        return DeepSeekProvider(settings)
    if settings.llm_provider == "minimax":
        return MiniMaxProvider(settings)
    return FakeProvider()
