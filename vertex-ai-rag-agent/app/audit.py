"""Audit trail: one structured trace row per /chat request, written to Postgres.

If you can't show a reviewer what the agent did, they won't trust it. Every
answered (or refused) request lands in chat_traces with enough context to
reconstruct the decision: which prompt and model versions produced it, which
sources were retrieved, what it cost, and whether its citations checked out.

Questions and answers are stored as SHA-256 hashes, not text — the same
input-hash posture as our production audit logging. The trace proves the
pipeline behaved; it doesn't become a second copy of customer conversations.
"""

import hashlib
import json
import re
import uuid
from dataclasses import dataclass, field

from .rag import PROMPT_VERSION

CITATION_RE = re.compile(r"\[(\d+)\]")


@dataclass
class Trace:
    question: str
    answer: str
    status: str  # "ok" | "no_context"
    chunks: list[dict]
    latency_ms: dict
    token_usage: dict
    trace_id: str = field(default_factory=lambda: uuid.uuid4().hex)

    @property
    def citations_ok(self) -> bool:
        """Every [n] cited maps to a retrieved chunk; silent answers fail."""
        cited = {int(n) for n in CITATION_RE.findall(self.answer)}
        valid = {c["rank"] for c in self.chunks}
        return cited.issubset(valid) and (bool(cited) or not self.chunks)


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def ensure_audit_table(conn) -> None:
    """Create the trace table if missing. Idempotent; runs at service startup."""
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_traces (
                trace_id         TEXT PRIMARY KEY,
                created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
                status           TEXT NOT NULL,
                question_sha256  TEXT NOT NULL,
                answer_sha256    TEXT,
                gemini_model     TEXT NOT NULL,
                embedding_model  TEXT NOT NULL,
                prompt_version   TEXT NOT NULL,
                sources          JSONB NOT NULL,
                latency_ms       JSONB NOT NULL,
                token_usage      JSONB NOT NULL,
                citations_ok     BOOLEAN
            )
            """
        )


def write_trace(conn, trace: Trace, gemini_model: str, embedding_model: str) -> None:
    """Insert one trace row. Callers catch failures — tracing never 500s a chat."""
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO chat_traces (
                trace_id, status, question_sha256, answer_sha256,
                gemini_model, embedding_model, prompt_version,
                sources, latency_ms, token_usage, citations_ok
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                trace.trace_id,
                trace.status,
                _sha256(trace.question),
                _sha256(trace.answer) if trace.answer else None,
                gemini_model,
                embedding_model,
                PROMPT_VERSION,
                _json([{k: c[k] for k in ("rank", "source", "score")} for c in trace.chunks]),
                _json(trace.latency_ms),
                _json(trace.token_usage),
                trace.citations_ok if trace.status == "ok" else None,
            ),
        )


def _json(value) -> str:
    return json.dumps(value)
