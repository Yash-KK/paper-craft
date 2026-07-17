import enum

from pydantic import BaseModel, Field


class ChunkType(str, enum.Enum):
    TEXT = "text"
    IMAGE = "image"
    TABLE = "table"


class ContentType(str, enum.Enum):
    THEORY = "theory"
    EXAMPLE = "example"
    EXERCISE = "exercise"
    FIGURE = "figure"
    TABLE = "table"


class DocumentMetadata(BaseModel):
    book_code: str
    subject: str
    grade: int
    chapter_number: int
    chapter_name: str | None = None
    page_number: int
    chunk_id: str
    chunk_type: ChunkType
    content_type: ContentType
    source_file: str
    asset_file: str | None = None


class IngestRequest(BaseModel):
    """Path to a class directory or single chapter folder under extracted_data/."""

    source_path: str = Field(
        examples=["extracted_data/class_10"],
        description="Relative or absolute path to a class dir or chapter dir",
    )


class IngestResponse(BaseModel):
    chapters_processed: int
    chunks_parsed: int
    points_upserted: int
    collection: str
    breakdown: dict[str, int]
