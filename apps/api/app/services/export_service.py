from __future__ import annotations

import re
from html import unescape
from io import BytesIO

from docx import Document as DocxDocument

from app.models import Task
from app.schemas.content import ContentDocument, ListBlock, ParagraphBlock, SectionBlock, TeachingStepBlock

HTML_TAG_PATTERN = re.compile(r"<[^>]+>")


def _to_plain_text(value: str) -> str:
    return unescape(HTML_TAG_PATTERN.sub("", value)).strip()


def _render_block(document: DocxDocument, block, level: int = 1) -> None:
    if block.status != "confirmed":
        return

    if isinstance(block, SectionBlock):
        document.add_heading(block.title, level=min(level, 4))
        for child in block.children:
            _render_block(document, child, level + 1)
        return

    if isinstance(block, TeachingStepBlock):
        duration = f"（{block.duration_minutes}分钟）" if block.duration_minutes else ""
        document.add_heading(f"{block.title}{duration}", level=min(level, 4))
        for child in block.children:
            _render_block(document, child, level + 1)
        return

    if isinstance(block, ParagraphBlock):
        text = _to_plain_text(block.content)
        if text:
            document.add_paragraph(text)
        return

    if isinstance(block, ListBlock):
        for item in block.items:
            text = _to_plain_text(item)
            if text:
                document.add_paragraph(text, style="List Bullet")


def build_docx(task: Task, content: ContentDocument) -> bytes:
    document = DocxDocument()
    document.add_heading(task.title, level=0)
    document.add_paragraph(f"{task.subject} · {task.grade} · {task.topic}")
    for block in content.blocks:
        _render_block(document, block)
    buffer = BytesIO()
    document.save(buffer)
    return buffer.getvalue()
