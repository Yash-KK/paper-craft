from app.schemas.generation import (
    GeneratedPaperResponse,
    GeneratedQuestion,
    QuestionType,
)
from app.services.chat.llm import get_chat_model

GENERATION_BATCH_SIZE = 5
GENERATION_MAX_CONCURRENCY = 4

ASSERTION_REASON_OPTIONS = [
    "Both Assertion (A) and Reason (R) are true and Reason (R) is the correct explanation of Assertion (A).",
    "Both Assertion (A) and Reason (R) are true and Reason (R) is not the correct explanation of Assertion (A).",
    "Assertion (A) is true but Reason (R) is false.",
    "Assertion (A) is false but Reason (R) is true.",
]

GENERATION_SYSTEM_INSTRUCTIONS = """You are an expert mathematics educator writing questions for school worksheets and examinations. For each spec (marked `=== slot_id: <id> ===`) produce exactly one GeneratedQuestion whose slot_id matches. Never omit, merge, duplicate, reorder, or invent slot_ids. Treat each slot independently.

GROUNDING
- The supplied textbook source text is the source of truth for concepts, definitions, terminology, methods, theorems, values, examples, and exercises.
- It is OCR/chunked and may be incomplete. Use your own subject knowledge ONLY to: repair OCR/chunk gaps, complete standard notation/terminology, finish a partially shown method, and write plausible distractors.
- Never introduce chapter-specific facts/formulas/values not supported by the source or by universally standard subject knowledge. If source and your knowledge conflict, trust the source.

EACH QUESTION must be academically correct, unambiguous, fully solvable, concise, and must match the spec's question type — without revealing its answer. Do not include answers, solutions, marking rubrics, or correct-option keys.

TYPE SPECIFICS
- MCQ: exactly 4 plausible, not-trivially-eliminable options in the options array only. Never list A)/B)/C)/D) or (a)/(b)/(c)/(d) inside question_text — options are rendered separately. Prefer adapting a textbook exercise when one fits.
- ASSERTION_REASON: question_text holds ONLY the Assertion (A) and Reason (R) (no options — standard AR choices are appended later), both grounded in the source.
- CASE_STUDY (sub_parts present): one shared scenario, then each sub-part in order, labeled (i),(ii),(iii)…; include marks only when the sub-part specifies them.
- SA/LA/VSA: grounded in source examples/theory; change numbers/context so the question is not a verbatim copy when adapting examples.

INTERNAL CHOICE (has_internal_choice=true): fill alternate_question_text — a full alternate for a normal question, but only the specified sub-part's alternate for a case study. Otherwise leave it null.

source_chunk_ids: list only chunk_ids that actually contributed; never fabricate.

Return only a valid GeneratedPaperResponse. Faithfulness and accuracy outrank creativity.
"""


def _chunked(seq: list, size: int):
    for i in range(0, len(seq), size):
        yield seq[i : i + size]


def _render_slot_block(slot: dict) -> str:
    chunks = slot.get("context_chunks", [])
    context_text = (
        "\n\n---\n\n".join(f"[{c['chunk_id']}]\n{c['text']}" for c in chunks)
        or "(no source text found)"
    )

    sub_parts_text = ""
    if slot.get("sub_parts"):
        lines = []
        for sp in slot["sub_parts"]:
            marks = sp.get("marks")
            marks_bit = f" {marks} marks" if marks is not None else ""
            choice_bit = (
                " [internal choice here]" if sp.get("has_internal_choice") else ""
            )
            lines.append(f"  - ({sp['label']}){marks_bit}{choice_bit}")
        sub_parts_text = "\nSub-parts required:\n" + "\n".join(lines)

    marks = slot.get("marks")
    marks_line = (
        f"Marks: {marks}" if marks is not None else "Marks: (ungraded practice)"
    )

    return f"""\
=== slot_id: {slot["slot_id"]} ===
Section: {slot["section_name"]}
Question type: {slot["question_type"]}
{marks_line}
Chapter: {slot["chapter_number"]} ({slot["chapter_name"]})
has_internal_choice: {slot["has_internal_choice"]}{sub_parts_text}
Source text:
{context_text}
"""


def validate_generated(slot: dict, gq: GeneratedQuestion) -> list[str]:
    errors = []

    if slot["question_type"] == QuestionType.MCQ.value and (
        not gq.options or len(gq.options) != 4
    ):
        errors.append("MCQ must have exactly 4 options")

    if slot["has_internal_choice"] and not gq.alternate_question_text:
        errors.append(
            "has_internal_choice is true but alternate_question_text is missing"
        )

    return errors


