from pathlib import Path
from typing import Any

from app.core.config import settings
from app.services.embeddings.openai import OpenAIDenseEmbedder
from app.services.embeddings.sparse import BM25SparseEmbedder
from app.services.ingestion.splitter import build_chunks
from app.services.vectorstore.client import get_qdrant_client
from app.services.vectorstore.operations import build_point, ensure_collection, upsert_points


def discover_chapter_md_files(root_dir: Path) -> list[Path]:
    """
    root_dir may be a class directory (jemh101/, jemh102/, ...) or a single chapter folder.
    """
    if (root_dir / f"{root_dir.name}.md").exists():
        chapter_dirs = [root_dir]
    else:
        chapter_dirs = [path for path in sorted(root_dir.iterdir()) if path.is_dir()]

    md_files: list[Path] = []
    for chapter_dir in chapter_dirs:
        md_files.extend(chapter_dir.glob("*.md"))
    return md_files


def parse_directory(root_dir: Path) -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []
    for path in discover_chapter_md_files(root_dir):
        chunks.extend(build_chunks(path))
    return chunks


def ingest_directory(root_dir: Path) -> dict[str, Any]:
    """
    End-to-end ingestion:
    NCERT markdown -> page-level chunks -> hybrid embeddings -> Qdrant upsert.
    """
    md_files = discover_chapter_md_files(root_dir)
    if not md_files:
        raise FileNotFoundError(f"No chapter .md files found under {root_dir}")

    all_chunks: list[dict[str, Any]] = []
    for path in md_files:
        all_chunks.extend(build_chunks(path))

    if not all_chunks:
        raise ValueError(f"No chunks produced from {root_dir}")

    dense_embedder = OpenAIDenseEmbedder()
    sparse_embedder = BM25SparseEmbedder()
    qdrant = get_qdrant_client()

    ensure_collection(qdrant)

    texts = [chunk["page_content"] for chunk in all_chunks]
    dense_vectors = dense_embedder.embed_documents(texts)
    sparse_vectors = sparse_embedder.embed_documents(texts)

    points = [
        build_point(chunk, dense_vector, sparse_vector)
        for chunk, dense_vector, sparse_vector in zip(
            all_chunks, dense_vectors, sparse_vectors, strict=True
        )
    ]
    upsert_points(qdrant, points)

    breakdown = {
        "text": sum(1 for c in all_chunks if c["metadata"]["chunk_type"] == "text"),
        "image": sum(1 for c in all_chunks if c["metadata"]["chunk_type"] == "image"),
        "table": sum(1 for c in all_chunks if c["metadata"]["chunk_type"] == "table"),
    }

    return {
        "chapters_processed": len(md_files),
        "chunks_parsed": len(all_chunks),
        "points_upserted": len(points),
        "collection": settings.collection_name,
        "breakdown": breakdown,
    }
