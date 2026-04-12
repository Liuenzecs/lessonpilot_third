from __future__ import annotations

import re
from html import escape, unescape
from io import BytesIO

from docx import Document as DocxDocument
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

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


def _set_style_font(style, font_name: str, size: int, *, bold: bool = False, color: str | None = None) -> None:
    style.font.name = font_name
    style.font.size = Pt(size)
    style.font.bold = bold
    if color:
        style.font.color.rgb = RGBColor.from_string(color)

    r_pr = style._element.get_or_add_rPr()
    r_fonts = r_pr.rFonts
    if r_fonts is None:
        r_fonts = OxmlElement("w:rFonts")
        r_pr.append(r_fonts)
    r_fonts.set(qn("w:ascii"), font_name)
    r_fonts.set(qn("w:hAnsi"), font_name)
    r_fonts.set(qn("w:eastAsia"), font_name)


def _ensure_paragraph_style(document: DocxDocument, name: str):
    if name in document.styles:
        return document.styles[name]
    return document.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)


def _configure_docx_styles(document: DocxDocument) -> None:
    section = document.sections[0]
    section.page_width = Cm(21)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2.2)
    section.bottom_margin = Cm(2.2)
    section.left_margin = Cm(2.4)
    section.right_margin = Cm(2.4)

    normal_style = document.styles["Normal"]
    _set_style_font(normal_style, "宋体", 11)
    normal_style.paragraph_format.line_spacing = 1.55
    normal_style.paragraph_format.space_after = Pt(6)

    title_style = _ensure_paragraph_style(document, "LessonPilot Title")
    _set_style_font(title_style, "Microsoft YaHei", 22, bold=True, color="243349")
    title_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_style.paragraph_format.space_after = Pt(10)
    title_style.paragraph_format.keep_with_next = True

    meta_style = _ensure_paragraph_style(document, "LessonPilot Meta")
    _set_style_font(meta_style, "Microsoft YaHei", 10, color="6C7A90")
    meta_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    meta_style.paragraph_format.space_after = Pt(18)
    meta_style.paragraph_format.keep_with_next = True

    section_style = _ensure_paragraph_style(document, "LessonPilot Section")
    _set_style_font(section_style, "Microsoft YaHei", 16, bold=True, color="16385B")
    section_style.paragraph_format.space_before = Pt(18)
    section_style.paragraph_format.space_after = Pt(8)
    section_style.paragraph_format.keep_with_next = True

    subsection_style = _ensure_paragraph_style(document, "LessonPilot Subheading")
    _set_style_font(subsection_style, "Microsoft YaHei", 13, bold=True, color="2D4B71")
    subsection_style.paragraph_format.space_before = Pt(14)
    subsection_style.paragraph_format.space_after = Pt(6)
    subsection_style.paragraph_format.keep_with_next = True

    body_style = _ensure_paragraph_style(document, "LessonPilot Body")
    _set_style_font(body_style, "宋体", 11, color="243349")
    body_style.paragraph_format.line_spacing = 1.62
    body_style.paragraph_format.space_after = Pt(8)

    list_style = _ensure_paragraph_style(document, "LessonPilot List")
    _set_style_font(list_style, "宋体", 11, color="243349")
    list_style.paragraph_format.line_spacing = 1.55
    list_style.paragraph_format.space_after = Pt(4)

    question_style = _ensure_paragraph_style(document, "LessonPilot Question")
    _set_style_font(question_style, "Microsoft YaHei", 11, bold=True, color="243349")
    question_style.paragraph_format.line_spacing = 1.45
    question_style.paragraph_format.space_before = Pt(8)
    question_style.paragraph_format.space_after = Pt(5)
    question_style.paragraph_format.keep_with_next = True

    option_style = _ensure_paragraph_style(document, "LessonPilot Option")
    _set_style_font(option_style, "宋体", 11, color="243349")
    option_style.paragraph_format.left_indent = Pt(18)
    option_style.paragraph_format.space_after = Pt(2)

    answer_style = _ensure_paragraph_style(document, "LessonPilot Answer")
    _set_style_font(answer_style, "宋体", 10, color="2E7B66")
    answer_style.paragraph_format.left_indent = Pt(18)
    answer_style.paragraph_format.space_after = Pt(2)

    analysis_style = _ensure_paragraph_style(document, "LessonPilot Analysis")
    _set_style_font(analysis_style, "宋体", 10, color="6C7A90")
    analysis_style.paragraph_format.left_indent = Pt(18)
    analysis_style.paragraph_format.space_after = Pt(8)


def _add_docx_paragraph(
    document: DocxDocument,
    text: str,
    style_name: str,
    *,
    left_indent: Pt | None = None,
) -> None:
    paragraph = document.add_paragraph(style=style_name)
    paragraph.add_run(text)
    if left_indent is not None:
        paragraph.paragraph_format.left_indent = left_indent


