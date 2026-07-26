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
    "general_instructions": [],
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
                _alloc(CH_LINEAR, 1, blooms="UNDERSTANDING", ar=True),
                _alloc(CH_REAL, 1, blooms="APPLYING"),
                _alloc(CH_REAL, 1, blooms="ANALYSING", ar=True),
                _alloc(CH_POLY, 1, blooms="ANALYSING"),
                _alloc(CH_POLY, 1, blooms="EVALUATING"),
                _alloc(CH_LINEAR, 1, blooms="EVALUATING"),
                _alloc(CH_REAL, 1, blooms="CREATING"),
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
                # Sample listed Remembering CBQ as 3M; Analysing CBQ as 4M.
                _alloc(CH_REAL, 1, blooms="REMEMBERING", marks=3),
                _alloc(CH_REAL, 1, blooms="ANALYSING", marks=4),
            ],
        },
    ],
}
