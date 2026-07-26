"""Build styled question-paper / answer-key DOCX files from generation JSON.

Ported from ``notebooks/export_to_docx.py``. Requires ``pandoc`` on PATH for
LaTeX → native Word equation conversion.
"""

from __future__ import annotations

import copy
import io
import re
import shutil
import subprocess
import zipfile
from pathlib import Path
from typing import Any

import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import qn
from docx.shared import Pt
from docx.text.run import Run

from app.services.export.latex import normalize_newlines, prepare_markdown_for_pandoc

FONT_NAME = "Bookman Old Style"
SIZE_SCHOOL_NAME = 16
SIZE_EXAM_TITLE = 14
SIZE_BODY = 12
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

DOCX_MEDIA_TYPE = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)


class PandocNotFoundError(RuntimeError):
    """Raised when the pandoc binary is missing from PATH."""


def ensure_pandoc() -> None:
    if shutil.which("pandoc") is None:
        raise PandocNotFoundError(
            "pandoc is required to export DOCX with equations. "
            "Install pandoc and ensure it is on PATH."
        )


def _pandoc_markdown_to_document_xml(md_text: str) -> bytes:
    ensure_pandoc()
    try:
        result = subprocess.run(
            ["pandoc", "-f", "markdown", "-t", "docx", "-o", "-"],
            input=md_text.encode("utf-8"),
            capture_output=True,
            check=True,
        )
    except FileNotFoundError as exc:
        raise PandocNotFoundError(
            "pandoc is required to export DOCX with equations."
        ) from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or b"").decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"pandoc failed: {detail or exc}") from exc

    with zipfile.ZipFile(io.BytesIO(result.stdout)) as archive:
        return archive.read("word/document.xml")


def _etree_localname(element) -> str:
    from lxml import etree

    return etree.QName(element).localname


def _extract_first_paragraph_children(document_xml: bytes):
    root = parse_xml(document_xml)
    body = root.find(f"{{{W_NS}}}body")
    paragraph = body.find(f"{{{W_NS}}}p")
    if paragraph is None:
        return []
    return [
        child
        for child in paragraph
        if _etree_localname(child) != "pPr"
    ]


def _tighten_spacing(paragraph):
    pf = paragraph.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.line_spacing = 1.0
    return paragraph


def add_blank_line(doc):
    return _tighten_spacing(doc.add_paragraph())


def add_rich_paragraph(
    doc,
    text,
    bold=False,
    italic=False,
    size_pt=SIZE_BODY,
    alignment=None,
    font_name=FONT_NAME,
    indent_cm=None,
):
    paragraph = doc.add_paragraph()
    _tighten_spacing(paragraph)
    if alignment is not None:
        paragraph.alignment = alignment
    if indent_cm is not None:
        paragraph.paragraph_format.left_indent = docx.shared.Cm(indent_cm)

    if not text.strip():
        return paragraph

    md = prepare_markdown_for_pandoc(text)
    children = _extract_first_paragraph_children(
        _pandoc_markdown_to_document_xml(md)
    )
    for child in children:
        from lxml import etree

        tag = etree.QName(child).localname
        el = copy.deepcopy(child)
        if tag == "r":
            run_obj = Run(el, paragraph)
            run_obj.font.name = font_name
            run_obj.font.size = Pt(size_pt)
            run_obj.bold = bold
            run_obj.italic = italic
        paragraph._p.append(el)
    return paragraph


def add_rich_block(doc, text, **kwargs):
    if not text:
        return
    text = normalize_newlines(text)
    for line in re.split(r"\n+", text):
        line = line.strip()
        if line:
            add_rich_paragraph(doc, line, **kwargs)


def load_template(reference_docx: str | Path) -> docx.Document:
    doc = docx.Document(str(reference_docx))
    body = doc.element.body
    sect_pr = body.find(qn("w:sectPr"))
    for child in list(body):
        if child is not sect_pr:
            body.remove(child)
    return doc


def _insert_before_sectpr(doc, element):
    sect_pr = doc.element.body.find(qn("w:sectPr"))
    sect_pr.addprevious(element)


def clone_paragraphs(reference_docx: str | Path, doc, start: int, end: int):
    source_doc = docx.Document(str(reference_docx))
    for paragraph in source_doc.paragraphs[start:end]:
        _insert_before_sectpr(doc, copy.deepcopy(paragraph._p))


