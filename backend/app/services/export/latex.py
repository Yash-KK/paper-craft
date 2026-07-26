"""LaTeX / Markdown helpers shared by DOCX and Markdown exporters."""

from __future__ import annotations

import re

MATH_SPAN_RE = re.compile(r"(\$\$.*?\$\$|\$[^$]+\$)", re.DOTALL)

LEADING_LIST_MARKER_RE = re.compile(
    r"^( {0,3})(\(?)(\d+|[A-Za-z]|[ivxlcdmIVXLCDM]+)([.)])(\s)"
)


def normalize_latex_delimiters(text: str) -> str:
    """Convert \\(...\\) / \\[...\\] to $...$ / $$...$$ for pandoc."""
    text = text.replace("\\[", "$$").replace("\\]", "$$")
    text = text.replace("\\(", "$").replace("\\)", "$")
    return text


def escape_markdown_outside_math(text: str) -> str:
    """Escape markdown-sensitive characters outside $...$/$$...$$ spans."""
    parts = MATH_SPAN_RE.split(text)
    out: list[str] = []
    for part in parts:
        if part and MATH_SPAN_RE.fullmatch(part):
            out.append(part)
        else:
            out.append(re.sub(r"([\\*_\[\]`])", r"\\\1", part))
    return "".join(out)


def escape_leading_list_marker(line: str) -> str:
    match = LEADING_LIST_MARKER_RE.match(line)
    if not match:
        return line
    start = match.start(4)
    return line[:start] + "\\" + line[start:]


def prepare_markdown_for_pandoc(text: str) -> str:
    text = escape_markdown_outside_math(normalize_latex_delimiters(text))
    return "\n".join(escape_leading_list_marker(line) for line in text.split("\n"))


def normalize_newlines(text: str) -> str:
    """Turn literal ``\\n`` (when not followed by a letter) into real newlines."""
    return re.sub(r"\\n(?![A-Za-z])", "\n", text)
