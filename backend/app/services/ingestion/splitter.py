from pathlib import Path

from langchain_core.documents import Document

from app.core.config import settings
from app.services.ingestion.parser import (
    EXAMPLE_RE,
    EXERCISE_RE,
    collect_page_assets,
    extract_chapter_name_and_number,
    parse_filename,
    split_pages,
)


def build_documents(path: Path) -> list[Document]:
    book_code, chapter_number = parse_filename(path)
    book_meta = settings.ncert_book_config[book_code]
    book_dir = path.parent
    full_text = path.read_text(encoding="utf-8")
    chapter_name, _ = extract_chapter_name_and_number(full_text)
    page_assets = collect_page_assets(book_dir)

    def meta(page_num: int, **extra) -> dict:
        return {
            "book_code": book_code,
            "subject": book_meta["subject"],
            "grade": book_meta["grade"],
            "chapter_number": chapter_number,
            "chapter_name": chapter_name,
            "page_number": page_num,
            "source_file": path.name,
            **extra,
        }

    documents: list[Document] = []
    for page_num, content in split_pages(full_text):
        if content:
            documents.append(
                Document(
                    page_content=content,
                    metadata=meta(
                        page_num,
                        chunk_id=f"{book_code}_ch{chapter_number}_pg{page_num}_text",
                        chunk_type="text",
                        content_types=["theory"]
                        + (["example"] if EXAMPLE_RE.search(content) else [])
                        + (["exercise"] if EXERCISE_RE.search(content) else []),
                    ),
                )
            )

        for idx, image_path in enumerate(
            page_assets.get(page_num, {}).get("image", []), start=1
        ):
            text = image_path.read_text(encoding="utf-8").strip()
            if text:
                documents.append(
                    Document(
                        page_content=text,
                        metadata=meta(
                            page_num,
                            chunk_id=f"{book_code}_ch{chapter_number}_pg{page_num}_img{idx}",
                            chunk_type="image",
                            content_types=["figure"],
                            asset_file=str(image_path.relative_to(book_dir)),
                        ),
                    )
                )

        for idx, table_path in enumerate(
            page_assets.get(page_num, {}).get("table", []), start=1
        ):
            text = table_path.read_text(encoding="utf-8").strip()
            if text:
                documents.append(
                    Document(
                        page_content=text,
                        metadata=meta(
                            page_num,
                            chunk_id=f"{book_code}_ch{chapter_number}_pg{page_num}_tbl{idx}",
                            chunk_type="table",
                            content_types=["table"],
                            asset_file=str(table_path.relative_to(book_dir)),
                        ),
                    )
                )

    return documents
