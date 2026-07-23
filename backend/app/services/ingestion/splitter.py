from pathlib import Path

from langchain_core.documents import Document

from app.core.config import settings
from app.schemas.document import ChunkType, ContentType, DocumentMetadata
from app.services.ingestion.parser import (
    EXAMPLE_RE,
    EXERCISE_RE,
    collect_page_assets,
    extract_chapter_name_and_number,
    parse_filename,
    split_pages,
)


def _text_content_type(content: str) -> ContentType:
    if EXERCISE_RE.search(content):
        return ContentType.EXERCISE
    if EXAMPLE_RE.search(content):
        return ContentType.EXAMPLE
    return ContentType.THEORY


def build_documents(path: Path) -> list[Document]:
    book_code, chapter_number = parse_filename(path)
    book_meta = settings.ncert_book_config[book_code]
    book_dir = path.parent
    full_text = path.read_text(encoding="utf-8")
    chapter_name, _ = extract_chapter_name_and_number(full_text)
    page_assets = collect_page_assets(book_dir)

    def meta(page_num: int, **extra) -> dict:
        metadata = DocumentMetadata(
            book_code=book_code.lower(),
            board=str(book_meta.get("board", "CBSE")).strip().upper(),
            subject=str(book_meta["subject"]).strip().lower(),
            grade=int(book_meta["grade"]),
            chapter_number=int(chapter_number),
            chapter_name=chapter_name.lower() if chapter_name else None,
            page_number=int(page_num),
            source_file=path.name.lower(),
            **extra,
        )
        return metadata.model_dump(mode="json", exclude_none=True)

    documents: list[Document] = []
    for page_num, content in split_pages(full_text):
        if content:
            documents.append(
                Document(
                    page_content=content,
                    metadata=meta(
                        page_num,
                        chunk_id=f"{book_code}_ch{chapter_number}_pg{page_num}_text",
                        chunk_type=ChunkType.TEXT,
                        content_type=_text_content_type(content),
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
                            chunk_type=ChunkType.IMAGE,
                            content_type=ContentType.FIGURE,
                            asset_file=image_path.relative_to(book_dir)
                            .as_posix()
                            .lower(),
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
                            chunk_type=ChunkType.TABLE,
                            content_type=ContentType.TABLE,
                            asset_file=table_path.relative_to(book_dir)
                            .as_posix()
                            .lower(),
                        ),
                    )
                )

    return documents
