from pathlib import Path

from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import FastEmbedSparse, QdrantVectorStore, RetrievalMode

from app.core.config import settings
from app.schemas.document import ChunkType
from app.services.ingestion.splitter import build_documents


def _chapter_md_files(root_dir: Path) -> list[Path]:
    if (root_dir / f"{root_dir.name}.md").exists():
        chapter_dirs = [root_dir]
    else:
        chapter_dirs = [p for p in sorted(root_dir.iterdir()) if p.is_dir()]
    return [md for d in chapter_dirs for md in d.glob("*.md")]


def ingest_directory(root_dir: Path) -> dict:
    md_files = _chapter_md_files(root_dir)
    if not md_files:
        raise FileNotFoundError(f"No chapter .md files found under {root_dir}")

    documents = [doc for path in md_files for doc in build_documents(path)]
    if not documents:
        raise ValueError(f"No chunks produced from {root_dir}")

    QdrantVectorStore.from_documents(
        documents,
        embedding=OpenAIEmbeddings(
            model=settings.aic_dense_embedding_model,
            api_key=settings.aic_api_key,
            base_url=settings.aic_base_url,
        ),
        sparse_embedding=FastEmbedSparse(model_name=settings.sparse_embedding_model),
        collection_name=settings.collection_name,
        retrieval_mode=RetrievalMode.HYBRID,
        url=settings.qdrant_url,
    )

    breakdown = {
        ChunkType.TEXT.value: sum(
            1 for d in documents if d.metadata.get("chunk_type") == ChunkType.TEXT.value
        ),
        ChunkType.IMAGE.value: sum(
            1 for d in documents if d.metadata.get("chunk_type") == ChunkType.IMAGE.value
        ),
        ChunkType.TABLE.value: sum(
            1 for d in documents if d.metadata.get("chunk_type") == ChunkType.TABLE.value
        ),
    }
    return {
        "chapters_processed": len(md_files),
        "chunks_parsed": len(documents),
        "points_upserted": len(documents),
        "collection": settings.collection_name,
        "breakdown": breakdown,
    }
