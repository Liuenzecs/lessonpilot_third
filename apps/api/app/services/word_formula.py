"""Render LaTeX snippets as Word OMML math elements."""

from __future__ import annotations

from dataclasses import dataclass

from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from app.services.formula_text import repair_latex_text


@dataclass(frozen=True)
class FormulaSegment:
    kind: str
    text: str


@dataclass
class MathNode:
    kind: str
    text: str = ""
    children: list["MathNode"] | None = None
    numerator: list["MathNode"] | None = None
    denominator: list["MathNode"] | None = None
    degree: list["MathNode"] | None = None
    radicand: list["MathNode"] | None = None
    base: "MathNode | None" = None
    sup: list["MathNode"] | None = None
    sub: list["MathNode"] | None = None


_DELIMITERS = (("$$", "$$"), (r"\[", r"\]"), (r"\(", r"\)"))

_COMMAND_TEXT = {
    "alpha": "α",
    "beta": "β",
    "gamma": "γ",
    "delta": "δ",
    "theta": "θ",
    "lambda": "λ",
    "mu": "μ",
    "pi": "π",
    "rho": "ρ",
    "sigma": "σ",
    "phi": "φ",
    "omega": "ω",
    "times": "×",
    "cdot": "·",
    "div": "÷",
    "pm": "±",
    "mp": "∓",
    "leq": "≤",
    "le": "≤",
    "geq": "≥",
    "ge": "≥",
    "neq": "≠",
    "approx": "≈",
    "infty": "∞",
    "circ": "°",
    "Rightarrow": "⇒",
    "rightarrow": "→",
    "leftarrow": "←",
    "Leftrightarrow": "⇔",
    "sin": "sin",
    "cos": "cos",
    "tan": "tan",
    "log": "log",
    "ln": "ln",
}


def split_formula_segments(text: str) -> list[FormulaSegment]:
    repaired = repair_latex_text(text)
    segments: list[FormulaSegment] = []
    cursor = 0
    while cursor < len(repaired):
        match = _next_delimiter(repaired, cursor)
        if match is None:
            segments.append(FormulaSegment("text", repaired[cursor:]))
            break
        index, opening, closing = match
        if index > cursor:
            segments.append(FormulaSegment("text", repaired[cursor:index]))
        start = index + len(opening)
        end = repaired.find(closing, start)
        if end == -1:
            segments.append(FormulaSegment("text", repaired[index:]))
            break
        formula = repaired[start:end].strip()
        if formula:
            segments.append(FormulaSegment("formula", formula))
        cursor = end + len(closing)
    return segments


def build_omath(latex: str):
    root = OxmlElement("m:oMath")
    nodes = _LatexParser(latex).parse()
    _append_nodes(root, nodes or [MathNode("text", latex)])
    return root


def _next_delimiter(text: str, cursor: int) -> tuple[int, str, str] | None:
    result: tuple[int, str, str] | None = None
    for opening, closing in _DELIMITERS:
        index = text.find(opening, cursor)
        if index != -1 and (result is None or index < result[0]):
            result = (index, opening, closing)
    return result


