"""Shared copy helpers for paper Markdown and DOCX export."""

from __future__ import annotations

import re
from typing import Any

from app.services.export.latex import normalize_newlines

_OPTION_BLOCK_RE = re.compile(
    r"(?:\n+\s*(?:\(?[A-Da-d]\)|[A-Da-d][).:])\s*[^\n]*)+\s*$"
)
_INLINE_OPTIONS_RE = re.compile(
    r"(?:\s*\([A-Da-d]\)\s+[^\n(]+){2,}\s*$"
)

INLINE_OPTION_GAP = "\u2003\u2003"

QUESTION_TYPE_LABELS: dict[str, str] = {
    "MCQ": "Multiple Choice Questions (MCQs)",
    "ASSERTION_REASON": "Assertion & Reasoning Questions",
    "VSA": "Very Short Answer Questions (VSAQs)",
    "SA": "Short Answer Questions (SAQs)",
    "LA": "Long Answer Questions (LAQs)",
    "CASE_STUDY": "Case Study Based Questions",
    "FILL_IN_THE_BLANK": "Fill in the Blank Questions",
    "TRUE_FALSE": "True / False Questions",
    "OTHER": "Questions",
}


def strip_embedded_options(text: str | None) -> str:
    """Remove option lists the model may have baked into question_text."""
    if not text:
        return ""
    cleaned = text.strip()
    cleaned = _OPTION_BLOCK_RE.sub("", cleaned)
    cleaned = _INLINE_OPTIONS_RE.sub("", cleaned)
    return cleaned.strip()


def format_option_label(raw_option: str, index: int) -> str:
    letter = "abcd"[index] if index < 4 else chr(ord("a") + index)
    stripped = re.sub(r"^\s*\(?[a-dA-D]\)?[.\):]\s*", "", raw_option).strip()
    return f"({letter}) {stripped}"


def format_options_line(options: list[str], *, single_line: bool = True) -> str:
    formatted = [format_option_label(opt, i) for i, opt in enumerate(options)]
    if single_line:
        return INLINE_OPTION_GAP.join(formatted)
    return "\n".join(formatted)


def question_body_lines(
    question_number: int | str | None,
    question_text: str | None,
) -> list[str]:
    """Split question text into lines with the serial number on the first line only."""
    cleaned = normalize_newlines(question_text or "").strip()
    raw_lines = [line.strip() for line in cleaned.split("\n") if line.strip()]
    if question_number is None:
        return raw_lines
    if not raw_lines:
        return [f"{question_number}."]
    lines = [f"{question_number}. {raw_lines[0]}"]
    lines.extend(raw_lines[1:])
    return lines


def format_question_markdown_lines(
    question_number: int | str | None,
    question_text: str | None,
) -> list[str]:
    """Markdown lines for a question stem (bold number on the first line)."""
    body_lines = question_body_lines(question_number, question_text)
    if not body_lines:
        return []
    first = body_lines[0]
    prefix = f"{question_number}. " if question_number is not None else ""
    if prefix and first.startswith(prefix):
        rest = first[len(prefix) :]
        lines = [f"**{question_number}.** {rest}"]
    else:
        lines = [first]
    for line in body_lines[1:]:
        lines.append(f"   {line}")
    return lines


def options_should_be_single_line(question_type: str | None) -> bool:
    return question_type != "ASSERTION_REASON"


def format_section_heading(section_name: str) -> str:
    raw = section_name.strip()
    match = re.match(
        r"^(?:section\s*[–—-]?\s*)([A-Za-z0-9]+)$",
        raw,
        flags=re.IGNORECASE,
    )
    if match:
        return f"SECTION {match.group(1).upper()}"
    if raw.upper().startswith("SECTION"):
        return raw.upper()
    return raw.upper()


def _marks_phrase(marks_each: float) -> str:
    unit = "mark" if abs(marks_each - 1.0) < 1e-9 else "marks"
    return f"{marks_each:g} {unit}"


