from __future__ import annotations

import asyncio
import json

from app.schemas.content import LessonPlanContent, StudyGuideContent
from app.services.llm_service import (
    FakeProvider,
    LessonPlanContext,
    StudyGuideContext,
    _load_prompt,
    _render,
    get_provider,
)


def test_get_provider_returns_fake_by_default(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "fake")
    from app.core.config import get_settings
    get_settings.cache_clear()
    provider = get_provider()
    assert isinstance(provider, FakeProvider)
    get_settings.cache_clear()


def test_render_replaces_placeholders():
    template = "学科：{subject}，年级：{grade}，课题：{topic}"
    result = _render(template, subject="语文", grade="七年级", topic="春")
    assert result == "学科：语文，年级：七年级，课题：春"


def test_load_prompt_exists():
    for name in [
        "lesson_plan_generation_prompt.md",
        "study_guide_generation_prompt.md",
        "section_rewrite_prompt.md",
    ]:
        content = _load_prompt(name)
        assert len(content) > 50


def test_fake_provider_generates_valid_lesson_plan_json():
    async def _run():
        provider = FakeProvider()
        ctx = LessonPlanContext(
            subject="语文",
            grade="七年级",
            topic="春",
        )
        chunks: list[str] = []
        async for chunk in provider.generate_lesson_plan(ctx):
            chunks.append(chunk)
        raw = "".join(chunks)
        data = json.loads(raw)
        content = LessonPlanContent.model_validate(data)
        assert content.header.title == "春"
        assert len(content.objectives) > 0
        assert len(content.teaching_process) > 0

    asyncio.run(_run())


def test_fake_provider_generates_valid_study_guide_json():
    async def _run():
        provider = FakeProvider()
        ctx = StudyGuideContext(
            subject="语文",
            grade="七年级",
            topic="春",
        )
        chunks: list[str] = []
        async for chunk in provider.generate_study_guide(ctx):
            chunks.append(chunk)
        raw = "".join(chunks)
        data = json.loads(raw)
        content = StudyGuideContent.model_validate(data)
        assert content.header.title == "春"
        assert len(content.learning_objectives) > 0

    asyncio.run(_run())
