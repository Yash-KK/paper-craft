import re
import subprocess
from pathlib import Path

IMG_PLACEHOLDER_RE = re.compile(r"!\[[^\]]*\]\([^)]*\)(\{[^}]*\})?")

SAMPLE_TEXT_MAX_CHARS = 10_000


def parse_docx(path: Path) -> tuple[str, int]:
    """Convert a .docx to markdown via pandoc; replace image embeds with placeholders."""
    result = subprocess.run(
        ["pandoc", "-t", "markdown", str(path)],
        capture_output=True,
        text=True,
        check=True,
    )
    md = result.stdout
    image_count = len(IMG_PLACEHOLDER_RE.findall(md))
    cleaned = IMG_PLACEHOLDER_RE.sub("[IMAGE - content not extracted]", md)
    return cleaned, image_count


def truncate_sample_text(text: str, max_chars: int = SAMPLE_TEXT_MAX_CHARS) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n[... truncated ...]"
