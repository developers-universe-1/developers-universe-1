# FDE Audit — Week One Operating Map

**Engagement:** Lead intake → scoring → sequencing → booking on the CalendarFuel platform
**Artifact type:** Operating map + exception inventory + ROI priority matrix
**When this exists:** End of week one. Before anything is built.

This is the document I hand a client after the first week of an engagement. It is not a proposal and it is not a backlog. It is a map of how the work *actually* runs — including the parts nobody would tell you in a one-hour meeting, because the people running the process have stopped noticing them. The audit is the deliverable. Everything that ships later is downstream of what's on this page.

The documented process is what the client believes happens. The real process is what the cron loops, webhooks, and one account manager's memory actually do. The gap between the two columns is where the engagement lives.

---

## Operating Map — Documented vs. Real

Each step carries the placement decision: **deterministic** (rule is writable, enforce it in code), **LLM** (judgment under ambiguity, error rate tolerable, output cheap to verify), or **human** (irreversible, relationship-facing, high consequence at low volume).

| # | Step | Documented process | What actually happens | Decision |
|---|---|---|---|---|
| 1 | Lead sourcing | "We feed the platform ICP-fit leads" | Two sources run on independent loops: warm signals (profile viewers, post engagers) pulled from the client's own LinkedIn via Unipile every 2h; hiring-intent and profile search via Apify every 4h. Nobody at the client could name both cadences | Deterministic |
| 2 | Deduplication | "Each lead is in one campaign" | The same prospect surfaces as a profile viewer *and* a post engager *and* an Apify search hit. Cross-campaign dedup exists in places; nothing guarantees a prospect isn't live in two client campaigns at once | Deterministic |
| 3 | ICP scoring | "Leads get scored against our ICP" | LLM scores each lead 0–100 against that client's ICP definition on a 30-min loop, over 60+ enrichment signals. Results cached on record hash — an unchanged lead is never re-scored. The ICP definition itself was written at onboarding and drifts as the client pivots | LLM |
| 4 | Qualification routing | "Good leads go to sequences" | A hard threshold: score ≥ 60 routes to campaign, below is disqualified before it burns a send. One exception the client forgot to mention: open profiles (LinkedIn gold badge) get a +3 bonus and route to the InMail track instead of connection requests | Deterministic |
| 5 | Connection request | "We send connection requests" | Requests go out at human-like pace with daily limits and warm-up scheduling. New client profiles start throttled and ramp. This pacing is why the platform holds zero bans — and it lives partly in code, partly in someone's head | Deterministic |
| 6 | First DM | "We message people who connect" | DMs are hard-gated behind the `connection.accepted` webhook, then delayed +2h so the message doesn't arrive like a bot. No webhook, no DM — the state machine does not advance on optimism | Deterministic gate / LLM content |
| 7 | Follow-up sequence | "We follow up" | Follow-ups escalate to an AI voice note (ElevenLabs TTS through Unipile) instead of another text wall. Voice notes are the step clients describe as "the AI part"; the gate in step 6 is the part that keeps them safe | LLM |
| 8 | Reply handling → booking | "Interested prospects book a call" | Interested replies trigger Calendly autopilot booking plus a Slack alert to the owner. Objections route to AI objection handling and re-engagement. Booking is deterministic; classifying "interested vs. objection" is not | LLM classify / deterministic book |

