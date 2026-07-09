from pathlib import Path
from typing import Any

from app.core.config import settings
from app.services.ingestion.parser import (
    EXAMPLE_RE,
    EXERCISE_RE,
    collect_page_assets,
    extract_chapter_name_and_number,
    parse_filename,
    split_pages,
)


def build_chunks(path: Path) -> list[dict[str, Any]]:
    """
    Parse a chapter's Mistral-OCR .md (plus sibling tables/ and images/) into
    page-level chunks: one text chunk per page, plus image/table asset chunks.
    """
    book_code, chapter_number_from_filename = parse_filename(path)
    book_meta = settings.ncert_book_config[book_code]
    book_dir = path.parent

    full_text = path.read_text(encoding="utf-8")
    chapter_name, chapter_number_from_heading = extract_chapter_name_and_number(full_text)

    chapter_number = chapter_number_from_filename
    page_assets = collect_page_assets(book_dir)

    def base_metadata(page_num: int) -> dict[str, Any]:
        return {
            "book_code": book_code,
            "subject": book_meta["subject"],
            "grade": book_meta["grade"],
            "chapter_number": chapter_number,
            "chapter_name": chapter_name,
            "page_number": page_num,
            "source_file": path.name,
        }

    chunks: list[dict[str, Any]] = []
    for page_num, content in split_pages(full_text):
        if content:
            example_refs = sorted({int(value) for value in EXAMPLE_RE.findall(content)})
            exercise_refs = sorted(set(EXERCISE_RE.findall(content)))
            content_types = ["theory"]
            if example_refs:
                content_types.append("example")
            if exercise_refs:
                content_types.append("exercise")

            chunks.append(
                {
                    "chunk_id": f"{book_code}_ch{chapter_number}_pg{page_num}_text",
                    "page_content": content,
                    "metadata": {
                        **base_metadata(page_num),
                        "chunk_type": "text",
                        "content_types": content_types,
                        "example_refs": example_refs,
                        "exercise_refs": exercise_refs,
                    },
                }
            )

        for idx, image_path in enumerate(
            page_assets.get(page_num, {}).get("image", []), start=1
        ):
            image_text = image_path.read_text(encoding="utf-8").strip()
            if not image_text:
                continue
            chunks.append(
                {
                    "chunk_id": f"{book_code}_ch{chapter_number}_pg{page_num}_img{idx}",
                    "page_content": image_text,
                    "metadata": {
                        **base_metadata(page_num),
                        "chunk_type": "image",
                        "content_types": ["figure"],
                        "asset_file": str(image_path.relative_to(book_dir)),
                    },
                }
            )

        for idx, table_path in enumerate(
            page_assets.get(page_num, {}).get("table", []), start=1
        ):
            table_text = table_path.read_text(encoding="utf-8").strip()
            if not table_text:
                continue
            chunks.append(
                {
                    "chunk_id": f"{book_code}_ch{chapter_number}_pg{page_num}_tbl{idx}",
                    "page_content": table_text,
                    "metadata": {
                        **base_metadata(page_num),
                        "chunk_type": "table",
                        "content_types": ["table"],
                        "asset_file": str(table_path.relative_to(book_dir)),
                    },
                }
            )

    return chunks
