# Where Intelligence Belongs — Deterministic vs. LLM vs. Human

The most consequential decision in any AI deployment is not which model to use. It is which parts of the workflow should use a model at all. Most failed AI pilots I have seen failed the same way: LLM calls bolted onto steps that were never judgment problems to begin with. This is the placement framework I run on every engagement before a single prompt gets written, with real decisions from the systems in this repo.

---

## The Three Buckets

Every step in a workflow earns one of three placements based on its properties, not on what is fashionable.

| Bucket | Properties that earn it | Test I apply |
|---|---|---|
| **Deterministic** | The rule is writable down to the last branch. Failure is either catastrophic or trivially cheap to check. Volume is high. | Can I write the correct output as code and unit-test it? If yes, an LLM here is a liability. |
| **LLM judgment** | The input is ambiguous or unstructured. A bounded error rate is tolerable. Errors are cheap to detect or verify downstream. | Can I define "wrong," sample outputs weekly, and route failures to a human? If yes, the model earns its tokens. |
| **Human** | The action is irreversible, relationship-facing, or low-volume/high-consequence. | Would one wrong execution cost more than every correct one saves? If yes, a person decides. |

The buckets are not a capability ranking. Deterministic beats LLM judgment wherever the rule is writable — cheaper, faster, and it fails loudly instead of plausibly.

---

## Placement Decisions in Production

Six real calls from the CalendarFuel platform and the Agentic Revenue Intelligence evals, with the reasoning and the failure mode if misplaced.

### 1. Schema validation and PII redaction — deterministic

Every LLM input passes through a redaction layer and every output passes a regex/schema validator before it can touch a customer surface. These rules are fully writable: a field either maps to a source record or it does not, a phone number either matches the pattern or it does not. Volume is ~500K records/month, so the check has to be microseconds, not a model call. **If misplaced:** an LLM judging its own PII leakage would leak at some nonzero rate with no testable contract — a compliance incident expressed as a probability instead of a bug.

### 2. ICP scoring — LLM judgment, with a deterministic route

Each lead is scored 0–100 against a specific client's ICP — title, seniority, company size, funding, tech stack, recent activity — across 60+ enrichment signals. Judging how a non-obvious profile maps to "this client's actual buyer" is ambiguity work; the rule is not writable, which is why it defeats static lists. GPT-4o-mini runs classification because classification does not need frontier capability, and results are cached on the record hash so unchanged leads are not re-scored. The error rate is tolerable because verification is cheap: score ≥ 60 routes to a campaign, below 60 is disqualified — the *routing* is a deterministic threshold, so the blast radius of a mis-score is one wasted send, not a corrupted system of record. **If misplaced the other way** (pure rules): the edge cases that decide whether a lead is good — a founder with an odd title, a company between stages — get scored wrong 100% of the time instead of 5%.

### 3. Objection classification and reply triage — LLM judgment

Inbound replies are unstructured text with intent buried in them. The classification feeds the follow-up sequence, and a misclassification surfaces in the unified reply inbox where a human sees it within the same workflow. Error is tolerable and visible. **If misplaced:** a deterministic keyword matcher catches "not interested" and misses "circle back after our funding closes" — the replies with the most money in them.

### 4. Follow-up draft generation — LLM judgment, human-gated by confidence

GPT-4o drafts; nothing ships unchecked. Score < 85 requires human approval before anything is sent or written to the CRM; > 95 is auto-send eligible only for low-risk internal actions, never external first contact. Auto-send is earned per-customer and revocable — one enterprise customer disabled it after a single bad draft and that was the correct call. **If misplaced:** full auto-send on day one means the first hallucinated "as discussed on our call" reference burns a prospect relationship the client spent months warming. Autonomy is earned with pass rates, not granted at install.

### 5. External first-touch send — human gate

The first message a prospect ever sees is relationship-facing and effectively irreversible. Per the quality gates, auto-send eligibility explicitly excludes external emails on first contact regardless of confidence score. Volume here is low relative to consequence. **If misplaced:** a confidence score cannot price reputational damage; 95% confident across 1,000 first touches is 50 brand-shaped errors.

### 6. Follow-up voice notes — LLM generation inside a deterministic trigger

Late-sequence follow-ups escalate to an ElevenLabs AI voice note instead of another text message. Whether to escalate is a deterministic sequence position — the state machine decides. What the voice note says is generation work and goes through the same quality gates as drafts. The split matters: the trigger being a model decision would make outreach cadence unauditable; the content being template code would read like mail-merge. **If misplaced:** letting the model pick *when* to send a voice note puts a probability in charge of the thing LinkedIn health monitoring is watching.

### 7. Enrichment failure handling — deterministic

Retry with jittered backoff honoring `Retry-After`, dead-letter queue, replay on recovery. The Apollo 429 incident exists because this logic was absent, and its replacement is pure code — there is exactly one correct response to a 429. **If misplaced:** an LLM "deciding" what to do with a rate-limited lead would be a nondeterministic data-loss machine. This class of problem never needed intelligence; it needed an error model.

---

## Where I Deliberately Do NOT Use AI

This section is the point of the document. Each of these was a candidate for an LLM call and each was rejected.

- **Connection-request pacing and warm-up scheduling.** Daily limits, human-like jitter, per-account warm-up curves. The rule is writable and the failure mode is catastrophic — a restricted LinkedIn account is a client relationship incident. Zero bans across all client accounts comes from boring arithmetic, not judgment.
- **Webhook state machine transitions.** DMs are hard-gated behind the `connection.accepted` webhook, then scheduled +2h. A state transition either happened or it did not; there is no ambiguity for a model to resolve. Putting an LLM on the gate would mean a probability decides what a boolean already knows.
- **CRM field writes.** Scores and stage changes write back to Salesforce/HubSpot through typed sync code. A malformed write corrupts the system of record the whole company reads. Writes are validated, logged with before/after values, and reversible — none of which an LLM adds.
- **Routing thresholds.** Score ≥ 60 routes to campaign; open profiles get +3 and route to InMail. Thresholds are deterministic and tuneable in a review meeting. The judgment lives upstream in the score, where ambiguity actually exists.
- **Retry and queue logic.** Covered above. The thousand ways a pipeline goes wrong are enumerated in code, not negotiated with a model.

The common thread: if the failure is silent, irreversible, or corrupts shared state, the step gets code. AI goes where ambiguity lives and nowhere else.

---

## Revisiting the Map

Placements are versioned decisions, not permanent ones. Three things move a step between buckets:

- **Eval results.** A step whose pass rate holds above the 92% floor on weekly sampling earns a wider confidence band. A step that regresses moves back toward review — the 85–95 band exists precisely so the map can tighten without a code rewrite.
- **Model capability.** Steps currently human-gated because verification is expensive get re-examined as verification gets cheaper. The gate moves when the check does, not when the model does.
- **Blast radius changes.** A step that was internal becomes external, or volume jumps an order of magnitude, and the tolerable-error math changes. The map gets re-run, not grandfathered.

---

## What This Buys

- LLM budget goes to steps where ambiguity actually exists — classification and generation — instead of subsidizing steps that were always writable rules.
- Failures land in the bucket designed to absorb them: deterministic bugs fail tests, LLM errors fail evals, human decisions carry accountability.
- Every "no AI here" is documented with reasoning, so the next engineer adds intelligence where it earns its tokens rather than where it demos well.
