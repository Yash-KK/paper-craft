from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_qdrant
from app.core.config import settings
from app.core.security import verify_api_key
from app.schemas.document import IngestRequest, IngestResponse
from app.services.ingestion.pipeline import ingest_directory

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/ingest", response_model=IngestResponse, dependencies=[Depends(verify_api_key)])
async def ingest_documents(request: IngestRequest) -> IngestResponse:
    """
    Ingest extracted NCERT markdown into Qdrant.

    Accepts a path to either:
    - a class directory: extracted_data/class_10/
    - a single chapter:   extracted_data/class_10/jemh101/
    """
    source = Path(request.source_path)
    if not source.is_absolute():
        candidates = [
            settings.extracted_data_dir / source,
            settings.extracted_data_dir.parent / source,
            Path.cwd() / source,
        ]
        source = next((path for path in candidates if path.exists()), candidates[0])

    if not source.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source path not found: {request.source_path}",
        )

    try:
        result = ingest_directory(source)
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    _ = get_qdrant()  # ensure client is initialisable
    return IngestResponse(**result)
