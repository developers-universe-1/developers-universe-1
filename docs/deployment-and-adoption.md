# Deployment & Adoption — How AI Lands Inside a Customer's World

The build is the easy half of an FDE engagement. The hard half is getting a production AI system adopted inside a customer's existing workflow without breaking trust — theirs in the system, and their champion's in you. This is the rollout playbook I run on every deployment, using the CalendarFuel platform and the case studies as the worked examples. Every mechanism here exists in code or in a document I hand over — nothing in this doc is a promise made in a meeting.

---

## Build on Top of What Exists

Rule one: the platform meets the customer's stack where it is. Forcing a migration is how pilots die — every migration is a second project the customer didn't ask for, with its own risk, staffed by people who didn't volunteer.

What this looks like on CalendarFuel:

- The client's **LinkedIn accounts stay theirs** — the platform plugs in via Unipile. No exported lists, no new sending tool for reps to learn.
- **Booking stays in Calendly** on the client's own calendar, with a Slack alert to the meeting owner. The platform handles everything between intent and booking; the client just shows up to meetings.
- **The CRM stays the system of record.** Scores and stage changes write back into it. The reference architecture states it plainly: adoption dies the day you ask a rep to check a second tool. Sync-back is the moat.

The same logic drives the database decision in the [reference architecture](../reference-architectures/ai-native-gtm-b2b-saas.md): PostgreSQL as the warehouse, deliberately. For a 50–200-person company, GTM data is ~100K–1M records/month — Postgres handles it with room to spare, and the RevOps lead already knows enough SQL to debug it. Snowflake would add cost, a second query dialect, and an ops burden the customer can't staff. The constraint that shapes the whole design: **the stack must be operable by RevOps alone after handoff.** If the system needs me on call to survive, I haven't finished the deployment.

---

## Graduated Autonomy Is the Default Rollout Path

No AI system I ship starts with write access to anything customer-facing. Autonomy is earned in stages, and each stage has an exit criterion, not a vibe.

| Stage | What the system does | Exit criterion |
|---|---|---|
| **Shadow mode** | Scores/drafts computed and logged; nothing synced, nothing sent | Output compared against human judgment on known cases; the reference architecture does this on days 2–3 against 20 known leads |
| **Review-and-approve** | System produces, human approves before any write or send | Approval rate stabilizes; edits shrink to style, not substance |
| **Supervised autonomy** | Low-risk internal actions auto-execute; external artifacts still gated | Confidence and eval pass rates hold at floor |
| **Earned auto-send** | Auto-send enabled per-customer, per-action-type | Confidence **> 95**, low-risk action classes only — never external first-contact email |

The stages map directly onto the confidence thresholds in the [eval doc](production-ai-evaluation.md): score **< 85** routes to human approval before anything is sent or written, **> 95** is auto-send eligible, and the 85–95 band defaults to review. Two properties matter more than the thresholds:

- **Auto-send is revocable.** One enterprise customer disabled it after a single bad draft, and that was the correct call. Revocation is a config flag, not an incident.
- **The gate is structural, not aspirational.** CalendarFuel's campaign state machine is graduated autonomy expressed in code: DMs are hard-gated behind the `connection.accepted` webhook from LinkedIn, then delayed +2 hours before sending. The system *cannot* skip a step — sequence order is enforced by webhook events, not by hoping the workflow is followed. Zero LinkedIn bans across all client accounts is what that buys.

The weekly eval loop (100 production outputs sampled and hand-graded, 92% pass-rate floor) is what keeps each stage honest after rollout. Autonomy isn't granted once; it's re-earned every week.

---

## De-Risking for the Internal Champion

Every deployment has an internal champion who staked their credibility on it. Their actual fear isn't that the system underperforms — it's that it fails visibly and they get fired for sponsoring it. My job is to make the engagement a thing that gets them promoted. Concretely:

- **Weekly eval reports they can show their VP.** Pass rate against the 92% floor, newly failing cases added to the golden set, latency against budget. The champion should never learn about a regression from their boss; the report lands in their inbox first, written in language a non-engineer can forward upward.
- **Rollback paths documented before launch.** Every automation stage above can drop back one level without a deploy. Shadow mode is always available as the safe harbor — the system keeps computing and logging while humans take back the pen.
- **Failure is designed to be boring.** The [rate-limit post-mortem](../post-mortems/ai-pipeline-rate-limit.md) is the reference: after the Apollo 429 incident, the pipeline got jittered backoff honoring `Retry-After`, a dead-letter queue with a replay path, and alerts on queue depth and 429 rate. The guarantee I give a champion: **worst case, a lead waits — nothing is silently dropped.** A delay is a conversation; silent data loss is a firing.
- **No surprise surface area.** PII is redacted before any LLM call, audit logs record every model decision with input hash, model/prompt version, confidence, and the human decision. When the customer's CISO asks "who decided this went out," the champion answers with a query, not an investigation.

---

## Adoption Is Engineered, Not Hoped For

Case 2 is the proof. A VP Sales had threatened comp plans over CRM hygiene and adoption sat at 34%. The finding from shadowing reps: adoption wasn't a discipline failure, it was a time-cost failure — 6.4 hours/week of post-call admin per rep. No comp plan fixes a 6.4-hour weekly tax.

The mechanism that moved adoption wasn't training or mandates. It was making the automation **checkable**: v1 drafted the CRM update and the rep *reviewed and approved* rather than wrote from scratch. Reviewing takes minutes and builds trust; every approval is a small proof the system got it right. Result: adoption 34% → 89% without a single comp-plan threat, post-call admin 6.4 → 1.2 hrs/week.

Three adoption rules I apply everywhere:

1. **Ship the wedge first.** The fastest path to a number the customer can feel — in Case 1, real-time signal detection (book rate 2.1% → 8.7%, lead-to-alert <15 minutes), not the attribution warehouse. Early felt value is what buys patience for everything deferred.
2. **Meet users in the tool they already open.** Slack alerts, CRM sync-back, Calendly booking. Every extra tab is an adoption tax.
3. **Defer explicitly and say why.** Deferred scope with a reason reads as judgment; deferred scope discovered later reads as a broken promise.

---

## Measuring What Matters

After deployment, I report on three buckets and only three. Anything that doesn't land in one of these is engineering vanity.

| Bucket | Question it answers | Example from this repo |
|---|---|---|
| **Revenue uplift** | Did the system produce pipeline or meetings? | 34% avg reply rate, 127 meetings in one week, book rate 2.1% → 8.7%, $1.2M pipeline attributed, ~1 week faster time-to-close |
| **Risk mitigation** | What did the system prevent? | 0 LinkedIn bans across all client accounts; PII redaction before every LLM call; DLQ + replay so no lead is silently dropped |
| **Cost savings** | What time or spend came back? | Post-call admin 6.4 → 1.2 hrs/wk per rep (5.2 hours reclaimed); the Apollo incident's 4–5 hours of SDR selling time lost is the cost of getting this wrong |

If a metric can't be traced to one of these buckets, it doesn't go in the customer report. It might still go in my own dashboards — but the customer report is how the champion argues for renewal, and it stays sharp.

---

## What This Buys

- Deployments land on the customer's existing stack, so the pilot never becomes a migration project.
- Autonomy is staged and revocable, so the first bad output is a config change, not an incident review.
- The champion gets artifacts — eval reports, audit logs, rollback paths — that make sponsoring the project career-safe.
- Adoption is a designed outcome (checkable automation, sync-back into existing tools), not a change-management hope.
- Success is measured in three buckets a CFO recognizes, which makes the renewal conversation a formality.
