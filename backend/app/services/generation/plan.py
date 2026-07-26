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


def assign_chapters(n: int, chapter_numbers: list[int]) -> list[int]:
    """Largest-remainder equal apportionment, interleaved across chapters."""
    if n == 0 or not chapter_numbers:
        return []
    k = len(chapter_numbers)
    base, rem = divmod(n, k)
    counts = {ch: base for ch in chapter_numbers}
    for ch in chapter_numbers[:rem]:
        counts[ch] += 1

    pool: list[int] = []
    remaining = dict(counts)
    while sum(remaining.values()) > 0:
        for ch in chapter_numbers:
            if remaining[ch] > 0:
                pool.append(ch)
                remaining[ch] -= 1
    return pool[:n]


def build_slots(
    question_paper: QuestionPaperBlueprint,
    selected_chapters: list[dict],
) -> list[Slot]:
    if not selected_chapters:
        raise ValueError("selected_chapters is empty — pick at least one chapter")

    chapter_numbers = [c["chapter_number"] for c in selected_chapters]
    by_number = {c["chapter_number"]: c for c in selected_chapters}

    all_questions = [
        (section, q) for section in question_paper.sections for q in section.questions
    ]
    chapter_pool = iter(assign_chapters(len(all_questions), chapter_numbers))

    slots: list[Slot] = []
    for section, q in all_questions:
        chapter_number = next(chapter_pool)
        chapter = by_number[chapter_number]
        slots.append(
            Slot(
                slot_id=f"Q{q.question_number}",
                section_name=section.section_name,
                question_number=q.question_number,
                question_type=q.question_type,
                marks=q.marks,
                chapter_number=chapter_number,
                chapter_name=chapter.get("chapter_name", f"Chapter {chapter_number}"),
                book_code=chapter.get("book_code"),
                content_types=TYPE_CONTENT_TYPES.get(
                    q.question_type, ["theory", "example"]
                ),
                has_internal_choice=q.has_internal_choice,
                sub_parts=[
                    SlotSubPart(
                        label=sp.label,
                        marks=sp.marks,
                        has_internal_choice=sp.has_internal_choice,
                    )
                    for sp in q.sub_parts
                ],
            )
        )
    return slots


def plan_slots_node(state: dict) -> dict:
    question_paper = QuestionPaperBlueprint.model_validate(state["question_paper"])
    slots = build_slots(question_paper, state["selected_chapters"])
    return {"slots": [s.model_dump(mode="json") for s in slots]}