def _render_docx_question(
    document: DocxDocument,
    label: str,
    prompt: str,
    answer: str,
    analysis: str,
    *,
    index: int | None = None,
    options: list[str] | None = None,
) -> None:
    prompt_text = _to_plain_text(prompt)
    if prompt_text:
        prefix = f"{index}. " if index is not None else ""
        _add_docx_paragraph(
            document,
            f"{prefix}{label}{prompt_text}",
            "LessonPilot Question",
        )

    for option_index, option in enumerate(options or []):
        option_text = _to_plain_text(option)
        if not option_text:
            continue
        option_prefix = chr(65 + option_index) if option_index < 26 else str(option_index + 1)
        _add_docx_paragraph(
            document,
            f"{option_prefix}. {option_text}",
            "LessonPilot Option",
        )

    if answer:
        _add_docx_paragraph(
            document,
            f"参考答案：{_to_plain_text(answer)}",
            "LessonPilot Answer",
        )
    if analysis:
        _add_docx_paragraph(
            document,
            f"解析：{_to_plain_text(analysis)}",
            "LessonPilot Analysis",
        )


def _render_docx_block(document: DocxDocument, block, level: int = 1) -> None:
    if block.status != "confirmed":
        return

    if isinstance(block, SectionBlock):
        _add_docx_paragraph(document, block.title, "LessonPilot Section")
        for child in block.children:
            _render_docx_block(document, child, level + 1)
        return

    if isinstance(block, TeachingStepBlock):
        duration = f"（{block.duration_minutes}分钟）" if block.duration_minutes else ""
        _add_docx_paragraph(document, f"{block.title}{duration}", "LessonPilot Subheading")
        for child in block.children:
            _render_docx_block(document, child, level + 1)
        return

    if isinstance(block, ExerciseGroupBlock):
        _add_docx_paragraph(document, block.title, "LessonPilot Subheading")
        for index, child in enumerate(block.children, start=1):
            if isinstance(child, ChoiceQuestionBlock):
                _render_docx_question(
                    document,
                    "选择题：",
                    child.prompt,
                    "；".join(child.answers),
                    child.analysis,
                    index=index,
                    options=child.options,
                )
                continue
            if isinstance(child, FillBlankQuestionBlock):
                _render_docx_question(
                    document,
                    "填空题：",
                    child.prompt,
                    "；".join(child.answers),
                    child.analysis,
                    index=index,
                )
                continue
            _render_docx_question(
                document,
                "简答题：",
                child.prompt,
                child.reference_answer,
                child.analysis,
                index=index,
            )
        return

    if isinstance(block, ParagraphBlock):
        text = _to_plain_text(block.content)
        if text:
            _add_docx_paragraph(
                document,
                text,
                "LessonPilot Body",
                left_indent=_indent_points(block.indent),
            )
        return

    if isinstance(block, ListBlock):
        for item in block.items:
            text = _to_plain_text(item)
            if text:
                _add_docx_paragraph(
                    document,
                    f"• {text}",
                    "LessonPilot List",
                    left_indent=_indent_points(block.indent),
                )
        return

    if isinstance(block, ChoiceQuestionBlock):
        _render_docx_question(
            document,
            "选择题：",
            block.prompt,
            "；".join(block.answers),
            block.analysis,
            options=block.options,
        )
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
    _configure_docx_styles(document)
    _add_docx_paragraph(document, task.title, "LessonPilot Title")
    _add_docx_paragraph(document, f"{task.subject} · {task.grade} · {task.topic}", "LessonPilot Meta")
    for block in content.blocks:
        _render_docx_block(document, block)
    buffer = BytesIO()
    document.save(buffer)
    return buffer.getvalue()


def _build_html_question(
    label: str,
    prompt: str,
    answer: str,
    analysis: str,
    *,
    index: int | None = None,
    options: list[str] | None = None,
) -> str:
    prefix = f'<span class="lp-question-index">{index}.</span>' if index is not None else ""
    parts = [
        '<div class="lp-question">',
        f'<div class="lp-question-title">{prefix}<span>{escape(label)}</span></div>',
        f'<div class="lp-question-body">{prompt}</div>',
    ]
    if options:
        option_items = "".join(
            f"<li>{escape(_to_plain_text(option))}</li>" for option in options if _to_plain_text(option)
        )
        if option_items:
            parts.append(f'<ol class="lp-option-list" type="A">{option_items}</ol>')
    if answer:
        parts.append(f'<p class="lp-answer"><strong>参考答案：</strong>{escape(_to_plain_text(answer))}</p>')
    if analysis:
        parts.append(f'<div class="lp-analysis"><strong>解析：</strong>{analysis}</div>')
    parts.append("</div>")
    return "".join(parts)


