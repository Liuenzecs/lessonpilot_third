from __future__ import annotations

import re
from html import escape, unescape
from io import BytesIO

from docx import Document as DocxDocument
from docx.shared import Pt

from app.models import Task
from app.schemas.content import (
    ChoiceQuestionBlock,
    ContentDocument,
    ExerciseGroupBlock,
    FillBlankQuestionBlock,
    ListBlock,
    ParagraphBlock,
    SectionBlock,
    ShortAnswerQuestionBlock,
    TeachingStepBlock,
)

HTML_TAG_PATTERN = re.compile(r"<[^>]+>")


def _indent_points(level: int) -> Pt:
    return Pt(max(level, 0) * 18)


def _indent_px(level: int) -> int:
    return max(level, 0) * 24


def _to_plain_text(value: str) -> str:
    return unescape(HTML_TAG_PATTERN.sub("", value)).strip()


def _render_docx_question(document: DocxDocument, label: str, prompt: str, answer: str, analysis: str) -> None:
    prompt_text = _to_plain_text(prompt)
    if prompt_text:
        document.add_paragraph(f"{label} {prompt_text}")
    if answer:
        document.add_paragraph(f"参考答案：{_to_plain_text(answer)}")
    if analysis:
        document.add_paragraph(f"解析：{_to_plain_text(analysis)}")


def _render_docx_block(document: DocxDocument, block, level: int = 1) -> None:
    if block.status != "confirmed":
        return

    if isinstance(block, SectionBlock):
        document.add_heading(block.title, level=min(level, 4))
        for child in block.children:
            _render_docx_block(document, child, level + 1)
        return

    if isinstance(block, TeachingStepBlock):
        duration = f"（{block.duration_minutes}分钟）" if block.duration_minutes else ""
        document.add_heading(f"{block.title}{duration}", level=min(level, 4))
        for child in block.children:
            _render_docx_block(document, child, level + 1)
        return

    if isinstance(block, ExerciseGroupBlock):
        document.add_heading(block.title, level=min(level, 4))
        for child in block.children:
            _render_docx_block(document, child, level + 1)
        return

    if isinstance(block, ParagraphBlock):
        text = _to_plain_text(block.content)
        if text:
            paragraph = document.add_paragraph(text)
            paragraph.paragraph_format.left_indent = _indent_points(block.indent)
        return

    if isinstance(block, ListBlock):
        for item in block.items:
            text = _to_plain_text(item)
            if text:
                paragraph = document.add_paragraph(text, style="List Bullet")
                paragraph.paragraph_format.left_indent = _indent_points(block.indent)
        return

    if isinstance(block, ChoiceQuestionBlock):
        _render_docx_question(
            document,
            "选择题：",
            block.prompt,
            "；".join(block.answers),
            block.analysis,
        )
        for option in block.options:
            option_text = _to_plain_text(option)
            if option_text:
                document.add_paragraph(option_text, style="List Bullet")
        return

    if isinstance(block, FillBlankQuestionBlock):
        _render_docx_question(
            document,
            "填空题：",
            block.prompt,
            "；".join(block.answers),
            block.analysis,
        )
        return

    if isinstance(block, ShortAnswerQuestionBlock):
        _render_docx_question(
            document,
            "简答题：",
            block.prompt,
            block.reference_answer,
            block.analysis,
        )


def build_docx(task: Task, content: ContentDocument) -> bytes:
    document = DocxDocument()
    document.add_heading(task.title, level=0)
    document.add_paragraph(f"{task.subject} | {task.grade} | {task.topic}")
    for block in content.blocks:
        _render_docx_block(document, block)
    buffer = BytesIO()
    document.save(buffer)
    return buffer.getvalue()


def _build_html_question(label: str, prompt: str, answer: str, analysis: str) -> str:
    parts = [f"<p><strong>{escape(label)}</strong> {prompt}</p>"]
    if answer:
        parts.append(f"<p><strong>参考答案：</strong>{escape(answer)}</p>")
    if analysis:
        parts.append(f"<p><strong>解析：</strong>{analysis}</p>")
    return "".join(parts)


def _build_html_block(block, level: int = 1) -> str:
    if block.status != "confirmed":
        return ""

    if isinstance(block, SectionBlock):
        tag = f"h{min(level + 1, 4)}"
        return f"<{tag}>{escape(block.title)}</{tag}>" + "".join(
            _build_html_block(child, level + 1) for child in block.children
        )

    if isinstance(block, TeachingStepBlock):
        duration = f"（{block.duration_minutes}分钟）" if block.duration_minutes else ""
        tag = f"h{min(level + 1, 5)}"
        return f"<{tag}>{escape(block.title + duration)}</{tag}>" + "".join(
            _build_html_block(child, level + 1) for child in block.children
        )

    if isinstance(block, ExerciseGroupBlock):
        tag = f"h{min(level + 1, 5)}"
        return f"<{tag}>{escape(block.title)}</{tag}>" + "".join(
            _build_html_block(child, level + 1) for child in block.children
        )

    if isinstance(block, ParagraphBlock):
        margin_left = _indent_px(block.indent)
        return f'<div style="margin-left: {margin_left}px">{block.content}</div>'

    if isinstance(block, ListBlock):
        items = "".join(f"<li>{item}</li>" for item in block.items if _to_plain_text(item))
        if not items:
            return ""
        margin_left = _indent_px(block.indent)
        return f'<ul style="margin-left: {margin_left}px">{items}</ul>'

    if isinstance(block, ChoiceQuestionBlock):
        options = "".join(f"<li>{escape(_to_plain_text(option))}</li>" for option in block.options if option)
        return _build_html_question("选择题：", block.prompt, "；".join(block.answers), block.analysis) + (
            f"<ul>{options}</ul>" if options else ""
        )

    if isinstance(block, FillBlankQuestionBlock):
        return _build_html_question("填空题：", block.prompt, "；".join(block.answers), block.analysis)

    return _build_html_question("简答题：", block.prompt, block.reference_answer, block.analysis)


