"""Resolve document URIs to local paths for reading.

Supported schemes:
- ``local:<relative-path>`` — file under the project root (default for samples)
- ``file:<absolute-path>`` — absolute filesystem path (e.g. teacher uploads)
- bare relative path — treated as ``local:``
- absolute filesystem path — treated as ``file:``

Future: ``s3://bucket/key`` can download into a temp file and return that path
without changing callers of ``resolve_document``.
"""

from __future__ import annotations

from pathlib import Path
from urllib.parse import unquote, urlparse

from app.core.config import PROJECT_ROOT

DEFAULT_FORMAT_REFERENCE_URI = "local:samples/40_marks_sample.docx"


def to_local_uri(relative_path: str) -> str:
    return f"local:{relative_path.lstrip('/')}"


def to_file_uri(path: Path) -> str:
    return path.resolve().as_uri()


def resolve_document(uri: str | None = None) -> Path:
    """Materialize a document URI to an existing local .docx path."""
    ref = (uri or DEFAULT_FORMAT_REFERENCE_URI).strip()
    if not ref:
        ref = DEFAULT_FORMAT_REFERENCE_URI

    path = _uri_to_path(ref)
    if not path.is_file():
        raise FileNotFoundError(f"Document not found for URI {ref!r} → {path}")
    if path.suffix.lower() != ".docx":
        raise ValueError("Document must be a .docx file")
    return path.resolve()


def _uri_to_path(uri: str) -> Path:
    if uri.startswith("local:"):
        return PROJECT_ROOT / uri.removeprefix("local:")

    if uri.startswith("s3://"):
        raise NotImplementedError(
            "S3 document resolution is not configured yet. "
            "Store samples under local: for now, or upload a DOCX at generate time."
        )

    if uri.startswith("file:"):
        parsed = urlparse(uri)
        return Path(unquote(parsed.path))

    candidate = Path(uri)
    if candidate.is_absolute():
        return candidate
    return PROJECT_ROOT / uri
