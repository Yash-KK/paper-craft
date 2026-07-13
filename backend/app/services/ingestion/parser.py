import re
from pathlib import Path

from app.core.config import settings

PAGE_BREAK_RE = re.compile(r"<!--\s*page break\s*-->", re.IGNORECASE)
EXAMPLE_RE = re.compile(r"\*\*Example\s*(\d+)")
EXERCISE_RE = re.compile(r"^#{1,4}\s*EXERCISE\s+(\d+\.\d+)", re.MULTILINE)
HEADING_RE = re.compile(r"^# (.+)$", re.MULTILINE)

IMAGE_LINK_LINE_RE = re.compile(r"^\[[^\]]*\]\(images/[^)]+\)\s*$", re.MULTILINE)
TABLE_LINK_LINE_RE = re.compile(r"^\[[^\]]*\]\(tables/[^)]+\)\s*$", re.MULTILINE)

BOILERPLATE_LINES = {"Reprint 2026-27", "---"}
FILENAME_RE = re.compile(r"^([a-z]+\d)(\d{2})$")
PAGE_ASSET_RE = re.compile(r"^page_(\d+)_(image|table)_(\d+)\.md$")


def parse_filename(path: Path) -> tuple[str, int]:
    """Derive book_code and chapter_number from the NCERT filename convention."""
    stem = path.stem
    match = FILENAME_RE.match(stem)
    if not match:
        raise ValueError(
            f"Filename '{stem}' doesn't match expected NCERT convention "
            f"(e.g. 'jemh102' = book 'jemh1' + chapter '02')."
        )
    book_code, chapter_suffix = match.group(1), match.group(2)
    if book_code not in settings.ncert_book_config:
        raise ValueError(
            f"book_code '{book_code}' not found in NCERT_BOOK_CONFIG. Add it in config first."
        )
    return book_code, int(chapter_suffix)


def extract_chapter_name_and_number(full_text: str) -> tuple[str | None, int | None]:
    """Chapter name/number appear as standalone H1 headings near the top of the file."""
    chapter_name: str | None = None
    chapter_number: int | None = None
    for heading in HEADING_RE.findall(full_text):
        heading = heading.strip()
        if chapter_number is None and re.match(r"^\d+$", heading):
            chapter_number = int(heading)
            continue
        if chapter_name is None and heading.isupper():
            chapter_name = heading.title()
        if chapter_name and chapter_number:
            break
    return chapter_name, chapter_number


def clean_page_text(text: str) -> str:
    """Strip boilerplate and image/table reference lines from a page's text chunk."""
    lines = text.splitlines()
    cleaned = [line for line in lines if line.strip() not in BOILERPLATE_LINES]
    text = "\n".join(cleaned)
    text = IMAGE_LINK_LINE_RE.sub("", text)
    text = TABLE_LINK_LINE_RE.sub("", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_pages(full_text: str) -> list[tuple[int, str]]:
    """Split on <!-- page break --> delimiters. Pages are numbered from 1."""
    parts = PAGE_BREAK_RE.split(full_text)
    return [(index + 1, clean_page_text(part)) for index, part in enumerate(parts)]


def collect_page_assets(book_dir: Path) -> dict[int, dict[str, list[Path]]]:
    """
    Scan tables/ and images/ next to the chapter .md and group by page number.
    Returns: {page_num: {"image": [Path, ...], "table": [Path, ...]}}
    """
    assets: dict[int, dict[str, list[Path]]] = {}
    for subdir, kind in ((book_dir / "images", "image"), (book_dir / "tables", "table")):
        if not subdir.exists():
            continue
        for file_path in sorted(subdir.glob("*.md")):
            match = PAGE_ASSET_RE.match(file_path.name)
            if not match:
                continue
            page_num = int(match.group(1))
            assets.setdefault(page_num, {"image": [], "table": []})[kind].append(file_path)
    return assets
