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
        return ChatResponse(
            answer="I don't have any documents to answer from. Please contact support@example.com.",
            sources=[],
            latency_ms={"retrieval": round((t_retrieval - t0) * 1000, 1), "generation": 0.0, "total": round((t_retrieval - t0) * 1000, 1)},
            token_usage=TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
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
    # Structured log line: one per request, feeds latency/cost dashboards.
    log.info(
        "chat top_k=%d retrieval_ms=%.1f generation_ms=%.1f total_ms=%.1f "
        "prompt_tokens=%d completion_tokens=%d",
        len(chunks), latency["retrieval"], latency["generation"], latency["total"],
        usage.prompt_token_count, usage.candidates_token_count,
    )
    return ChatResponse(
        answer=resp.text,
        sources=[Source(rank=c["rank"], source=c["source"], score=c["score"]) for c in chunks],
        latency_ms=latency,
        token_usage=TokenUsage(
            prompt_tokens=usage.prompt_token_count,
            completion_tokens=usage.candidates_token_count,
            total_tokens=usage.total_token_count,
        ),
    )