def section_description(
    *,
    question_type: str | None,
    question_count: int,
    marks_each: float | None,
    total_marks: float,
) -> str:
    """Bold descriptive sentence + marks scheme for a section."""
    scheme = _marks_scheme(question_count, marks_each, total_marks)
    qtype = (question_type or "OTHER").upper()

    if qtype == "CASE_STUDY":
        blurb = (
            "This section comprises Case Study Based Questions. "
            "Read each case carefully and answer the questions that follow."
        )
    elif qtype == "ASSERTION_REASON":
        label = QUESTION_TYPE_LABELS["ASSERTION_REASON"]
        if marks_each is not None:
            blurb = (
                f"This section comprises {label} of "
                f"{_marks_phrase(marks_each)} each."
            )
        else:
            blurb = f"This section comprises {label}."
    elif marks_each is not None and qtype in QUESTION_TYPE_LABELS:
        label = QUESTION_TYPE_LABELS[qtype]
        blurb = (
            f"This section comprises {label} of "
            f"{_marks_phrase(marks_each)} each."
        )
    elif qtype in QUESTION_TYPE_LABELS:
        blurb = f"This section comprises {QUESTION_TYPE_LABELS[qtype]}."
    else:
        blurb = "This section comprises the following questions."

    return f"{blurb}      {scheme}" if scheme else blurb


def _marks_scheme(
    question_count: int,
    marks_each: float | None,
    total_marks: float,
) -> str:
    if question_count <= 0:
        return ""
    if marks_each is not None:
        return f"{question_count} × {marks_each:g} = {total_marks:g}M"
    return f"{question_count} questions, {total_marks:g}M total"


def infer_section_question_type(questions: list[dict[str, Any]]) -> str | None:
    """Prefer the dominant non-AR type so MCQ sections with trailing AR stay MCQ."""
    questions = [q for q in questions if isinstance(q, dict)]
    if not questions:
        return None
    types = [str(q.get("question_type") or "") for q in questions]
    non_ar = [t for t in types if t and t != "ASSERTION_REASON"]
    if non_ar:
        # Most common among non-AR types
        return max(set(non_ar), key=non_ar.count)
    return types[0] or None


def coerce_section_questions(raw: Any) -> list[dict[str, Any]]:
    """Accept only question dicts; drop LLM string / malformed section payloads."""
    if raw is None:
        return []
    if isinstance(raw, dict):
        if "question_text" in raw or "question_number" in raw:
            return [raw]
        return []
    if isinstance(raw, str) or not isinstance(raw, list):
        return []
    return [q for q in raw if isinstance(q, dict)]


def normalize_final_paper(final_paper: Any) -> dict[str, Any]:
    """Coerce final_paper.sections to ``dict[str, list[dict]]``."""
    if not isinstance(final_paper, dict):
        return {"sections": {}}

    sections_raw = final_paper.get("sections")
    sections: dict[str, list[dict[str, Any]]] = {}

    if isinstance(sections_raw, dict):
        for name, questions in sections_raw.items():
            coerced = coerce_section_questions(questions)
            if coerced:
                sections[str(name)] = coerced
    elif isinstance(sections_raw, list):
        for entry in sections_raw:
            if not isinstance(entry, dict):
                continue
            name = entry.get("section_name") or entry.get("name")
            qs = entry.get("questions") or entry.get("items")
            coerced = coerce_section_questions(qs if qs is not None else entry)
            if name and coerced:
                sections[str(name)] = coerced

    return {"sections": sections}


def resolve_final_paper(
    final_paper: Any,
    generated_items: list[Any] | None = None,
) -> dict[str, Any]:
    """Prefer a well-shaped final_paper; otherwise rebuild from generated_items."""
    normalized = normalize_final_paper(final_paper)
    if any(normalized["sections"].values()):
        return normalized

    items = [
        item
        for item in (generated_items or [])
        if isinstance(item, dict) and item.get("section_name")
    ]
    if items:
        from app.services.generation.assemble import assemble_final_paper

        return assemble_final_paper(items)
    return normalized


def section_marks_summary(
    questions: list[dict[str, Any]],
) -> tuple[int, float | None, float]:
    questions = [q for q in questions if isinstance(q, dict)]
    count = len(questions)
    try:
        marks = [float(q.get("marks") or 0) for q in questions]
    except (TypeError, ValueError):
        return count, None, 0.0
    total = sum(marks)
    unique = set(marks)
    each = unique.pop() if len(unique) == 1 else None
    return count, each, total