def _build_html_block(block, level: int = 1) -> str:
    if block.status != "confirmed":
        return ""

    if isinstance(block, SectionBlock):
        return (
            '<section class="lp-section">'
            f'<h2 class="lp-section-title">{escape(block.title)}</h2>'
            + "".join(_build_html_block(child, level + 1) for child in block.children)
            + "</section>"
        )

    if isinstance(block, TeachingStepBlock):
        duration = f"（{block.duration_minutes}分钟）" if block.duration_minutes else ""
        return (
            '<section class="lp-subsection">'
            f'<h3 class="lp-subsection-title">{escape(block.title + duration)}</h3>'
            + "".join(_build_html_block(child, level + 1) for child in block.children)
            + "</section>"
        )

    if isinstance(block, ExerciseGroupBlock):
        questions = []
        for index, child in enumerate(block.children, start=1):
            if isinstance(child, ChoiceQuestionBlock):
                questions.append(
                    _build_html_question(
                        "选择题",
                        child.prompt,
                        "；".join(child.answers),
                        child.analysis,
                        index=index,
                        options=child.options,
                    )
                )
                continue
            if isinstance(child, FillBlankQuestionBlock):
                questions.append(
                    _build_html_question(
                        "填空题",
                        child.prompt,
                        "；".join(child.answers),
                        child.analysis,
                        index=index,
                    )
                )
                continue
            questions.append(
                _build_html_question(
                    "简答题",
                    child.prompt,
                    child.reference_answer,
                    child.analysis,
                    index=index,
                )
            )
        return (
            '<section class="lp-subsection lp-exercise-group">'
            f'<h3 class="lp-subsection-title">{escape(block.title)}</h3>'
            + "".join(questions)
            + "</section>"
        )

    if isinstance(block, ParagraphBlock):
        margin_left = _indent_px(block.indent)
        return f'<p class="lp-paragraph" style="margin-left: {margin_left}px">{block.content}</p>'

    if isinstance(block, ListBlock):
        items = "".join(f"<li>{item}</li>" for item in block.items if _to_plain_text(item))
        if not items:
            return ""
        margin_left = _indent_px(block.indent)
        return f'<ul class="lp-list" style="margin-left: {margin_left}px">{items}</ul>'

    if isinstance(block, ChoiceQuestionBlock):
        return _build_html_question(
            "选择题",
            block.prompt,
            "；".join(block.answers),
            block.analysis,
            options=block.options,
        )

    if isinstance(block, FillBlankQuestionBlock):
        return _build_html_question(
            "填空题",
            block.prompt,
            "；".join(block.answers),
            block.analysis,
        )

    return _build_html_question(
        "简答题",
        block.prompt,
        block.reference_answer,
        block.analysis,
    )


def _build_export_html(task: Task, content: ContentDocument) -> str:
    body = "".join(_build_html_block(block) for block in content.blocks)
    return f"""
    <!doctype html>
    <html lang="zh-CN">
      <head>
        <meta charset="utf-8" />
        <style>
          @page {{
            size: A4;
            margin: 20mm 18mm 20mm 18mm;
          }}

          body {{
            font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
            color: #243349;
            line-height: 1.7;
            font-size: 12pt;
          }}

          .lp-document-title {{
            margin: 0 0 10pt;
            text-align: center;
            font-size: 22pt;
            font-weight: 700;
          }}

          .lp-document-meta {{
            margin: 0 0 18pt;
            text-align: center;
            color: #6c7a90;
            font-size: 10.5pt;
          }}

          .lp-section {{
            margin-top: 16pt;
          }}

          .lp-section-title {{
            margin: 0 0 8pt;
            color: #16385b;
            font-size: 16pt;
            page-break-after: avoid;
          }}

          .lp-subsection {{
            margin-top: 12pt;
          }}

          .lp-subsection-title {{
            margin: 0 0 6pt;
            color: #2d4b71;
            font-size: 13pt;
            page-break-after: avoid;
          }}

          .lp-paragraph,
          .lp-list li,
          .lp-question-body,
          .lp-answer,
          .lp-analysis {{
            font-size: 11pt;
          }}

          .lp-paragraph {{
            margin: 0 0 8pt;
          }}

          .lp-list {{
            margin: 0 0 8pt 0;
            padding-left: 18pt;
          }}

          .lp-question {{
            margin: 8pt 0 12pt;
            padding: 12pt 14pt;
            border: 1px solid #dbe3ef;
            border-radius: 10pt;
            background: #fafbfc;
            page-break-inside: avoid;
          }}

          .lp-question-title {{
            margin-bottom: 6pt;
            color: #16385b;
            font-weight: 700;
          }}

          .lp-question-index {{
            display: inline-block;
            min-width: 18pt;
          }}

          .lp-option-list {{
            margin: 6pt 0;
            padding-left: 18pt;
          }}

          .lp-answer {{
            margin: 6pt 0 4pt;
            color: #2e7b66;
          }}

          .lp-analysis {{
            margin: 4pt 0 0;
            color: #6c7a90;
          }}
        </style>
      </head>
      <body>
        <h1 class="lp-document-title">{escape(task.title)}</h1>
        <p class="lp-document-meta">{escape(task.subject)} · {escape(task.grade)} · {escape(task.topic)}</p>
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
