# Production AI Evaluation — Agentic Revenue Intelligence

How the LLM components of the Agentic Revenue Intelligence system are gated, budgeted, and audited before and after they reach enterprise customers. This covers the two production surfaces: **ICP lead scoring** (classification) and **follow-up draft generation** (generation). If a number here changes, it changes because an eval run justified it — not because someone tweaked a prompt and it "felt better."

---

## Latency Budget

Latency is a product feature in sales tooling — a score that arrives after the rep has moved on is worth zero.

| Component | p50 | p95 | Notes |
|---|---|---|---|
| ICP scoring (end-to-end) | < 200ms | < 800ms | Enrichment lookup + deterministic features + model call |
| Follow-up draft (full) | — | < 3s | Streaming; first token renders at ~500ms |

- First-token streaming matters more than total time for drafts. A rep watching text appear at 500ms perceives "instant"; a 2.5s spinner reads as broken.
- p95 is the SLO, not p50. p50 hides the tail, and the tail is exactly the enterprise customer with the largest record payloads.
- If the scoring path breaches 800ms p95 for two consecutive days, the fallback is the cached prior score plus a recompute job — never a blocking wait on the model.

---

## Quality Gates

No LLM output reaches a customer-visible surface without passing these.

1. **Hallucination check (two layers).**
   - *Structural:* regex/schema validator confirms every claim in a draft maps to a field that exists in the source record (company name, deal size, last touch date). Anything that looks like an invented number or name fails fast.
   - *Semantic:* embedding similarity between the generated text and the source data it cites. Below the similarity threshold, the output is rejected and regenerated once; a second failure routes to a human.
2. **Human-in-the-loop routing by confidence score.**
   - Score **< 85** → requires human approval before anything is sent or written to the CRM.
   - Score **> 95** → auto-send eligible (only for low-risk actions: internal CRM updates, never external emails on first contact).
   - The 85–95 band defaults to review. Auto-send is earned per-customer, per-action-type, and can be revoked — one enterprise customer disabled it after a single bad draft and that was the correct call.
3. **Weekly eval sampling.** 100 production outputs sampled per week, graded manually against the rubric (factual accuracy, format compliance, tone, no PII leakage). If pass rate drops **< 92%**, the prompt (or model routing) gets tuned and the failing cases get added to the golden set so the regression can't silently return.

---

## Cost Controls

- **Model routing by task difficulty:** GPT-4o-mini for classification (ICP scoring, objection tagging) — cheap, fast, and classification doesn't need frontier capability. GPT-4o for generation (follow-up drafts, call summaries) where quality is customer-visible.
- **Max tokens enforced at the API gateway**, not in app code. A prompt bug that balloons output length hits a hard ceiling instead of a surprise invoice. Token and spend dashboards per customer; per-customer budgets exist because one runaway loop at ~500K records/month is a real scenario, not a hypothetical.
- Classification results are cached on the record hash — a lead that hasn't changed doesn't get re-scored.

---

## Evaluation Dataset Management

- **Golden set:** ~250 curated input/output pairs drawn from real (anonymized) production cases — hard cases deliberately over-represented: edge-case ICPs, ambiguous call transcripts, records with missing fields.
- **Versioned in git alongside the prompts** (`evals/` directory). Every prompt change ships with the golden-set run result in the PR description: pass rate, delta vs. baseline, and any newly failing cases. A prompt PR without an eval run doesn't merge.
- **Growth path:** every weekly-sampling failure and every human-override of an auto-sent output becomes a candidate golden-set entry. The set grows from production pain, not from imagination.

---

## Failure Mode Taxonomy

| Failure mode | What it looks like | Mitigation |
|---|---|---|
| **Hallucination** | Invented deal sizes, wrong contact names, fabricated "as discussed" references | Regex + schema validator against source fields; semantic similarity check; regenerate-once then human routing |
| **Format drift** | Model output no longer parses into CRM fields after a model version bump | Output contract tests in CI on every model/prompt version change; structured output mode (JSON schema) where the API supports it |
| **PII leakage** | Prospect personal data surfacing in outputs or logs beyond what's contractually allowed | PII redaction layer before any LLM call (see below); PII checks in weekly manual grading; log scrubbing |
| **Stale-data reasoning** | Confident output from an enrichment record that's 45 days old | Data-freshness field injected into every prompt context; outputs carry a "data as of" stamp |
| **Prompt injection** | Malicious text in a scraped profile or inbound email steering the model | System/user prompt separation, instruction hierarchy, no tool access from untrusted content without sanitization |

The taxonomy exists so that when something breaks in production we classify it in the incident review and ask "which mitigation failed," not "wow, weird."

---

## Responsible AI

Three commitments, all enforced in code rather than policy docs:

1. **PII redaction before LLM calls.** Prospect and customer records pass through a redaction layer (names of minors, personal phone numbers, anything flagged sensitive in the CRM) before hitting any external model API. Redaction is logged, so "did we send this to the model?" is answerable.
2. **Human review gates.** No external-facing artifact is auto-sent without the confidence thresholds above. Automation earns autonomy by being checkable first — this is the same reason Case 2's CRM automation was review-and-approve in v1.
3. **Audit logging.** Every LLM call logs: input hash, model version, prompt version, output, confidence score, and the human decision (approved/edited/rejected). When a customer's CISO asks "who decided this email went out," the answer is a query, not an investigation. A working, minimal version of this pattern ships in code in the [Vertex AI RAG agent](../vertex-ai-rag-agent/README.md#audit-trail) (`app/audit.py` — one `chat_traces` row per request: input/output hashes, model and prompt versions, retrieved sources, latency, tokens, citation verdict).

---

## What This Buys

- Evals gate changes; they don't just observe them. A prompt regression fails a PR before it fails a customer.
- Latency budgets are set by the rep's workflow, not by what the model happens to deliver.
- Cost is engineered at the routing layer, where the leverage is — not by asking people to write shorter prompts.
