"""Format-reference helpers — thin wrappers over the document store."""

from pathlib import Path

from app.core.config import PROJECT_ROOT
from app.services.documents import (
    DEFAULT_FORMAT_REFERENCE_URI,
    resolve_document,
    to_file_uri,
    to_local_uri,
)

DEFAULT_FORMAT_REFERENCE = PROJECT_ROOT / "samples" / "40_marks_sample.docx"


def resolve_format_reference(uri_or_path: str | Path | None = None) -> Path:
    """Resolve a format-reference URI or local path to an existing DOCX file."""
    if uri_or_path is None:
        return resolve_document(None)
    if isinstance(uri_or_path, Path):
        return resolve_document(to_file_uri(uri_or_path))
    return resolve_document(uri_or_path)


__all__ = [
    "DEFAULT_FORMAT_REFERENCE",
    "DEFAULT_FORMAT_REFERENCE_URI",
    "resolve_format_reference",
    "to_file_uri",
    "to_local_uri",
]
