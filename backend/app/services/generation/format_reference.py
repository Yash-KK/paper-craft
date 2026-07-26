from pathlib import Path

from app.core.config import PROJECT_ROOT

SAMPLES_DIR = PROJECT_ROOT / "samples"
DEFAULT_FORMAT_REFERENCE = SAMPLES_DIR / "40_marks_sample.docx"


def resolve_format_reference(path: Path | None = None) -> Path:
    """Return an existing DOCX path for paper formatting; default sample if none given."""
    candidate = path or DEFAULT_FORMAT_REFERENCE
    if not candidate.is_file():
        raise FileNotFoundError(
            f"Format reference DOCX not found: {candidate}. "
            f"Expected default at {DEFAULT_FORMAT_REFERENCE}"
        )
    if candidate.suffix.lower() != ".docx":
        raise ValueError("Format reference must be a .docx file")
    return candidate.resolve()
