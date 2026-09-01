# Latency and Cost

## Latency budget

| Stage | Target | Notes |
|---|---|---|
| Retrieval (embed query + pgvector search) | p95 < 300ms | Embedding call dominates; HNSW lookup is <10ms at MVP corpus sizes |
| Generation (Gemini) | p95 < 1.7s | Bounded by `MAX_OUTPUT_TOKENS=512` |
| End-to-end `POST /chat` | p95 < 2s | Sum of stages + FastAPI overhead |
| Time to first token (streaming) | < 500ms | When streaming is added, start tokens before retrieval finishes where possible |

## How it's measured

Every `/chat` request logs one structured line (`app/main.py`):

```
chat top_k=5 retrieval_ms=182.4 generation_ms=931.0 total_ms=1113.4 prompt_tokens=1482 completion_tokens=96
```

Cloud Run routes these to Cloud Logging; a log-based metric on `retrieval_ms` /
`generation_ms` / `total_ms` gives p50/p95/p99 dashboards without extra
instrumentation. The same numbers are returned in the response body
(`latency_ms`), so load tests (e.g. `k6`, Locust) can compute percentiles offline
from a run of N requests — that's how the budget above should be validated before
calling the service done.

The three latency numbers per request make regressions attributable: if p95 slips,
you can see in one query whether it was retrieval (embedding API or DB) or generation.

## Cost tracking

Token usage is read from Gemini's `usage_metadata` on every request and returned in
the response (`token_usage`) plus the structured log line above. A scheduled BigQuery
export of Cloud Logging, or a log sink with a sink-side aggregation, turns that into
$/day and $/request without a separate metering service.

### Estimated cost per 1,000 requests

Assumptions: ~1,500 prompt tokens (5 retrieved chunks + question + instructions) and
~150 output tokens per request, plus 1 query embedding (~50 tokens, billed per 1k
chars, negligible). List prices, subject to change — check the Vertex AI pricing page.

| Model | Input $/1M tok | Output $/1M tok | Est. $/1K requests |
|---|---|---|---|
| gemini-2.0-flash-001 | $0.10 | $0.40 | ~$0.21 |
| gemini-2.5-flash | $0.30 | $2.50 | ~$0.83 |
| gemini-2.5-pro | $1.25 | $10.00 | ~$3.38 |

Embedding ingestion adds a one-time cost per corpus refresh (trivial at support-doc
volumes). Cloud SQL `db-custom-2-4096` and Cloud Run scale-to-zero dominate the fixed
floor; per-request LLM cost dominates at volume.

### Cost guardrails

- **`MAX_OUTPUT_TOKENS` enforced in config** (`app/config.py`), passed to every
  `generate_content` call — a runaway completion cannot exceed 512 tokens.
- **Question length capped** (`max_length=4000` on `ChatRequest`) so a single request
  can't inflate the prompt unboundedly; `top_k` capped at 20.
- **`--max-instances 10`** on Cloud Run caps concurrent spend under load or abuse.
- Model choice is one env var, so the quality/cost dial is a deploy-time decision,
  informed by the eval pass rate in `app/evals.py`.
