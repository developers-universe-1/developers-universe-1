# Incident: AI Pipeline Dropped 40% of Leads for 6 Hours

**Author:** Madelyn Reyes
**Status:** Resolved
**Severity:** SEV-2 (revenue-adjacent, no data loss after replay)
**Duration:** 6h 12m (first 429 to full queue drain)

## Summary

The lead enrichment pipeline silently dropped roughly 40% of incoming leads for about six hours after Apollo reduced the rate limit on our API tier from 100 requests/minute to 10 requests/minute. The v1 enrichment worker had no retry logic at all — it treated a 429 the same as a 500 and moved on — so rate-limited leads were marked "enriched" with empty fields and pushed to SDR queues as-is. Symptom was a backed-up CRM enrichment queue and SDRs working leads with no contact data, no intent score, and stale firmographics. Detection came from a human, not a monitor: an SDR Slack message asking why "every lead this morning is blank."

## Impact

- ~3,800 of ~9,400 leads ingested during the window (40.4%) were written to the CRM with empty enrichment fields.
- Enrichment queue depth peaked at ~2,100 messages; normal steady-state is under 50.
- 6 SDRs spent the morning triaging blank leads manually instead of working sequences; estimated 4–5 hours of collective selling time lost.
- No permanent data loss. All affected leads were replayed from the dead-letter queue after the fix; enrichment completed by end of day.
- No customer-facing impact. This was internal pipeline infrastructure.

## Timeline

All times PT.

- **07:52** — Apollo's rate limit change takes effect. First 429s appear in worker logs. No alert fires; we had no alert on 429 rate.
- **08:15–11:30** — SDRs begin their day. Leads arriving "enriched" but blank. Because the pipeline kept *writing records*, every dashboard looked green.
- **11:34** — Detection. An SDR posts in #sales-ops: "is enrichment broken? every lead since this morning has no phone number." I get tagged.
- **11:41** — I pull the enrichment worker logs. The dominant log line is `POST /v1/mixed_people/search 429`, repeating since ~07:50. First hypothesis: transient Apollo outage.
- **11:58** — I replay a single failed request manually with `curl`. It 429s consistently even at 1 request/second, which rules out a transient burst and points at a changed limit. Apollo's response body confirms the tier limit is now 10/min; the change had shipped in their changelog two days earlier, which none of us had read.
- **12:10** — Diagnosis confirmed: worker sends 429'd requests, gets no `Retry-After` handling (Apollo does send the header; we never read it), records the lead as processed, and advances the queue offset. Data isn't backed up at the queue — it's being *consumed and discarded as failures*.
- **12:25** — Mitigation: I pause the enrichment worker to stop the bleeding. Queue starts accumulating cleanly instead of being drained into garbage writes. SDR leads are temporarily routed to a "pending enrichment" view so reps stop working blanks.
- **12:40–14:15** — I write and deploy the fix: jittered exponential backoff honoring `Retry-After`, a dead-letter queue for leads that exhaust retries, and a replay path from DLQ back into the main queue.
- **14:15** — Worker redeployed. DLQ replay starts for the ~3,800 affected leads.
- **18:04** — Queue fully drained, all affected leads enriched and written. Incident closed.

## Root Cause

Two causes, one proximate and one structural:

1. **Proximate:** Apollo reduced our tier's rate limit 100/min → 10/min without an in-band deprecation window we'd configured alerts on. Our throughput (~40 req/min steady state, higher during morning ingest bursts) instantly exceeded the new ceiling.
2. **Structural:** The v1 enrichment worker was written with a success-path-only error model. Any non-2xx response — including 429 — was logged and skipped, and the lead was marked processed. There was no backoff, no retry, no dead-letter, and no alerting on failure rate or queue depth. The system was designed to lose data quietly under exactly this class of failure, and it did, for four hours, with every dashboard green.

The rate limit change was the trigger. The missing failure handling is why four hours passed before a human noticed. That's the part we owned.

## Resolution

Three changes shipped same day:

- **Jittered exponential backoff** on the Apollo client: base delay 1s, cap 60s, full jitter, honors the `Retry-After` header when present (it was present all along; we just never parsed it). Max 5 attempts before giving up.
- **Dead-letter queue** for leads that exhaust retries, with a replay worker that re-enqueues DLQ messages once the upstream recovers. Nothing is silently dropped anymore — worst case, a lead waits.
- **PagerDuty alert** on queue depth > 100 sustained for 5 minutes, plus a secondary alert on 429 rate > 5% of requests. Detection no longer depends on an SDR noticing blank fields.

## Lessons Learned / Prevention

The uncomfortable lesson: "the pipeline is up" and "the pipeline is working" were the same signal in our monitoring. Writes were succeeding; the writes were just empty. Green dashboards measured liveness, not correctness. Any pipeline that consumes a queue should alarm on what it *throws away*, not just on whether it's running.

Second lesson: third-party API limits are a dependency contract that can change underneath you. We now treat provider changelogs as operational inputs, not release notes to skim later.

### What changed in the codebase

- [x] `apollo_client.py`: retry decorator with jittered exponential backoff + `Retry-After` support (default for all methods, not opt-in)
- [x] `enrichment_worker.py`: non-2xx responses no longer mark a lead as processed; failures route to DLQ after max retries
- [x] New `dlq_replay.py` worker: replays dead-lettered leads on upstream recovery, idempotent on lead ID
- [x] PagerDuty alerts: queue depth > 100 (5 min sustained), 429 rate > 5%, DLQ depth > 0 for > 30 min
- [x] Circuit breaker wrapper (`circuit_breaker.py`) applied to Apollo, Clearbit, and HubSpot clients — all external API calls now fail fast and queue instead of hammering a degraded provider
- [x] Data-quality check: hourly job alerts if > 2% of enriched leads have empty core fields (phone, title, company domain) — the signal that would have caught this at 08:00
- [x] Subscribed to Apollo/HubSpot/Clearbit status pages and changelogs; ownership assigned in the on-call runbook
- [x] Runbook entry added: "queue depth alert → check provider status page before touching the worker"

Backoffs and circuit breakers are now the default in the shared HTTP client, so the next integration gets them without anyone deciding to add them.
