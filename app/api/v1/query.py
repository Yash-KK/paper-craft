from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_vector_store
from app.core.security import verify_api_key
from app.schemas.query import QueryRequest, QueryResponse
from app.services.llm.generator import ResponseGenerator

router = APIRouter(prefix="/query", tags=["query"])


@router.post("/", response_model=QueryResponse, dependencies=[Depends(verify_api_key)])
async def query_documents(
    request: QueryRequest,
    vector_store=Depends(get_vector_store),
) -> QueryResponse:
    _ = (request, vector_store, ResponseGenerator())
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Query endpoint not yet wired.",
    )
