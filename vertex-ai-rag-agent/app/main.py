"""FastAPI service: /chat (RAG over pgvector + Gemini) and /healthz."""

import logging
import time
from contextlib import asynccontextmanager

import anyio
import psycopg
import vertexai
from fastapi import FastAPI, HTTPException
from psycopg_pool import ConnectionPool
from pydantic import BaseModel, Field
from vertexai.generative_models import GenerationConfig, GenerativeModel

from .audit import Trace, ensure_audit_table, write_trace
from .config import settings
from .rag import build_prompt, retrieve

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("rag-agent")

pool: ConnectionPool | None = None
model: GenerativeModel | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global pool, model
    vertexai.init(project=settings.gcp_project, location=settings.gcp_region)
    pool = ConnectionPool(settings.db_dsn, min_size=1, max_size=10, kwargs={"autocommit": True})
    model = GenerativeModel(settings.gemini_model)
    with pool.connection() as conn:
        ensure_audit_table(conn)
    yield
    pool.close()


app = FastAPI(title="vertex-ai-rag-agent", lifespan=lifespan)


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    top_k: int | None = Field(default=None, ge=1, le=20)


class Source(BaseModel):
    rank: int
    source: str
    score: float


class TokenUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]
    latency_ms: dict
    token_usage: TokenUsage
    trace_id: str  # audit trail lookup key — every answer is reconstructable


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}


def _generate(prompt: str):
    return model.generate_content(
        prompt,
        generation_config=GenerationConfig(
            temperature=settings.temperature,
            max_output_tokens=settings.max_output_tokens,
        ),
    )


async def _write_trace(trace: Trace) -> None:
    """Persist the audit trail. Tracing must never fail a customer request."""
    try:
        assert pool is not None
        with pool.connection() as conn:
            await anyio.to_thread.run_sync(
                write_trace, conn, trace, settings.gemini_model, settings.embedding_model
            )
    except Exception:
        log.exception("failed to write chat trace %s", trace.trace_id)


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    t0 = time.perf_counter()
    assert pool is not None and model is not None

    try:
        with pool.connection() as conn:
            chunks = await anyio.to_thread.run_sync(retrieve, conn, req.question, req.top_k)
    except psycopg.Error as e:
        log.error("retrieval failed: %s", e)
        raise HTTPException(status_code=503, detail="retrieval backend unavailable")

    t_retrieval = time.perf_counter()
    if not chunks:
        answer = "I don't have any documents to answer from. Please contact support@example.com."
        latency = {"retrieval": round((t_retrieval - t0) * 1000, 1), "generation": 0.0, "total": round((t_retrieval - t0) * 1000, 1)}
        tokens = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        trace = Trace(
            question=req.question, answer=answer, status="no_context",
            chunks=[], latency_ms=latency, token_usage=tokens,
        )
        await _write_trace(trace)
        return ChatResponse(
            answer=answer,
            sources=[],
            latency_ms=latency,
            token_usage=TokenUsage(**tokens),
            trace_id=trace.trace_id,
        )

    prompt = build_prompt(req.question, chunks)
    try:
        resp = await anyio.to_thread.run_sync(_generate, prompt)
    except Exception as e:
        log.error("generation failed: %s", e)
        raise HTTPException(status_code=502, detail="generation backend unavailable")

    t_generation = time.perf_counter()
    usage = resp.usage_metadata
    latency = {
        "retrieval": round((t_retrieval - t0) * 1000, 1),
        "generation": round((t_generation - t_retrieval) * 1000, 1),
        "total": round((t_generation - t0) * 1000, 1),
    }
    tokens = {
        "prompt_tokens": usage.prompt_token_count,
        "completion_tokens": usage.candidates_token_count,
        "total_tokens": usage.total_token_count,
    }
    trace = Trace(
        question=req.question, answer=resp.text, status="ok",
        chunks=chunks, latency_ms=latency, token_usage=tokens,
    )
    await _write_trace(trace)
    # Structured log line: one per request, feeds latency/cost dashboards.
    log.info(
        "chat trace_id=%s top_k=%d retrieval_ms=%.1f generation_ms=%.1f total_ms=%.1f "
        "prompt_tokens=%d completion_tokens=%d citations_ok=%s",
        trace.trace_id,
        len(chunks), latency["retrieval"], latency["generation"], latency["total"],
        tokens["prompt_tokens"], tokens["completion_tokens"], trace.citations_ok,
    )
    return ChatResponse(
        answer=resp.text,
        sources=[Source(rank=c["rank"], source=c["source"], score=c["score"]) for c in chunks],
        latency_ms=latency,
        token_usage=TokenUsage(**tokens),
        trace_id=trace.trace_id,
    )
