from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(min_length=1)
    grade: int | None = None
    subject: str | None = None
    top_k: int = Field(default=5, ge=1, le=20)


class RetrievedChunk(BaseModel):
    chunk_id: str
    page_content: str
    score: float
    metadata: dict


class QueryResponse(BaseModel):
    answer: str
    sources: list[RetrievedChunk] = Field(default_factory=list)
