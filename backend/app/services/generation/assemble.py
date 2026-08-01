"""Assemble student-facing final_paper JSON from generated item records."""

from __future__ import annotations

from typing import Any


def assemble_final_paper(generated_items: list[dict[str, Any]]) -> dict[str, Any]:
    """Build `{sections: {name: [question, ...]}}` from generated_items."""
    student_paper: dict[str, Any] = {"sections": {}}
    items = sorted(
        (item for item in generated_items if isinstance(item, dict)),
        key=lambda x: x.get("question_number") or 0,
    )
    for item in items:
        sec = item.get("section_name")
        if not sec:
            continue
        student_paper["sections"].setdefault(sec, []).append(
            {
                "question_number": item.get("question_number"),
                "question_type": item.get("question_type"),
                "question_text": item.get("question_text"),
                "options": item.get("options"),
                "marks": item.get("marks"),
                "sub_parts": item.get("sub_parts"),
                "alternate_question_text": item.get("alternate_question_text"),
            }
        )
    return student_paper


def assemble_node(state: dict) -> dict:
    return {"final_paper": assemble_final_paper(state["generated_items"])}
