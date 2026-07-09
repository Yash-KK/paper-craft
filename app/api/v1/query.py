from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_dense_embedder, get_response_generator, get_sparse_embedder, get_qdrant
from app.core.security import verify_api_key
from app.schemas.query import QueryRequest, QueryResponse
from app.services.llm.generator import ResponseGenerator

router = APIRouter(prefix="/query", tags=["query"])


@router.post("/", response_model=QueryResponse, dependencies=[Depends(verify_api_key)])
async def query_documents(
    request: QueryRequest,
    qdrant=Depends(get_qdrant),
    dense_embedder=Depends(get_dense_embedder),
    sparse_embedder=Depends(get_sparse_embedder),
    generator: ResponseGenerator = Depends(get_response_generator),
) -> QueryResponse:
    """Hybrid search + LLM answer generation (retrieval wiring to be expanded)."""
    _ = (qdrant, dense_embedder, sparse_embedder)
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Query endpoint scaffolded; hybrid retrieval not yet wired.",
    )