def _build_export_html(task: Task, content: ContentDocument) -> str:
    body = "".join(_build_html_block(block) for block in content.blocks)
    return f"""
    <!doctype html>
    <html lang="zh-CN">
      <head>
        <meta charset="utf-8" />
        <style>
          body {{
            font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
            color: #1f2f45;
            padding: 32px;
            line-height: 1.7;
          }}
          h1, h2, h3, h4, h5 {{
            color: #15355a;
            margin: 18px 0 10px;
          }}
          p, li {{
            font-size: 13px;
            margin: 6px 0;
          }}
          ul {{
            padding-left: 20px;
          }}
        </style>
      </head>
      <body>
        <h1>{escape(task.title)}</h1>
        <p>{escape(task.subject)} | {escape(task.grade)} | {escape(task.topic)}</p>
        {body}
      </body>
    </html>
    """


def _escape_pdf_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _build_simple_pdf(task: Task, content: ContentDocument) -> bytes:
    text_blocks = [_to_plain_text(task.title), f"{task.subject} | {task.grade} | {task.topic}"]

    def collect(block) -> None:
        if block.status != "confirmed":
            return
        if isinstance(block, SectionBlock):
            text_blocks.append(block.title)
            for child in block.children:
                collect(child)
            return
        if isinstance(block, TeachingStepBlock):
            duration = f"（{block.duration_minutes}分钟）" if block.duration_minutes else ""
            text_blocks.append(f"{block.title}{duration}")
            for child in block.children:
                collect(child)
            return
        if isinstance(block, ExerciseGroupBlock):
            text_blocks.append(block.title)
            for child in block.children:
                collect(child)
            return
        if isinstance(block, ParagraphBlock):
            value = _to_plain_text(block.content)
            if value:
                text_blocks.append(f"{'  ' * max(block.indent, 0)}{value}")
            return
        if isinstance(block, ListBlock):
            for item in block.items:
                value = _to_plain_text(item)
                if value:
                    text_blocks.append(f"{'  ' * max(block.indent, 0)}- {value}")
            return
        if isinstance(block, ChoiceQuestionBlock):
            text_blocks.append(f"选择题：{_to_plain_text(block.prompt)}")
            for option in block.options:
                option_text = _to_plain_text(option)
                if option_text:
                    text_blocks.append(f"  * {option_text}")
            if block.answers:
                text_blocks.append(f"参考答案：{'；'.join(block.answers)}")
            if _to_plain_text(block.analysis):
                text_blocks.append(f"解析：{_to_plain_text(block.analysis)}")
            return
        if isinstance(block, FillBlankQuestionBlock):
            text_blocks.append(f"填空题：{_to_plain_text(block.prompt)}")
            if block.answers:
                text_blocks.append(f"参考答案：{'；'.join(block.answers)}")
            if _to_plain_text(block.analysis):
                text_blocks.append(f"解析：{_to_plain_text(block.analysis)}")
            return
        text_blocks.append(f"简答题：{_to_plain_text(block.prompt)}")
        if _to_plain_text(block.reference_answer):
            text_blocks.append(f"参考答案：{_to_plain_text(block.reference_answer)}")
        if _to_plain_text(block.analysis):
            text_blocks.append(f"解析：{_to_plain_text(block.analysis)}")

    for block in content.blocks:
        collect(block)

    lines = ["BT", "/F1 12 Tf", "50 790 Td"]
    first_line = True
    for text in text_blocks:
        if not text:
            continue
        if not first_line:
            lines.append("0 -16 Td")
        lines.append(f"({_escape_pdf_text(text)}) Tj")
        first_line = False
    lines.append("ET")
    content_stream = "\n".join(lines).encode("latin-1", errors="replace")

    objects = [
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj",
        b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj",
        (
            b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
            b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj"
        ),
        f"4 0 obj << /Length {len(content_stream)} >> stream\n".encode("latin-1")
        + content_stream
        + b"\nendstream endobj",
        b"5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj",
    ]

    buffer = BytesIO()
    buffer.write(b"%PDF-1.4\n")
    offsets: list[int] = []
    for obj in objects:
        offsets.append(buffer.tell())
        buffer.write(obj)
        buffer.write(b"\n")

    xref_offset = buffer.tell()
    buffer.write(f"xref\n0 {len(objects) + 1}\n".encode("latin-1"))
    buffer.write(b"0000000000 65535 f \n")
    for offset in offsets:
        buffer.write(f"{offset:010d} 00000 n \n".encode("latin-1"))
    buffer.write(
        (
            f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF"
        ).encode("latin-1")
    )
    return buffer.getvalue()


def build_pdf(task: Task, content: ContentDocument) -> bytes:
    html = _build_export_html(task, content)
    try:
        from weasyprint import HTML

        return HTML(string=html).write_pdf()
    except Exception:
        return _build_simple_pdf(task, content)
