"""LLM 输出内容安全过滤服务。

对 AI 生成的教学内容进行关键词过滤，防止不当内容进入课堂。
支持 warn（仅告警）和 block（阻止保存）两种模式。
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.core.config import get_settings

logger = logging.getLogger(__name__)

FILTER_DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@dataclass(slots=True)
class FilterResult:
    passed: bool
    blocked_terms: list[str] = field(default_factory=list)
    message: str = ""


def _load_blocklist() -> list[str]:
    """加载关键词黑名单。"""
    path = FILTER_DATA_DIR / "content_filter_keywords.json"
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data.get("blocked_terms", [])
    except Exception:
        logger.warning("Failed to load content filter keywords", exc_info=True)
        return []


def _check_text(text: str, blocked_terms: list[str]) -> FilterResult:
    """检查文本是否包含禁止词。"""
    if not blocked_terms or not text:
        return FilterResult(passed=True)

    matched: list[str] = []
    lower_text = text.lower()
    for term in blocked_terms:
        if term.lower() in lower_text:
            matched.append(term)

    if matched:
        return FilterResult(
            passed=False,
            blocked_terms=matched,
            message=f"内容包含 {len(matched)} 个敏感词",
        )
    return FilterResult(passed=True)


def _serialize_value(value: Any) -> str:
    """将 section 值序列化为可检查的文本。"""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, list):
        parts = []
        for item in value:
            parts.append(_serialize_value(item))
        return " ".join(parts)
    return str(value)


def check_section_content(section_name: str, content: Any) -> FilterResult:
    """检查单个 section 的内容是否合规。"""
    settings = get_settings()
    if not settings.content_filter_enabled:
        return FilterResult(passed=True)

    blocked_terms = _load_blocklist()
    if not blocked_terms:
        return FilterResult(passed=True)

    text = _serialize_value(content)
    result = _check_text(text, blocked_terms)

    if not result.passed:
        logger.warning(
            "Content filter hit: section=%s terms=%s",
            section_name,
            result.blocked_terms,
        )

    return result


def sanitize_section_content(content: Any, blocked_terms: list[str]) -> Any:
    """移除内容中的敏感词（返回新对象，不修改原对象）。"""
    if isinstance(content, str):
        result = content
        for term in blocked_terms:
            # Case-insensitive replacement
            pattern = re.compile(re.escape(term), re.IGNORECASE)
            result = pattern.sub("[内容已移除]", result)
        return result
    if isinstance(content, dict):
        return {k: sanitize_section_content(v, blocked_terms) for k, v in content.items()}
    if isinstance(content, list):
        return [sanitize_section_content(item, blocked_terms) for item in content]
    return content