def find_paragraph_index(reference_docx: str | Path, predicate) -> int | None:
    source_doc = docx.Document(str(reference_docx))
    for i, paragraph in enumerate(source_doc.paragraphs):
        if predicate(paragraph.text):
            return i
    return None


def add_bottom_border(paragraph, size=12, color="000000"):
    p_pr = paragraph._p.get_or_add_pPr()
    p_bdr = parse_xml(
        f'<w:pBdr xmlns:w="{W_NS}">'
        f'<w:bottom w:val="single" w:sz="{size}" w:space="1" w:color="{color}"/>'
        f"</w:pBdr>"
    )
    p_pr.append(p_bdr)


def set_list_numbering(doc, paragraph, num_id: int, ilvl: int = 0):
    paragraph.style = doc.styles["List Paragraph"]
    p_pr = paragraph._p.get_or_add_pPr()
    num_pr = parse_xml(
        f'<w:numPr xmlns:w="{W_NS}">'
        f'<w:ilvl w:val="{ilvl}"/><w:numId w:val="{num_id}"/>'
        f"</w:numPr>"
    )
    p_pr.append(num_pr)


def format_option_label(raw_option: str, index: int) -> str:
    letter = "abcd"[index] if index < 4 else chr(ord("a") + index)
    stripped = re.sub(r"^\s*\(?[a-dA-D]\)?[.\)]\s*", "", raw_option).strip()
    return f"({letter}) {stripped}"


def header_from_question_paper(question_paper: Any) -> dict[str, Any]:
    if hasattr(question_paper, "subject"):
        get = lambda key: getattr(question_paper, key)
    else:
        get = lambda key: question_paper.get(key)
    return {
        "school_name": get("school_name"),
        "exam_title": get("exam_title"),
        "subject": get("subject"),
        "grade": get("grade"),
        "total_marks": get("total_marks"),
        "duration_minutes": get("duration_minutes"),
        "general_instructions": get("general_instructions") or [],
    }


def add_header_block(
    doc,
    header: dict,
    reference_docx: str | Path,
    title_suffix: str | None = None,
):
    name_line_idx = find_paragraph_index(
        reference_docx, lambda t: t.strip().upper().startswith("NAME:")
    )
    if name_line_idx is not None:
        clone_paragraphs(reference_docx, doc, 0, name_line_idx)
        if title_suffix:
            add_rich_paragraph(
                doc,
                title_suffix,
                bold=True,
                size_pt=SIZE_EXAM_TITLE,
                alignment=WD_ALIGN_PARAGRAPH.CENTER,
            )
    else:
        if header.get("school_name"):
            add_rich_paragraph(
                doc,
                header["school_name"],
                bold=True,
                size_pt=SIZE_SCHOOL_NAME,
                alignment=WD_ALIGN_PARAGRAPH.CENTER,
            )
        title = header.get("exam_title") or ""
        if title_suffix:
            title = f"{title} - {title_suffix}" if title else title_suffix
        if title:
            add_rich_paragraph(
                doc,
                title,
                bold=True,
                size_pt=SIZE_EXAM_TITLE,
                alignment=WD_ALIGN_PARAGRAPH.CENTER,
            )

    grade_line = (
        f"NAME: {'…' * 18}   ROLL NO: {'…' * 6}   GRADE: {header.get('grade', '')}"
    )
    add_rich_paragraph(doc, grade_line, bold=True, size_pt=SIZE_BODY)

    subject_line = add_rich_paragraph(
        doc,
        f"SUBJECT: {header.get('subject', '')}",
        bold=True,
        size_pt=SIZE_BODY,
    )
    add_bottom_border(subject_line)

    duration_txt = ""
    if header.get("duration_minutes"):
        hours = header["duration_minutes"] / 60
        duration_txt = f"DURATION: {hours:g} HOUR(S)"
    marks_line = add_rich_paragraph(
        doc,
        f"{duration_txt}          MAX MARKS: {header.get('total_marks', '')}",
        bold=True,
        size_pt=SIZE_BODY,
    )
    add_bottom_border(marks_line)

    if header.get("general_instructions"):
        add_rich_paragraph(doc, "General Instructions:", bold=True, size_pt=SIZE_BODY)
        add_rich_paragraph(
            doc,
            "Read the following instructions carefully and strictly follow them:",
            bold=True,
            size_pt=SIZE_BODY,
        )
        for instr in header["general_instructions"]:
            paragraph = add_rich_paragraph(doc, instr, size_pt=SIZE_BODY)
            set_list_numbering(doc, paragraph, num_id=1)
        add_blank_line(doc)


