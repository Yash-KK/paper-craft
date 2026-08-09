"""Extract NCERT chapter PDFs to markdown via Mistral OCR + Pixtral."""

from __future__ import annotations

import argparse
import base64
import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv
from mistralai.client import Mistral

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

IMAGE_DESCRIPTION_PROMPT = """\
You are describing figures from a school textbook.

Describe this image in detail. Return markdown with these sections:
- **Figure Type** (diagram, graph, photo, illustration, etc.)
- **Description**
- **Text in Image** (transcribe any visible text)
- **Key Information** (labels, values, relationships)

If it is a graph, explain the axes and trends.
If it is a diagram, explain the relationships between parts.
If it is a table, describe the rows and columns.

Do not hallucinate. Only describe what is visible."""


def describe_image(client: Mistral, image_base64: str) -> str:
    response = client.chat.complete(
        model="pixtral-12b-latest",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": IMAGE_DESCRIPTION_PROMPT},
                    {"type": "image_url", "image_url": image_base64},
                ],
            }
        ],
    )
    return response.choices[0].message.content


def save_extraction(
    ocr_response, output_dir: Path, book_id: str, client: Mistral
) -> Path:
    output_dir = Path(output_dir)
    tables_dir = output_dir / "tables"
    images_dir = output_dir / "images"
    tables_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)

    for old_image in images_dir.glob("*"):
        if old_image.suffix.lower() in {".jpeg", ".jpg", ".png", ".gif", ".webp"}:
            old_image.unlink()

    page_markdowns: list[str] = []

    for page in ocr_response.pages:
        page_num = page.index + 1
        markdown = page.markdown or ""

        for image_idx, image in enumerate(page.images or [], start=1):
            filename = f"page_{page_num}_image_{image_idx}.md"
            image_path = images_dir / filename
            rel_path = f"images/{filename}"

            if image.image_base64:
                description = describe_image(client, image.image_base64)
                image_path.write_text(description.strip() + "\n", encoding="utf-8")
                print(f"  described {filename}", flush=True)

            markdown = re.sub(
                rf"!\[[^\]]*\]\({re.escape(image.id)}\)",
                f"[Figure {image_idx}]({rel_path})",
                markdown,
            )
            markdown = markdown.replace(f"]({image.id})", f"]({rel_path})")

        for table_idx, table in enumerate(page.tables or [], start=1):
            filename = f"page_{page_num}_table_{table_idx}.md"
            table_path = tables_dir / filename
            table_path.write_text(table.content or "", encoding="utf-8")

            rel_path = f"tables/{filename}"
            markdown = markdown.replace(f"]({table.id})", f"]({rel_path})")
            markdown = re.sub(
                rf"\[{re.escape(table.id)}\]\({re.escape(table.id)}\)",
                f"[Table {table_idx}]({rel_path})",
                markdown,
            )

        page_markdowns.append(markdown.strip())

    full_markdown = "\n\n<!-- page break -->\n\n".join(page_markdowns)
    main_md_path = output_dir / f"{book_id}.md"
    main_md_path.write_text(full_markdown + "\n", encoding="utf-8")

    print(f"Saved {main_md_path}", flush=True)
    print(f"  tables: {len(list(tables_dir.glob('*.md')))} files", flush=True)
    print(f"  images: {len(list(images_dir.glob('*.md')))} files", flush=True)
    return main_md_path


def extract_pdf(client: Mistral, book_id: str) -> Path:
    pdf_path = PROJECT_ROOT / "data/class-10/textbooks" / f"{book_id}.pdf"
    output_dir = PROJECT_ROOT / "extracted_data/class_10" / book_id

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    print(f"\n=== Extracting {book_id} from {pdf_path} ===", flush=True)
    with pdf_path.open("rb") as f:
        pdf_b64 = base64.b64encode(f.read()).decode()

    print("Running OCR...", flush=True)
    ocr_response = client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "document_url",
            "document_url": f"data:application/pdf;base64,{pdf_b64}",
        },
        include_image_base64=True,
        table_format="markdown",
    )
    print(f"OCR complete: {len(ocr_response.pages)} pages", flush=True)
    return save_extraction(ocr_response, output_dir, book_id, client)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "book_ids",
        nargs="+",
        help="Book IDs to extract, e.g. jemh103 jemh104 jemh105",
    )
    args = parser.parse_args()

    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        print("MISTRAL_API_KEY not set", file=sys.stderr)
        return 1

    client = Mistral(api_key=api_key)
    for book_id in args.book_ids:
        extract_pdf(client, book_id)
    print("\nAll extractions complete.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
