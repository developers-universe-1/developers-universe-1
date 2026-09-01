"""Retrieval and prompt construction: embed query, pgvector cosine search, cite sources."""

import vertexai
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel

from .config import settings

_initialized = False


def init_vertex() -> None:
    """Initialize the Vertex AI SDK once per process."""
    global _initialized
    if not _initialized:
        vertexai.init(project=settings.gcp_project, location=settings.gcp_region)
        _initialized = True


def embed_texts(texts: list[str], task_type: str = "RETRIEVAL_DOCUMENT") -> list[list[float]]:
    """Embed a batch of texts with the configured Vertex AI embedding model."""
    init_vertex()
    model = TextEmbeddingModel.from_pretrained(settings.embedding_model)
    inputs = [TextEmbeddingInput(text=t, task_type=task_type) for t in texts]
    return [e.values for e in model.get_embeddings(inputs)]


def retrieve(conn, question: str, top_k: int | None = None) -> list[dict]:
    """Cosine-similarity search over pgvector. Returns chunks with source metadata."""
    k = top_k or settings.top_k
    query_vec = embed_texts([question], task_type="RETRIEVAL_QUERY")[0]
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT content, source, 1 - (embedding <=> %s::vector) AS score
            FROM documents
            ORDER BY embedding <=> %s::vector
            LIMIT %s
            """,
            (query_vec, query_vec, k),
        )
        rows = cur.fetchall()
    return [
        {"rank": i + 1, "content": content, "source": source, "score": round(float(score), 4)}
        for i, (content, source, score) in enumerate(rows)
    ]


def build_prompt(question: str, chunks: list[dict]) -> str:
    """Grounded-answer prompt with numbered sources the model must cite."""
    context = "\n\n".join(
        f"[{c['rank']}] (source: {c['source']})\n{c['content']}" for c in chunks
    )
    return f"""You are a customer support agent for our B2B SaaS product.
Answer the question using ONLY the context below. If the context does not contain
the answer, say you don't know and suggest contacting support@example.com.
Cite every claim with the source number in brackets, e.g. [1], [2].

Context:
{context}

Question: {question}

Answer:"""