def add_section_header(
    doc,
    section_name: str,
    section_questions: list[dict],
    section_instructions: str | None = None,
):
    add_blank_line(doc)
    match = re.match(
        r"^Section\s+([A-Za-z0-9]+)$", section_name.strip(), flags=re.IGNORECASE
    )
    display_name = (
        f"SECTION \u2013 {match.group(1).upper()}" if match else section_name.upper()
    )
    add_rich_paragraph(
        doc,
        display_name,
        bold=True,
        size_pt=SIZE_BODY,
        alignment=WD_ALIGN_PARAGRAPH.CENTER,
    )
    add_blank_line(doc)

    if section_instructions and section_instructions.strip():
        add_rich_paragraph(
            doc,
            section_instructions.strip(),
            bold=True,
            size_pt=SIZE_BODY,
            alignment=WD_ALIGN_PARAGRAPH.CENTER,
        )
        return

    total = sum(q["marks"] for q in section_questions)
    marks_values = {q["marks"] for q in section_questions}
    if len(marks_values) == 1:
        each = marks_values.pop()
        scheme = f"{len(section_questions)}X{each:g}={total:g}M"
    else:
        scheme = f"{len(section_questions)} questions, {total:g}M total"
    add_rich_paragraph(
        doc,
        scheme,
        bold=True,
        size_pt=SIZE_BODY,
        alignment=WD_ALIGN_PARAGRAPH.CENTER,
    )


def add_question(doc, q: dict, case_study_number: int | None = None):
    if case_study_number is not None:
        add_rich_paragraph(
            doc,
            f"Case Study - {case_study_number}",
            bold=True,
            size_pt=SIZE_BODY,
            alignment=WD_ALIGN_PARAGRAPH.CENTER,
        )

    add_rich_block(
        doc, f"{q['question_number']}. {q['question_text']}", size_pt=SIZE_BODY
    )

    if q.get("options"):
        formatted = [
            format_option_label(opt, i) for i, opt in enumerate(q["options"])
        ]
        options_line = "      ".join(formatted)
        add_rich_paragraph(doc, options_line, size_pt=SIZE_BODY, indent_cm=0.5)

    if q.get("alternate_question_text"):
        add_rich_paragraph(
            doc,
            "(OR)",
            bold=True,
            size_pt=SIZE_BODY,
            alignment=WD_ALIGN_PARAGRAPH.CENTER,
        )
        add_rich_block(doc, q["alternate_question_text"], size_pt=SIZE_BODY)

    add_blank_line(doc)


def section_instructions_map(question_paper: Any) -> dict[str, str | None]:
    sections = getattr(question_paper, "sections", None)
    if sections is None and isinstance(question_paper, dict):
        sections = question_paper.get("sections", [])
    result: dict[str, str | None] = {}
    for section in sections or []:
        if isinstance(section, dict):
            name, instr = section.get("section_name"), section.get(
                "section_instructions"
            )
        else:
            name = getattr(section, "section_name", None)
            instr = getattr(section, "section_instructions", None)
        if name:
            result[name] = instr
    return result


def _build_question_paper_document(
    question_paper: Any,
    final_paper: dict,
    reference_docx: str | Path,
) -> docx.Document:
    doc = load_template(reference_docx)
    add_header_block(doc, header_from_question_paper(question_paper), reference_docx)

    instructions_by_section = section_instructions_map(question_paper)
    for section_name, questions in final_paper["sections"].items():
        add_section_header(
            doc,
            section_name,
            questions,
            instructions_by_section.get(section_name),
        )
        case_study_counter = 0
        for question in questions:
            case_study_number = None
            if question.get("question_type") == "CASE_STUDY":
                case_study_counter += 1
                case_study_number = case_study_counter
            add_question(doc, question, case_study_number=case_study_number)
    return doc


