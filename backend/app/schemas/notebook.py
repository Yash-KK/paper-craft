from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class NotebookChapterCreate(BaseModel):
    book_code: str = Field(max_length=50)
    chapter_number: int
    chapter_name: str = Field(max_length=255)
    subject: str | None = Field(default=None, max_length=100)
    grade: str | None = Field(default=None, max_length=50)
    enabled: bool = True


class NotebookChapterUpdate(BaseModel):
    book_code: str | None = Field(default=None, max_length=50)
    chapter_number: int | None = None
    chapter_name: str | None = Field(default=None, max_length=255)
    subject: str | None = Field(default=None, max_length=100)
    grade: str | None = Field(default=None, max_length=50)
    enabled: bool | None = None


class NotebookChapterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    notebook_id: UUID
    book_code: str
    chapter_number: int
    chapter_name: str
    subject: str | None = None
    grade: str | None = None
    enabled: bool
    created_at: datetime


class NotebookCreate(BaseModel):
    name: str = Field(max_length=255)
    class_grade: str | None = Field(default=None, max_length=50)
    subject: str | None = Field(default=None, max_length=100)
    color_hex: str | None = Field(default=None, max_length=10)
    chapters: list[NotebookChapterCreate] = Field(default_factory=list)


class NotebookUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    class_grade: str | None = Field(default=None, max_length=50)
    subject: str | None = Field(default=None, max_length=100)
    color_hex: str | None = Field(default=None, max_length=10)


class NotebookResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    name: str
    class_grade: str | None = None
    subject: str | None = None
    color_hex: str | None = None
    created_at: datetime
    updated_at: datetime
    chapters: list[NotebookChapterResponse] = Field(default_factory=list)