def _build_batch_messages(
    slots: list[dict],
    *,
    general_instructions: list[str] | None = None,
    generation_rules: list[str] | None = None,
    teacher_instructions: str | None = None,
    feedback_by_slot: dict[str, str] | None = None,
) -> list[tuple]:
    blocks = "\n\n".join(_render_slot_block(slot) for slot in slots)

    header = f"Generate all {len(slots)} questions below, one item per slot_id:"
    if feedback_by_slot:
        batch_feedback = {
            s["slot_id"]: feedback_by_slot[s["slot_id"]]
            for s in slots
            if s["slot_id"] in feedback_by_slot
        }
        feedback_text = "\n".join(
            f"- {sid}: {err}" for sid, err in batch_feedback.items()
        )
        header = (
            f"Your previous attempt had validation errors on these slot_ids - fix them and "
            f"return ONLY these {len(slots)} items:\n{feedback_text}\n\nSpecs:"
        )

    teacher_block = ""
    if teacher_instructions:
        teacher_block = (
            "\n\nTEACHER INSTRUCTIONS (follow when writing questions; "
            "do not change the slot/marks structure):\n"
            f"{teacher_instructions}\n"
        )

    edited_instructions = [
        instruction.strip()
        for instruction in (general_instructions or [])
        if instruction.strip()
    ]
    general_instructions_block = ""
    if edited_instructions:
        rendered = "\n".join(
            f"{index}. {instruction}"
            for index, instruction in enumerate(edited_instructions, start=1)
        )
        general_instructions_block = (
            "\n\nGENERAL INSTRUCTIONS FOR THE FINAL PAPER "
            "(this is the teacher-edited version; ensure the generated questions "
            "conform to it):\n"
            f"{rendered}\n"
        )

    generation_rules_block = ""
    cleaned_rules = [rule.strip() for rule in (generation_rules or []) if rule.strip()]
    if cleaned_rules:
        rendered_rules = "\n".join(f"- {rule}" for rule in cleaned_rules)
        generation_rules_block = f"\n\nBLUEPRINT GENERATION RULES:\n{rendered_rules}\n"

    return [
        ("system", GENERATION_SYSTEM_INSTRUCTIONS),
        (
            "human",
            (
                f"{header}{general_instructions_block}{generation_rules_block}"
                f"{teacher_block}\n\n{blocks}"
            ),
        ),
    ]


def _run_batches_parallel(
    batches: list[list[dict]],
    *,
    general_instructions: list[str] | None = None,
    generation_rules: list[str] | None = None,
    teacher_instructions: str | None = None,
    feedback_by_slot: dict[str, str] | None = None,
) -> dict[str, GeneratedQuestion]:
    if not batches:
        return {}

    structured_llm = (
        get_chat_model()
        .bind(max_tokens=16000)
        .with_structured_output(GeneratedPaperResponse)
    )
    message_lists = [
        _build_batch_messages(
            batch,
            general_instructions=general_instructions,
            generation_rules=generation_rules,
            teacher_instructions=teacher_instructions,
            feedback_by_slot=feedback_by_slot,
        )
        for batch in batches
    ]

    responses = structured_llm.batch(
        message_lists,
        config={"max_concurrency": GENERATION_MAX_CONCURRENCY},
        return_exceptions=True,
    )

    items_by_slot: dict[str, GeneratedQuestion] = {}
    for response in responses:
        # return_exceptions=True can surface BaseException (e.g. SystemExit from
        # Celery SIGTERM). Those are not Exception subclasses — re-raise them.
        if isinstance(response, BaseException):
            if isinstance(response, Exception):
                continue
            raise response
        for item in response.items:
            items_by_slot[item.slot_id] = item
    return items_by_slot


def generate_paper_node(state: dict) -> dict:
    slots = state["slots"]
    slots_by_id = {s["slot_id"]: s for s in slots}
    question_paper = state["question_paper"]
    general_instructions = question_paper.get("general_instructions") or []
    generation_rules = question_paper.get("generation_rules") or []
    teacher_instructions = (state.get("teacher_instructions") or "").strip() or None

    items_by_slot: dict[str, GeneratedQuestion] = {}

    def validate_all() -> dict[str, str]:
        errors: dict[str, str] = {}
        for slot_id, slot in slots_by_id.items():
            gq = items_by_slot.get(slot_id)
            errs = (
                ["missing from model output"]
                if gq is None
                else validate_generated(slot, gq)
            )
            if errs:
                errors[slot_id] = "; ".join(errs)
        return errors

    initial_batches = list(_chunked(slots, GENERATION_BATCH_SIZE))
    items_by_slot = _run_batches_parallel(
        initial_batches,
        general_instructions=general_instructions,
        generation_rules=generation_rules,
        teacher_instructions=teacher_instructions,
    )
    errors_by_slot = validate_all()

    if errors_by_slot:
        retry_slots = [slots_by_id[sid] for sid in errors_by_slot]
        retry_batches = list(_chunked(retry_slots, GENERATION_BATCH_SIZE))
        items_by_slot.update(
            _run_batches_parallel(
                retry_batches,
                general_instructions=general_instructions,
                generation_rules=generation_rules,
                teacher_instructions=teacher_instructions,
                feedback_by_slot=errors_by_slot,
            )
        )
        errors_by_slot = validate_all()
    generated_items = []
    for slot_id, slot in slots_by_id.items():
        gq = items_by_slot.get(slot_id)
        status = (
            "needs_manual_review" if slot_id in errors_by_slot or gq is None else "ok"
        )

        options = gq.options if gq else None
        if gq and slot["question_type"] == QuestionType.ASSERTION_REASON.value:
            options = ASSERTION_REASON_OPTIONS

        generated_items.append(
            {
                "slot_id": slot_id,
                "section_name": slot["section_name"],
                "question_number": slot["question_number"],
                "question_type": slot["question_type"],
                "marks": slot["marks"],
                "chapter_number": slot["chapter_number"],
                "chapter_name": slot["chapter_name"],
                "has_internal_choice": slot["has_internal_choice"],
                "sub_parts": slot["sub_parts"],
                "question_text": gq.question_text if gq else None,
                "options": options,
                "alternate_question_text": gq.alternate_question_text if gq else None,
                "source_chunk_ids": gq.source_chunk_ids if gq else [],
                "status": status,
            }
        )

    return {"generated_items": generated_items}
