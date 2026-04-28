r"""Math formula text helpers.

The LLM returns section content as JSON. Bare LaTeX commands such as
``\frac`` are valid-looking JSON escapes (``\f``) and can be corrupted during
``json.loads``. These helpers preserve common LaTeX text before parsing and
repair older parsed values when possible.
"""

from __future__ import annotations

import re
from typing import Any

_LATEX_COMMAND_RE = re.compile(r"(?<!\\)\\([A-Za-z]{2,})")
_LATEX_DELIMITER_RE = re.compile(r"(?<!\\)\\([()[\]])")

_CONTROL_REPAIRS: tuple[tuple[str, str], ...] = (
    ("\x0crac", r"\frac"),
    ("\x0cbox", r"\fbox"),
    ("\times", r"\times"),
    ("\theta", r"\theta"),
    ("\tfrac", r"\tfrac"),
    ("\text", r"\text"),
    ("\tan", r"\tan"),
    ("\to", r"\to"),
    ("\beta", r"\beta"),
    ("\begin", r"\begin"),
    ("\rho", r"\rho"),
    ("\right", r"\right"),
    ("\nabla", r"\nabla"),
)


def escape_latex_for_json(raw: str) -> str:
    """Escape bare LaTeX commands and delimiters before JSON parsing."""

    text = _LATEX_DELIMITER_RE.sub(r"\\\\\1", raw)
    return _LATEX_COMMAND_RE.sub(r"\\\\\1", text)


def repair_latex_text(text: str) -> str:
    """Repair common LaTeX commands already damaged by JSON escapes."""

    repaired = text
    for broken, fixed in _CONTROL_REPAIRS:
        repaired = repaired.replace(broken, fixed)
    return repaired


def repair_latex_in_value(value: Any) -> Any:
    """Recursively repair LaTeX text in JSON-like values."""

    if isinstance(value, str):
        return repair_latex_text(value)
    if isinstance(value, list):
        return [repair_latex_in_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(repair_latex_in_value(item) for item in value)
    if isinstance(value, dict):
        return {key: repair_latex_in_value(item) for key, item in value.items()}
    return value
