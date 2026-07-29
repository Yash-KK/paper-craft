"""Shared copy helpers for paper Markdown and DOCX export."""

from __future__ import annotations

import re
from typing import Any

_OPTION_BLOCK_RE = re.compile(
    r"(?:\n+\s*(?:\(?[A-Da-d]\)|[A-Da-d][).:])\s*[^\n]*)+\s*$"
)
_INLINE_OPTIONS_RE = re.compile(
    r"(?:\s*\([A-Da-d]\)\s+[^\n(]+){2,}\s*$"
)

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
        return "     ".join(formatted)
    return "\n".join(formatted)


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
    if not questions:
        return None
    types = [str(q.get("question_type") or "") for q in questions]
    non_ar = [t for t in types if t and t != "ASSERTION_REASON"]
    if non_ar:
        # Most common among non-AR types
        return max(set(non_ar), key=non_ar.count)
    return types[0] or None


def section_marks_summary(
    questions: list[dict[str, Any]],
) -> tuple[int, float | None, float]:
    count = len(questions)
    try:
        marks = [float(q.get("marks") or 0) for q in questions]
    except (TypeError, ValueError):
        return count, None, 0.0
    total = sum(marks)
    unique = set(marks)
    each = unique.pop() if len(unique) == 1 else None
    return count, each, total
