"""Canonical 40 Marks sample blueprint (SVIS-style Class 10 Mathematics).

Flattened from Bloom's × type × lesson matrix into question-type sections.
CBQ uses CASE_STUDY with marks_each=4 per Question Type / Weightage.
"""

from __future__ import annotations

from typing import Any

# Chapter catalog numbers for Class 10 Mathematics (jemh1)
CH_REAL = {"chapter_number": 1, "chapter_name": "Real Numbers"}
CH_POLY = {"chapter_number": 2, "chapter_name": "Polynomials"}
CH_LINEAR = {
    "chapter_number": 3,
    "chapter_name": "Pair of Linear Equations in Two Variables",
}

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


def _alloc(
    chapter: dict[str, Any],
    count: int,
    *,
    blooms: str,
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
    "school_name": None,
    "exam_title": "PRE-MID TERM EXAMINATION",
    "subject": "Mathematics",
    "grade": 10,
    "total_marks": 40,
    "duration_minutes": 90,
    "exam_date": None,
    "general_instructions": FORTY_MARKS_GENERAL_INSTRUCTIONS,
    "blooms_targets": {
        "REMEMBERING": 10,
        "UNDERSTANDING": 12,
        "APPLYING": 9,
        "ANALYSING": 6,
        "EVALUATING": 2,
        "CREATING": 1,
    },
    "sections": [
        {
            "section_name": "MCQ",
            "question_type": "MCQ",
            "marks_each": 1,
            "section_instructions": None,
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
            "chapter_allocations": [
                _alloc(CH_REAL, 1, blooms="ANALYSING", marks=4, ic=True),
                _alloc(CH_REAL, 1, blooms="REMEMBERING", marks=3),
            ],
        },
    ],
}