def _build_answer_key_document(
    question_paper: Any,
    final_answer_key: dict,
    reference_docx: str | Path,
) -> docx.Document:
    doc = load_template(reference_docx)
    add_header_block(
        doc,
        header_from_question_paper(question_paper),
        reference_docx,
        title_suffix="Answer Key",
    )

    for section_name, items in final_answer_key["sections"].items():
        add_blank_line(doc)
        add_rich_paragraph(
            doc,
            section_name.upper(),
            bold=True,
            size_pt=SIZE_BODY,
            alignment=WD_ALIGN_PARAGRAPH.CENTER,
        )
        for item in items:
            add_answer_item(doc, item)
    return doc


def add_answer_item(doc, item: dict):
    label = f"Q{item['question_number']}"
    meta_bits = [
        bit for bit in [item.get("chapter_name"), item.get("blooms_level")] if bit
    ]
    if meta_bits:
        label += "  (" + ", ".join(meta_bits) + ")"
    add_rich_paragraph(doc, label, bold=True, size_pt=SIZE_BODY)

    if item.get("status") and item["status"] != "ok":
        add_rich_paragraph(
            doc,
            f"[FLAGGED FOR REVIEW: {item['status']}]",
            bold=True,
            size_pt=SIZE_BODY,
        )

    if item.get("correct_option"):
        add_rich_paragraph(
            doc,
            f"Correct option: ({item['correct_option']})",
            size_pt=SIZE_BODY,
        )

    add_rich_paragraph(doc, "Answer:", italic=True, size_pt=SIZE_BODY)
    add_rich_block(doc, item.get("answer") or "", size_pt=SIZE_BODY, indent_cm=1)

    if item.get("marking_rubric"):
        add_rich_paragraph(doc, "Marking scheme:", italic=True, size_pt=SIZE_BODY)
        for step in item["marking_rubric"]:
            add_rich_paragraph(
                doc,
                f"- {step['description']} ({step['marks']:g} marks)",
                size_pt=SIZE_BODY,
                indent_cm=1,
            )

    if item.get("alternate_answer"):
        add_rich_paragraph(
            doc,
            "OR (alternate):",
            italic=True,
            size_pt=SIZE_BODY,
            alignment=WD_ALIGN_PARAGRAPH.CENTER,
        )
        add_rich_block(
            doc, item["alternate_answer"], size_pt=SIZE_BODY, indent_cm=1
        )

    add_blank_line(doc)


def _document_to_bytes(doc: docx.Document) -> bytes:
    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()


def build_question_paper_docx(
    question_paper: Any,
    final_paper: dict,
    reference_docx: str | Path,
    out_path: str | Path | None = None,
) -> Path | bytes:
    doc = _build_question_paper_document(question_paper, final_paper, reference_docx)
    if out_path is None:
        return _document_to_bytes(doc)
    path = Path(out_path)
    doc.save(str(path))
    return path


def build_answer_key_docx(
    question_paper: Any,
    final_answer_key: dict,
    reference_docx: str | Path,
    out_path: str | Path | None = None,
) -> Path | bytes:
    doc = _build_answer_key_document(
        question_paper, final_answer_key, reference_docx
    )
    if out_path is None:
        return _document_to_bytes(doc)
    path = Path(out_path)
    doc.save(str(path))
    return path


def render_question_paper_docx_bytes(
    question_paper: Any,
    final_paper: dict,
    reference_docx: str | Path,
) -> bytes:
    return build_question_paper_docx(
        question_paper, final_paper, reference_docx, out_path=None
    )


def render_answer_key_docx_bytes(
    question_paper: Any,
    final_answer_key: dict,
    reference_docx: str | Path,
) -> bytes:
    return build_answer_key_docx(
        question_paper, final_answer_key, reference_docx, out_path=None
    )


def export_question_paper_only(
    question_paper: Any,
    final_paper: dict,
    reference_docx: str | Path,
    paper_out: str | Path = "generated_question_paper.docx",
) -> Path:
    result = build_question_paper_docx(
        question_paper, final_paper, reference_docx, paper_out
    )
    assert isinstance(result, Path)
    return result


def export_question_paper_and_answer_key(
    question_paper: Any,
    final_paper: dict,
    final_answer_key: dict,
    reference_docx: str | Path,
    paper_out: str | Path = "generated_question_paper.docx",
    answer_key_out: str | Path = "generated_answer_key.docx",
) -> tuple[str, str]:
    build_question_paper_docx(question_paper, final_paper, reference_docx, paper_out)
    build_answer_key_docx(
        question_paper, final_answer_key, reference_docx, answer_key_out
    )
    return str(paper_out), str(answer_key_out)
