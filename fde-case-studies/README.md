# FDE Decomposition Case Studies

Forward Deployed Engineering interviews don't test LeetCode — they test whether you can take a vague, emotionally-charged customer problem and decompose it into shippable components. These are three real decompositions from my work, written in the format I use in interviews.

Each case follows the same structure: **what the customer actually said** → **how I decomposed it** → **the wedge** → **what shipped in v1 vs. what I deferred** → **architecture decision** → **outcome**.

---

## Case 1: "Our leads are bad"

**Customer:** Series B B2B SaaS, ~80 employees, 6-person SDR team.

### What the customer actually said

> "We're spending $40K/month on LinkedIn but our sales team says the leads are trash."

Note what this is *not*: it's not "we need better leads." It's two teams with contradictory dashboards and no shared definition of "good." The stated problem (lead quality) was a symptom; the actual problems were attribution blindness and stale intent data.

### How I decomposed it

1. **Defined "bad" with data, not vibes.** Pulled 90 days of CRM records. "Trash leads" decomposed into three distinct failure modes: (a) no attribution visibility — nobody knew which channel sourced which meetings; (b) 30–45 day stale intent data from static ZoomInfo lists; (c) no intent scoring — every lead treated identically regardless of buying signals.
2. **Found the wedge.** Fixing attribution requires months of historical data before it produces insight. Fixing stale intent produces value in week one. **The wedge was real-time signal detection** — fastest path to a number the customer could feel.
3. **Scoped v1 ruthlessly.** LinkedIn engagement monitor → 4-layer ICP score → Slack alert to the owning SDR. Nothing else. No dashboard, no warehouse, no multi-touch model.
4. **Deferred explicitly.** Multi-touch attribution warehouse moved to v2 (needed ~3 months of clean touchpoint data to be meaningful). I told the customer *what they weren't getting and why* — that's the part of decomposition most engineers skip and most customers remember.

### Architecture decision

PostgreSQL + FastAPI instead of a warehouse-first design. The customer had no data team and needed <15-minute lead-to-alert latency; a Snowflake/dbt stack would have added 4–6 weeks and an ops burden they couldn't staff. Right-sizing infrastructure to the customer's operating reality is the decision — not the technology itself.

### Outcome

- Meeting book rate: **2.1% → 8.7%** (4x)
- Lead response time: **30–45 days → <15 minutes**
- Competitive win rate: **+23%** (reps reached prospects during active evaluation windows)
- Daily dials dropped 80 → 35 while meetings/week rose 3.2 → 6.1

---

## Case 2: "Reps won't update the CRM"

**Customer:** Enterprise sales org, 12 reps, VP Sales as the champion.

### What the customer actually said

> "I've threatened comp plans over CRM hygiene and it's still at 34% adoption. Just fix it."

Tempting reading: change-management problem. Actual finding from discovery: reps spent **6.4 hours/week** on post-call admin (CRM updates, follow-ups, call notes). Adoption wasn't a discipline failure — it was a time-cost failure. No amount of comp pressure fixes a 6.4-hour weekly tax.

### How I decomposed it

1. **Separated the symptom from the workflow.** Shadowed two reps for a day. Post-call work broke into: CRM field updates, follow-up email drafting, call note summarization, next-step scheduling. Each had a different automation shape.
2. **Found the wedge.** Call recording → structured CRM update was the highest-frequency, most-mechanical task. If the CRM updated itself, adoption stops being a metric you manage and becomes a side effect.
3. **Scoped v1.** Gong/Fathom/Fireflies webhook → AI analysis pipeline (objection classification, sentiment trajectory, next-step extraction) → auto CRM update → rep *reviews and approves* rather than writes. Human-in-the-loop was non-negotiable for trust in week one.
4. **Deferred.** Coaching scorecards and follow-up auto-drafting shipped in v2, after reps trusted the CRM automation. Sequencing mattered: coaching features before trust = surveillance; after trust = value.

### Architecture decision

Event-driven (webhook → queue → analysis → CRM write) rather than batch polling, because the value decays fast — a follow-up drafted 3 minutes after the call converts; one drafted the next morning is admin again. Reviewer checkpoint before any CRM write: automation earns trust by being checkable.

### Outcome

- Post-call admin: **6.4 → 1.2 hrs/week per rep** (5.2 hours reclaimed)
- CRM adoption: **34% → 89%** — without a single comp-plan threat
- Follow-up send time: **45 min → 3 min**
- Coaching became data-driven: managers saw exactly which objection types each rep struggled with

---

## Case 3: "Marketing and sales disagree on what's working"

**Customer:** Series B SaaS (same company as Case 1, three months later — this was the deferred v2).

### What the customer actually said

> "Marketing says LinkedIn is 60% of pipeline. Sales says email is 60% of pipeline. One of them is lying and I don't know which." — CFO

Classic attribution fight. Both numbers were "true" under different models — first-touch credited LinkedIn's awareness role, last-touch credited email's closing role. The argument existed because the company had implicitly picked a different model per team without knowing it.

### How I decomposed it

1. **Reframed the problem.** The question isn't "which team is right" — it's "which model matches our buying journey." That requires running *multiple* models in parallel over the same data and comparing.
2. **Audited the data first.** Before modeling: were touchpoints even captured? Found webinar touches and LinkedIn organic engagement missing entirely. Modeling on partial data would have just made the argument more confident and more wrong.
3. **Scoped v1.** Ingest every touchpoint (Salesforce, HubSpot, Apollo, Clearbit) into a unified PostgreSQL schema → run four models in parallel: first-touch, last-touch, linear, U-shaped.
4. **Deferred.** Predictive budget allocation (given a model, where should the next dollar go) — needed two more quarters of clean data before recommendations would beat the CFO's intuition.

### Architecture decision

Models as pure SQL over a dimensional schema rather than a Python notebook, because the CFO's team needed to re-run and audit them without an engineer in the loop. Auditability was the feature — the deliverable was trust, not a number.

### Outcome

- **$1.2M pipeline attributed** with model-level transparency
- U-shaped revealed the real story: LinkedIn created awareness (35%) but email closed (38%)
- Budget reallocated from broad LinkedIn ads to targeted email nurture
- CFO's question changed from *"Is this working?"* to *"How do we scale what works?"*

---

## The Pattern Across All Three

1. **The stated problem is never the problem.** "Bad leads," "lazy reps," "lying teams" — each decomposed into a data or workflow failure with a nameable shape.
2. **The wedge is the fastest path to a number the customer can feel.** Not the most elegant component, not the biggest one.
3. **Deferring is a deliverable.** Saying what you're *not* building, and why, is what separates decomposition from scope creep.
4. **Architecture follows the customer's operating reality** — team size, latency needs, staffing — not the engineer's preference.
