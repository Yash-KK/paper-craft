"""Canonical sample blueprints for CBSE Mathematics.

Each blueprint is a self-contained template: kind, sections, instructions,
learning outcomes, and generation rules. Grade/chapter placeholders are
rematched to the teacher's notebook when the blueprint is applied.
"""

from __future__ import annotations

from typing import Any

CH_REAL = {"chapter_number": 1, "chapter_name": "Real Numbers"}
CH_POLY = {"chapter_number": 2, "chapter_name": "Polynomials"}
CH_LINEAR = {
    "chapter_number": 3,
    "chapter_name": "Pair of Linear Equations in Two Variables",
}
CH_SELECTED = {"chapter_number": None, "chapter_name": "Selected Chapter"}

FORTY_MARKS_GENERAL_INSTRUCTIONS = [
    "This question paper contains 19 questions. All questions are compulsory.",
    "This question paper is divided into five Sections – A, B, C, D and E.",
    (
        "In Section A, Question Nos. 1–8 are Multiple Choice Questions (MCQs), and "
        "Question Nos. 9–10 are Assertion–Reason based questions carrying 1 mark each."
    ),
    (
        "In Section B, Question Nos. 11–12 are Very Short Answer (VSA) questions "
        "carrying 2 marks each."
    ),
    (
        "In Section C, Question Nos. 13–15 are Short Answer (SA) questions carrying "
        "3 marks each."
    ),
    (
        "In Section D, Question Nos. 16–17 are Long Answer (LA) questions carrying "
        "5 marks each."
    ),
    (
        "In Section E, Question Nos. 18–19 are Case Study based questions carrying "
        "4 marks and 3 marks respectively."
    ),
    (
        "There is no overall choice. However, an internal choice is provided in one "
        "question each from Section B, Section C, Section D, and Section E."
    ),
    "Draw neat diagrams wherever required.",
    "Use of a calculator is not allowed.",
]

REVISION_SHEET_GENERAL_INSTRUCTIONS = [
    "This revision sheet is for practice and concept reinforcement.",
    "Attempt all sections. Show working wherever required.",
    "SECTION I contains Multiple Choice Questions covering key concepts.",
    "SECTION II contains Short Answer / Practice Questions.",
    "SECTION III contains Case Study based questions with sub-parts.",
    "SECTION IV contains Assertion & Reasoning questions.",
    "Use of a calculator is not allowed unless instructed otherwise.",
]

REVISION_SHEET_LEARNING_OUTCOMES = [
    "Conceptual Understanding",
    "Formula / Identity Recall",
    "Application",
    "Analysis",
    "Real-life Context",
    "Reasoning",
    "Higher Order Thinking",
]

REVISION_SHEET_GENERATION_RULES = [
    "Generate a revision/practice sheet, not a timed examination paper.",
    "Prefer one chapter focus when a single chapter is selected; otherwise cover the selected chapters evenly.",
    "MCQs should mix concept checks, application, identity/property recognition, and real-life situations.",
    "Short-answer practice should include simplification, expansion, factorisation, finding values, identity-based problems, word problems, and higher-order items.",
    "Each Case Study must share one scenario with parts (i), (ii), and (iii).",
    "Assertion & Reasoning items must use the standard four options (a)–(d).",
    "Do not invent examination-style mark totals; focus on clear practice questions and worked answers.",
]


def _alloc(
    chapter: dict[str, Any],
    count: int,
    *,
    blooms: str | None = None,
    ic: bool = False,
    ar: bool = False,
    marks: float | None = None,
) -> dict[str, Any]:
    return {
        "chapter_number": chapter["chapter_number"],
        "chapter_name": chapter["chapter_name"],
        "question_count": count,
        "blooms_level": blooms,
        "has_internal_choice": ic,
        "is_assertion_reason": ar,
        "marks": marks,
    }


