from pathlib import Path

from fastapi import APIRouter, HTTPException, status

from app.core.config import settings
from app.schemas.document import IngestRequest, IngestResponse
from app.services.ingestion.pipeline import ingest_directory

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/ingest", response_model=IngestResponse)
async def ingest_documents(request: IngestRequest) -> IngestResponse:
    source = Path(request.source_path)
    if not source.is_absolute():
        candidates = [
            settings.extracted_data_dir / source,
            settings.extracted_data_dir.parent / source,
            Path.cwd() / source,
        ]
        source = next((p for p in candidates if p.exists()), candidates[0])

    if not source.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Not found: {request.source_path}")

    try:
        return IngestResponse(**ingest_directory(source))
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
