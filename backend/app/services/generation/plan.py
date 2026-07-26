from app.schemas.generation import (
    QuestionPaperBlueprint,
    QuestionType,
    Slot,
    SlotSubPart,
)

TYPE_CONTENT_TYPES: dict[QuestionType, list[str]] = {
    QuestionType.MCQ: ["exercise"],
    QuestionType.VSA: ["exercise"],
    QuestionType.FILL_IN_THE_BLANK: ["exercise"],
    QuestionType.TRUE_FALSE: ["exercise"],
    QuestionType.SA: ["example"],
    QuestionType.LA: ["theory", "example"],
    QuestionType.CASE_STUDY: ["theory", "example"],
    QuestionType.ASSERTION_REASON: ["theory", "example"],
    QuestionType.OTHER: ["theory", "example"],
}


def _normalize_name(name: str) -> str:
    return " ".join(name.lower().split())


def _resolve_chapter(
    allocation_chapter_number: int | None,
    allocation_chapter_name: str,
    selected_chapters: list[dict],
    by_number: dict[int, dict],
    by_name: dict[str, dict],
) -> dict:
    if allocation_chapter_number is not None and allocation_chapter_number in by_number:
        return by_number[allocation_chapter_number]

    match = by_name.get(_normalize_name(allocation_chapter_name))
    if match:
        return match

    # Fuzzy: "Pair of Linear Equations" → catalog full name
    needle = _normalize_name(allocation_chapter_name)
    for chapter in selected_chapters:
        catalog_name = _normalize_name(chapter.get("chapter_name", ""))
        if needle in catalog_name or catalog_name in needle:
            return chapter

    if selected_chapters:
        return selected_chapters[0]

    raise ValueError("selected_chapters is empty — pick at least one chapter")


def build_slots(
    question_paper: QuestionPaperBlueprint,
    selected_chapters: list[dict],
) -> list[Slot]:
    if not selected_chapters:
        raise ValueError("selected_chapters is empty — pick at least one chapter")

    by_number = {c["chapter_number"]: c for c in selected_chapters}
    by_name = {_normalize_name(c["chapter_name"]): c for c in selected_chapters}

    slots: list[Slot] = []
    question_number = 0

    for section in question_paper.sections:
        section_sub_parts = [
            SlotSubPart(label=part.label, marks=part.marks)
            for part in section.sub_parts
        ]
        for allocation in section.chapter_allocations:
            chapter = _resolve_chapter(
                allocation.chapter_number,
                allocation.chapter_name,
                selected_chapters,
                by_number,
                by_name,
            )
            q_type = (
                QuestionType.ASSERTION_REASON
                if allocation.is_assertion_reason
                else section.question_type
            )

            for _ in range(allocation.question_count):
                question_number += 1
                marks = (
                    allocation.marks
                    if allocation.marks is not None
                    else section.marks_each
                )
                slots.append(
                    Slot(
                        slot_id=f"Q{question_number}",
                        section_name=section.section_name,
                        question_number=question_number,
                        question_type=q_type,
                        marks=marks,
                        chapter_number=chapter["chapter_number"],
                        chapter_name=chapter.get(
                            "chapter_name", allocation.chapter_name
                        ),
                        book_code=chapter.get("book_code"),
                        content_types=TYPE_CONTENT_TYPES[q_type],
                        has_internal_choice=allocation.has_internal_choice,
                        sub_parts=list(section_sub_parts),
                    )
                )

    return slots


def plan_slots_node(state: dict) -> dict:
    question_paper = QuestionPaperBlueprint.model_validate(state["question_paper"])
    slots = build_slots(question_paper, state["selected_chapters"])
    return {"slots": [s.model_dump(mode="json") for s in slots]}