FORTY_MARKS_BLUEPRINT: dict[str, Any] = {
    "kind": "EXAM",
    "school_name": None,
    "exam_title": "PRE-MID TERM EXAMINATION",
    "subject": "Mathematics",
    "grade": 10,
    "total_marks": 40,
    "duration_minutes": 90,
    "exam_date": None,
    "general_instructions": FORTY_MARKS_GENERAL_INSTRUCTIONS,
    "learning_outcomes": [],
    "generation_rules": [
        "Generate an examination-style question paper matching the marking scheme.",
        "Respect marks, internal choices, and Assertion–Reason nesting under Section A.",
    ],
    "blooms_targets": {
        "REMEMBERING": 10,
        "UNDERSTANDING": 12,
        "APPLYING": 9,
        "ANALYSING": 6,
        "EVALUATING": 2,
        "CREATING": 1,
    },
    "metadata": {},
    "sections": [
        {
            "section_name": "MCQ",
            "question_type": "MCQ",
            "marks_each": 1,
            "section_instructions": None,
            "sub_parts": [],
            "chapter_allocations": [
                _alloc(CH_REAL, 1, blooms="REMEMBERING"),
                _alloc(CH_LINEAR, 1, blooms="REMEMBERING"),
                _alloc(CH_POLY, 1, blooms="UNDERSTANDING"),
                _alloc(CH_REAL, 1, blooms="APPLYING"),
                _alloc(CH_POLY, 1, blooms="ANALYSING"),
                _alloc(CH_POLY, 1, blooms="EVALUATING"),
                _alloc(CH_LINEAR, 1, blooms="EVALUATING"),
                _alloc(CH_REAL, 1, blooms="CREATING"),
                _alloc(CH_LINEAR, 1, blooms="UNDERSTANDING", ar=True),
                _alloc(CH_REAL, 1, blooms="ANALYSING", ar=True),
            ],
        },
        {
            "section_name": "VSA",
            "question_type": "VSA",
            "marks_each": 2,
            "section_instructions": None,
            "sub_parts": [],
            "chapter_allocations": [
                _alloc(CH_LINEAR, 1, blooms="REMEMBERING"),
                _alloc(CH_REAL, 1, blooms="UNDERSTANDING", ic=True),
            ],
        },
        {
            "section_name": "SA",
            "question_type": "SA",
            "marks_each": 3,
            "section_instructions": None,
            "sub_parts": [],
            "chapter_allocations": [
                _alloc(CH_POLY, 1, blooms="REMEMBERING", ic=True),
                _alloc(CH_LINEAR, 1, blooms="UNDERSTANDING"),
                _alloc(CH_REAL, 1, blooms="APPLYING"),
            ],
        },
        {
            "section_name": "LA",
            "question_type": "LA",
            "marks_each": 5,
            "section_instructions": None,
            "sub_parts": [],
            "chapter_allocations": [
                _alloc(CH_POLY, 1, blooms="UNDERSTANDING"),
                _alloc(CH_LINEAR, 1, blooms="APPLYING", ic=True),
            ],
        },
        {
            "section_name": "CBQ",
            "question_type": "CASE_STUDY",
            "marks_each": 4,
            "section_instructions": None,
            "sub_parts": [],
            "chapter_allocations": [
                _alloc(CH_REAL, 1, blooms="ANALYSING", marks=4, ic=True),
                _alloc(CH_REAL, 1, blooms="REMEMBERING", marks=3),
            ],
        },
    ],
}


REVISION_SHEET_BLUEPRINT: dict[str, Any] = {
    "kind": "REVISION_SHEET",
    "school_name": None,
    "exam_title": "REVISION SHEET",
    "subject": "Mathematics",
    "grade": 10,
    "total_marks": None,
    "duration_minutes": None,
    "exam_date": None,
    "general_instructions": REVISION_SHEET_GENERAL_INSTRUCTIONS,
    "learning_outcomes": REVISION_SHEET_LEARNING_OUTCOMES,
    "generation_rules": REVISION_SHEET_GENERATION_RULES,
    "blooms_targets": None,
    "metadata": {
        "typical_scope": "per_chapter",
        "assertion_reason_range": {"min": 2, "max": 5},
    },
    "sections": [
        {
            "section_name": "SECTION I : Multiple Choice Questions (MCQs)",
            "question_type": "MCQ",
            "marks_each": None,
            "section_instructions": (
                "10 Questions covering important concepts, including application-based "
                "MCQs, identity/property recognition, and real-life situations."
            ),
            "sub_parts": [],
            "chapter_allocations": [
                _alloc(CH_SELECTED, 10, blooms="UNDERSTANDING"),
            ],
        },
        {
            "section_name": "SECTION II : Short Answer / Practice Questions",
            "question_type": "SA",
            "marks_each": None,
            "section_instructions": (
                "10 Questions including simplification, expansion, factorisation, "
                "finding values, identity-based problems, word problems, and "
                "higher-order questions."
            ),
            "sub_parts": [],
            "chapter_allocations": [
                _alloc(CH_SELECTED, 10, blooms="APPLYING"),
            ],
        },
        {
            "section_name": "SECTION III : Case Study",
            "question_type": "CASE_STUDY",
            "marks_each": None,
            "section_instructions": (
                "Two case studies. Each case study has parts (i), (ii), and (iii)."
            ),
            "sub_parts": [
                {"label": "i", "marks": None},
                {"label": "ii", "marks": None},
                {"label": "iii", "marks": None},
            ],
            "chapter_allocations": [
                _alloc(CH_SELECTED, 2, blooms="ANALYSING"),
            ],
        },
        {
            "section_name": "SECTION IV : Assertion & Reasoning",
            "question_type": "ASSERTION_REASON",
            "marks_each": None,
            "section_instructions": (
                "2–5 Assertion & Reasoning questions with options (a), (b), (c), (d)."
            ),
            "sub_parts": [],
            "chapter_allocations": [
                _alloc(CH_SELECTED, 3, blooms="EVALUATING"),
            ],
        },
    ],
}
