"""Ingestion CLI: load .md/.txt docs from a folder, chunk, embed, upsert into pgvector.

Usage:
    python -m app.ingest ./docs_corpus
    python -m app.ingest ./docs_corpus --recreate
"""

import argparse
import logging
from pathlib import Path

import psycopg
from pgvector.psycopg import register_vector

from .config import settings
from .rag import embed_texts

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("ingest")

BATCH_SIZE = 100  # well under the embedding API's per-request limit


def chunk_text(text: str, size: int, overlap: int) -> list[str]:
    """Sliding-window character chunking; simple and predictable for support docs."""
    chunks, start = [], 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end].strip())
        start += size - overlap
    return [c for c in chunks if c]


def load_documents(folder: Path) -> list[dict]:
    docs = []
    for path in sorted(folder.rglob("*")):
        if path.suffix not in {".md", ".txt"}:
            continue
        text = path.read_text(encoding="utf-8")
        for i, chunk in enumerate(chunk_text(text, settings.chunk_size, settings.chunk_overlap)):
            docs.append({"source": str(path.relative_to(folder)), "chunk_index": i, "content": chunk})
    return docs


def ensure_schema(conn, recreate: bool) -> None:
    with conn.cursor() as cur:
        if recreate:
            cur.execute("DROP TABLE IF EXISTS documents")
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS documents (
                id          BIGSERIAL PRIMARY KEY,
                source      TEXT NOT NULL,
                chunk_index INT NOT NULL,
                content     TEXT NOT NULL,
                embedding   vector({settings.embedding_dims}),
                UNIQUE (source, chunk_index)
            )
            """
        )
        # HNSW index: sub-100ms p95 at our corpus sizes; add only for larger corpora.
        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS documents_embedding_hnsw
            ON documents USING hnsw (embedding vector_cosine_ops)
            """
        )
    conn.commit()


def upsert_documents(conn, docs: list[dict]) -> None:
    log.info("embedding %d chunks in batches of %d", len(docs), BATCH_SIZE)
    for i in range(0, len(docs), BATCH_SIZE):
        batch = docs[i : i + BATCH_SIZE]
        vectors = embed_texts([d["content"] for d in batch])
        with conn.cursor() as cur:
            for doc, vec in zip(batch, vectors):
                cur.execute(
                    """
                    INSERT INTO documents (source, chunk_index, content, embedding)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (source, chunk_index)
                    DO UPDATE SET content = EXCLUDED.content, embedding = EXCLUDED.embedding
                    """,
                    (doc["source"], doc["chunk_index"], doc["content"], vec),
                )
        conn.commit()
        log.info("upserted %d/%d chunks", min(i + BATCH_SIZE, len(docs)), len(docs))


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest docs into pgvector.")
    parser.add_argument("folder", type=Path, help="folder containing .md/.txt docs")
    parser.add_argument("--recreate", action="store_true", help="drop and recreate the table")
    args = parser.parse_args()

    if not args.folder.is_dir():
        raise SystemExit(f"not a directory: {args.folder}")

    docs = load_documents(args.folder)
    if not docs:
        raise SystemExit(f"no .md/.txt documents found under {args.folder}")
    log.info("loaded %d chunks from %s", len(docs), args.folder)

    with psycopg.connect(settings.db_dsn) as conn:
        ensure_schema(conn, args.recreate)
        register_vector(conn)
        upsert_documents(conn, docs)
    log.info("done")


if __name__ == "__main__":
    main()