What the map surfaces that the meeting didn't: the pipeline's safety-critical behavior (steps 5 and 6) is invisible to the client because it works. What they describe as the product (step 7's voice notes) is the least load-bearing part of it.

---

## Exception Inventory

Every workflow has exceptions. The audit question isn't whether they exist — it's *where the knowledge of them lives*. An exception encoded in code survives the person who wrote it leaving. An exception in one person's head is an unpriced dependency.

| Exception | Where the knowledge lives today | Blast radius |
|---|---|---|
| Open-profile InMail routing (+3 bonus, InMail track) | Code | Medium — misroute burns InMail capacity or strands high-intent prospects in the connection-request queue |
| Per-client ICP drift | One person's head — whoever onboarded the client wrote the ICP definition; nobody owns re-reading it as the client's positioning shifts | High — the ≥60 threshold keeps routing, but against the wrong definition; scores look green while targeting decays |
| Stale signals | Partially in code (2h engagement sync) — nothing expires a signal that sat in the inbox | High — warm outreach sent weeks after the signal reads as cold; reply rate is the number that pays for the platform |
| Duplicate leads across campaigns | Nowhere complete — dedup is per-campaign, not cross-campaign | Medium — same prospect touched from two campaigns reads as spam; on LinkedIn, spam reads as a ban risk |
| Warm-up pacing for new profiles | One person's head + runbook | Critical — a new account sent at full pace is the one irreversible failure mode; the zero-ban record is the platform's sales pitch |
| Provider fallback drift (OpenCode → OpenRouter) | Code — fallback exists, but no check that fallback scoring matches primary scoring | Medium — a provider outage silently changes score distribution; ≥60 routing shifts and nobody sees why |
| Provider rate limits | Code, after the incident — jittered backoff honoring `Retry-After`, DLQ + replay, alerts on queue depth and 429 rate | Was critical: 40% of leads dropped for 6h with green dashboards. Now the rule holds: alarm on what the pipeline throws away, not just liveness |

The pattern: the highest-blast-radius exceptions are the ones nobody wrote down. Warm-up pacing and ICP drift both live in exactly one head. That is a staffing risk dressed as a workflow detail.

---

## ROI Priority Matrix

Ranked by volume × pain × risk ÷ build effort. The verdict column is the deliverable — including what I am explicitly recommending we *not* touch.

| Candidate | Volume | Pain | Risk if automated wrong | Build effort | Verdict |
|---|---|---|---|---|---|
| Cross-campaign dedup | High — every sourcing loop feeds it | Medium — duplicate touches erode reply rate | Low — worst case a real lead waits one cycle | Low | **Automate first** — cheap, safe, visible within a week |
| Stale-signal expiry | High — every warm lead has a shelf life | High — stale outreach converts like cold outreach | Low — expiring a live signal costs one lead | Low | **Automate first** — same wedge logic as Case 1: fastest path to a number the client can feel |
| ICP drift detection (periodic drift report per client) | Medium — ~50 customers across 10 companies | Medium — silent targeting decay | Low — a report can't break routing | Medium | **Next** — surfaces drift for a human to act on; does not auto-rewrite ICPs |
| Fallback-score parity check | Low — only during provider outages | Medium | Low — alerting only | Low | **Next** — one comparison job; closes the silent-drift hole |
| LLM-written connection request notes | High | Medium | Critical — LinkedIn restriction risk on the asset that books the meetings | Medium | **Deliberately leave alone** — see below |
| Auto-send of first-touch DMs without the webhook gate | High | High | Critical — ungated sends are how accounts get banned | Low to remove, unacceptable to remove | **Deliberately leave alone** — the gate is the product |

---

## What I Recommended Deferring

Deferring is a deliverable. This is the list the client remembers.

- **LLM-personalized connection request notes.** The highest-volume text surface in the pipeline, and the obvious "AI upgrade." Deferred indefinitely. Connection requests are the rate-limited, ban-exposed step; generated notes add variance exactly where the platform's zero-ban record is earned. Deterministic pacing beats clever copy when the failure mode is losing the client's LinkedIn account.
- **Auto-rewriting client ICP definitions.** Drift detection ships as a report, not an agent. An LLM redefining "who our customer is" from scoring data is feedback-loop territory — the model would be grading its own homework. A human reads the drift report and decides.
- **Bulk re-scoring of the existing lead base.** The record-hash cache means re-scores are cheap, but a re-score against a drifted ICP just moves the error faster. Sequenced after drift detection, not before.
- **Touching the webhook state machine.** The `connection.accepted` gate and the +2h delay stay exactly as they are. "Only one way something goes right, a thousand ways it goes wrong" — this is the one way it goes right.
- **Attribution for sourced leads.** Which signal source actually books meetings is a real question, and answering it needs months of clean touchpoint data before any model beats intuition. Same lesson as Case 3: modeling on partial data makes the argument more confident and more wrong. Deferred to a later phase, with the capture layer starting now so the data exists when the question gets asked.

---

## What This Buys

- The client can see their own operation — most of them have never seen all eight steps on one page.
- Exceptions are priced. "Lives in one person's head" is now a line item with a blast radius, not a surprise at month four.
- The build order is defensible: dedup and signal expiry first because they are cheap, safe, and felt within a week — not because they are interesting.
- Two recommendations are explicit non-builds. Deciding where intelligence does *not* belong is the part of the audit that signals the engagement is being run by an engineer, not a vendor.
