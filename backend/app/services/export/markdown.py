"""Render assembled generation JSON as Markdown for the UI."""

from __future__ import annotations

from typing import Any

from app.services.export.latex import normalize_newlines
from app.services.export.section_copy import (
    format_option_label,
    format_options_line,
    format_section_heading,
    infer_section_question_type,
    options_should_be_single_line,
    section_description,
    section_marks_summary,
    strip_embedded_options,
)


def _get(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def render_paper_markdown(
    question_paper: Any,
    final_paper: dict[str, Any],
) -> str:
    """Student-facing question paper as Markdown (LaTeX delimiters preserved)."""
    lines: list[str] = []

    school = _get(question_paper, "school_name")
    exam = _get(question_paper, "exam_title")
    subject = _get(question_paper, "subject")
    grade = _get(question_paper, "grade")
    total_marks = _get(question_paper, "total_marks")
    duration = _get(question_paper, "duration_minutes")
    general = _get(question_paper, "general_instructions") or []

    if school:
        lines.append(f"# {school}")
    if exam:
        lines.append(f"## {exam}")

    meta_bits: list[str] = []
    if subject:
        meta_bits.append(f"**Subject:** {subject}")
    if grade is not None:
        meta_bits.append(f"**Grade:** {grade}")
    if duration:
        hours = duration / 60
        meta_bits.append(f"**Duration:** {hours:g} hour(s)")
    if total_marks is not None:
        meta_bits.append(f"**Max marks:** {total_marks}")
    if meta_bits:
        lines.append("  \n".join(meta_bits))

    if general:
        lines.append("### General Instructions")
        for i, instr in enumerate(general, start=1):
            lines.append(f"{i}. {instr}")

    type_by_section = _section_question_type_map(question_paper)
    instructions_by_section = _section_instructions_map(question_paper)
    sections = final_paper.get("sections") or {}

    for section_name in _ordered_section_names(question_paper, sections):
        questions = sections.get(section_name) or []
        if not questions:
            continue
        lines.append(f"## {format_section_heading(section_name)}")
        count, marks_each, total = section_marks_summary(questions)
        custom = instructions_by_section.get(section_name)
        if custom and str(custom).strip():
            description = str(custom).strip()
            if marks_each is not None and "×" not in description:
                description = (
                    f"{description}      {count} × {marks_each:g} = {total:g}M"
                )
        else:
            description = section_description(
                question_type=type_by_section.get(section_name)
                or infer_section_question_type(questions),
                question_count=count,
                marks_each=marks_each,
                total_marks=total,
            )
        lines.append(f"**{description}**")

        case_study_counter = 0
        for q in questions:
            if q.get("question_type") == "CASE_STUDY":
                case_study_counter += 1
                lines.append(f"### Case Study - {case_study_counter}")

            q_num = q.get("question_number", "")
            q_text = normalize_newlines(q.get("question_text") or "").strip()
            options = q.get("options") or []
            if options:
                q_text = strip_embedded_options(q_text)
            lines.append(f"**{q_num}.** {q_text}")

            if options:
                if options_should_be_single_line(q.get("question_type")):
                    lines.append(format_options_line(options, single_line=True))
                else:
                    lines.append(
                        "\n".join(
                            format_option_label(opt, i)
                            for i, opt in enumerate(options)
                        )
                    )

            alt = q.get("alternate_question_text")
            if alt:
                lines.append("**(OR)**")
                alt_text = normalize_newlines(alt).strip()
                if options:
                    alt_text = strip_embedded_options(alt_text)
                lines.append(alt_text)

    return "\n\n".join(line for line in lines if line is not None).strip() + "\n"


def render_answer_key_markdown(
    question_paper: Any,
    final_answer_key: dict[str, Any],
) -> str:
    """Teacher-facing answer key as Markdown."""
    lines: list[str] = []

    exam = _get(question_paper, "exam_title") or "Question Paper"
    lines.append(f"# {exam} — Answer Key")

    sections = final_answer_key.get("sections") or {}
    for section_name in _ordered_section_names(question_paper, sections):
        items = sections.get(section_name) or []
        if not items:
            continue
        lines.append(f"## {format_section_heading(section_name)}")
        for item in items:
            label = f"Q{item.get('question_number', '')}"
            meta_bits = [
                b for b in [item.get("chapter_name"), item.get("blooms_level")] if b
            ]
            if meta_bits:
                label += f" ({', '.join(meta_bits)})"
            lines.append(f"### {label}")

            status = item.get("status")
            if status and status != "ok":
                lines.append(f"**Flagged for review:** {status}")

            if item.get("correct_option"):
                lines.append(f"**Correct option:** ({item['correct_option']})")

            lines.append("**Answer:**")
            lines.append(normalize_newlines(item.get("answer") or "").strip())

            rubric = item.get("marking_rubric") or []
            if rubric:
                lines.append("**Marking scheme:**")
                for step in rubric:
                    desc = step.get("description", "")
                    marks = step.get("marks", "")
                    try:
                        marks_txt = f"{float(marks):g}"
                    except (TypeError, ValueError):
                        marks_txt = str(marks)
                    lines.append(f"- {desc} ({marks_txt} marks)")

            alt = item.get("alternate_answer")
            if alt:
                lines.append("**(OR) Alternate:**")
                lines.append(normalize_newlines(alt).strip())

    return "\n\n".join(line for line in lines if line is not None).strip() + "\n"


def _section_question_type_map(question_paper: Any) -> dict[str, str | None]:
    result: dict[str, str | None] = {}
    for section in _get(question_paper, "sections") or []:
        name = _get(section, "section_name")
        qtype = _get(section, "question_type")
        if name:
            if qtype is not None and hasattr(qtype, "value"):
                qtype = qtype.value
            result[str(name)] = str(qtype) if qtype else None
    return result


def _section_instructions_map(question_paper: Any) -> dict[str, str | None]:
    result: dict[str, str | None] = {}
    for section in _get(question_paper, "sections") or []:
        name = _get(section, "section_name")
        instr = _get(section, "section_instructions")
        if name:
            result[str(name)] = instr
    return result


def _ordered_section_names(
    question_paper: Any, assembled_sections: dict[str, Any]
) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for section in _get(question_paper, "sections") or []:
        name = _get(section, "section_name")
        if name and str(name) not in seen:
            ordered.append(str(name))
            seen.add(str(name))
    for name in assembled_sections:
        if name not in seen:
            ordered.append(name)
            seen.add(name)
    return ordered