class _LatexParser:
    def __init__(self, text: str) -> None:
        self.text = text
        self.index = 0

    def parse(self) -> list[MathNode]:
        return self._parse_until(None)

    def _parse_until(self, stop: str | None) -> list[MathNode]:
        nodes: list[MathNode] = []
        while self.index < len(self.text):
            if stop and self.text[self.index] == stop:
                self.index += 1
                break
            node = self._parse_atom()
            node = self._parse_scripts(node)
            nodes.append(node)
        return _merge_text_nodes(nodes)

    def _parse_atom(self) -> MathNode:
        char = self._peek()
        if char == "{":
            return MathNode("group", children=self._parse_group())
        if char == "\\":
            return self._parse_command()
        self.index += 1
        return MathNode("text", char)

    def _parse_command(self) -> MathNode:
        self.index += 1
        name = self._read_command_name()
        if name in {"frac", "dfrac", "tfrac"}:
            return MathNode("frac", numerator=self._parse_group(), denominator=self._parse_group())
        if name == "sqrt":
            degree = self._parse_optional_bracket_group()
            return MathNode("rad", degree=degree, radicand=self._parse_group())
        if name == "text":
            return MathNode("text", "".join(node.text for node in self._parse_group()))
        if name in {"left", "right"}:
            return self._parse_atom() if self.index < len(self.text) else MathNode("text", "")
        return MathNode("text", _COMMAND_TEXT.get(name, f"\\{name}"))

    def _parse_scripts(self, base: MathNode) -> MathNode:
        sup: list[MathNode] | None = None
        sub: list[MathNode] | None = None
        while self._peek() in {"^", "_"}:
            marker = self._peek()
            self.index += 1
            value = self._parse_script_value()
            if marker == "^":
                sup = value
            else:
                sub = value
        if sup and sub:
            return MathNode("subsup", base=base, sup=sup, sub=sub)
        if sup:
            return MathNode("sup", base=base, sup=sup)
        if sub:
            return MathNode("sub", base=base, sub=sub)
        return base

    def _parse_script_value(self) -> list[MathNode]:
        if self._peek() == "{":
            return self._parse_group()
        return [self._parse_atom()]

    def _parse_group(self) -> list[MathNode]:
        if self._peek() != "{":
            return [self._parse_atom()] if self.index < len(self.text) else []
        self.index += 1
        return self._parse_until("}")

    def _parse_optional_bracket_group(self) -> list[MathNode] | None:
        if self._peek() != "[":
            return None
        self.index += 1
        return self._parse_until("]")

    def _read_command_name(self) -> str:
        start = self.index
        while self.index < len(self.text) and self.text[self.index].isalpha():
            self.index += 1
        if self.index == start and self.index < len(self.text):
            self.index += 1
        return self.text[start:self.index]

    def _peek(self) -> str:
        return self.text[self.index] if self.index < len(self.text) else ""


def _merge_text_nodes(nodes: list[MathNode]) -> list[MathNode]:
    merged: list[MathNode] = []
    for node in nodes:
        if node.kind == "text" and merged and merged[-1].kind == "text":
            merged[-1].text += node.text
        else:
            merged.append(node)
    return merged


def _append_nodes(parent, nodes: list[MathNode] | None) -> None:
    for node in nodes or []:
        _append_node(parent, node)


def _append_node(parent, node: MathNode) -> None:
    if node.kind == "text":
        parent.append(_math_run(node.text))
    elif node.kind == "group":
        _append_nodes(parent, node.children)
    elif node.kind == "frac":
        parent.append(_fraction(node.numerator, node.denominator))
    elif node.kind == "rad":
        parent.append(_radical(node.degree, node.radicand))
    elif node.kind in {"sup", "sub", "subsup"}:
        parent.append(_script(node))


def _math_run(text: str):
    run = OxmlElement("m:r")
    text_el = OxmlElement("m:t")
    text_el.text = text
    run.append(text_el)
    return run


def _argument(tag: str, nodes: list[MathNode] | None):
    element = OxmlElement(tag)
    _append_nodes(element, nodes)
    return element


def _fraction(numerator: list[MathNode] | None, denominator: list[MathNode] | None):
    element = OxmlElement("m:f")
    element.append(_argument("m:num", numerator))
    element.append(_argument("m:den", denominator))
    return element


def _radical(degree: list[MathNode] | None, radicand: list[MathNode] | None):
    element = OxmlElement("m:rad")
    if not degree:
        props = OxmlElement("m:radPr")
        deg_hide = OxmlElement("m:degHide")
        deg_hide.set(qn("m:val"), "1")
        props.append(deg_hide)
        element.append(props)
    element.append(_argument("m:deg", degree))
    element.append(_argument("m:e", radicand))
    return element


def _script(node: MathNode):
    tag = {"sup": "m:sSup", "sub": "m:sSub", "subsup": "m:sSubSup"}[node.kind]
    element = OxmlElement(tag)
    element.append(_argument("m:e", [node.base] if node.base else []))
    if node.kind in {"sub", "subsup"}:
        element.append(_argument("m:sub", node.sub))
    if node.kind in {"sup", "subsup"}:
        element.append(_argument("m:sup", node.sup))
    return element
