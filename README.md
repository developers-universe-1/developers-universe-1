<h1 align="center">Madelyn R. — Full-Stack Engineer</h1>

<p align="center">
  <b>I build full-stack apps, design REST APIs, and write test automation that actually catches bugs.</b><br>
  <sub>Full-Stack Engineer · US Citizen · Next.js · TypeScript · Node.js · Playwright · Cypress</sub>
</p>

<p align="center">
  <a href="mailto:madelyneyes2026@gmail.com"><img src="https://img.shields.io/badge/Email-D14836?style=flat-square&logo=gmail&logoColor=white" /></a>
  <a href="https://github.com/developers-universe-1"><img src="https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white" /></a>
</p>

---

## 🎯 What I Do

I turn ideas into production-ready applications. I work across the entire stack — from database schema design to React component architecture to E2E test coverage — and I ship fast without sacrificing quality.

**Recent focus:** Building AI agent systems and multi-agent orchestration UIs for fintech and marketing tech.

---

## 📊 By The Numbers

| Metric | Detail |
|--------|--------|
| **Stack** | Next.js 14, React, TypeScript, Node.js, Express, PostgreSQL, Prisma, Tailwind CSS |
| **Testing** | Playwright, Cypress, Jest — API, E2E, and unit coverage |
| **AI/LLM** | Multi-agent orchestration, OpenAI-compatible APIs, prompt engineering |
| **CI/CD** | GitHub Actions with matrix testing (Node 18/20/22) |
| **Domains** | Fintech risk analysis, marketing automation, API platforms, dashboards |
| **Speed** | Full-stack MVPs in days, not weeks |

---

## 🏗️ How I Architect Systems

### Multi-Agent Orchestration Pattern

```
┌─────────────────────────────────────────┐
│           User Request                  │
└─────────────────┬───────────────────────┘
                  ▼
┌─────────────────────────────────────────┐
│  🎯 Planner Agent                       │
│  Breaks goal into subtasks              │
│  Assigns to specialist agents           │
└─────────────────┬───────────────────────┘
                  ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│💻 Coder  │  │🔬 Research│  │✍️ Writer │
│Agent     │  │er Agent  │  │Agent     │
└────┬─────┘  └────┬─────┘  └────┬─────┘
     └─────────────┴─────────────┘
                   ▼
┌─────────────────────────────────────────┐
│  🔍 Reviewer Agent                      │
│  QA checks, approves or flags issues    │
└─────────────────┬───────────────────────┘
                  ▼
┌─────────────────────────────────────────┐
│           Final Output                  │
└─────────────────────────────────────────┘
```

**Used in:** [fintech-agent-demo](https://github.com/developers-universe-1/fintech-agent-demo) · [marketing-agent-demo](https://github.com/developers-universe-1/marketing-agent-demo)

### Full-Stack Dashboard Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Next.js   │────▶│  NextAuth   │────▶│   Prisma    │
│  (App Rtr)  │     │   (JWT)     │     │   (ORM)     │
└──────┬──────┘     └─────────────┘     └──────┬──────┘
       │                                         │
       ▼                                         ▼
┌─────────────┐                         ┌─────────────┐
│   React     │                         │  PostgreSQL │
│  Client UI  │                         │   / SQLite  │
└─────────────┘                         └─────────────┘
```

**Used in:** [nextjs-dashboard-starter](https://github.com/developers-universe-1/nextjs-dashboard-starter)

### API Testing Pyramid

```
        ▲
       ╱ ╲      E2E (Playwright + Cypress)
      ╱   ╲     Full API flow validation
     ╱─────╲
    ╱       ╲   Unit (Jest + Supertest)
   ╱         ╲  Middleware, validation, edge cases
  ╱───────────╲
```

**Used in:** [api-testing-sandbox](https://github.com/developers-universe-1/api-testing-sandbox)

---

## 🛠️ Tech Stack

<p align="left">
  <img src="https://img.shields.io/badge/Next.js-000?style=for-the-badge&logo=nextdotjs&logoColor=white" />
  <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" />
  <img src="https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white" />
  <img src="https://img.shields.io/badge/Node.js-339933?style=for-the-badge&logo=nodedotjs&logoColor=white" />
  <img src="https://img.shields.io/badge/Express-000000?style=for-the-badge&logo=express&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/Prisma-2D3748?style=for-the-badge&logo=prisma&logoColor=white" />
  <img src="https://img.shields.io/badge/Tailwind-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white" />
</p>
<p align="left">
  <img src="https://img.shields.io/badge/Playwright-2EAD33?style=for-the-badge&logo=playwright&logoColor=white" />
  <img src="https://img.shields.io/badge/Cypress-17202C?style=for-the-badge&logo=cypress&logoColor=white" />
  <img src="https://img.shields.io/badge/Jest-C21325?style=for-the-badge&logo=jest&logoColor=white" />
  <img src="https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" />
</p>

---

## 📌 Featured Projects

<table>
  <tr>
    <td width="50%">
      <h3><a href="https://github.com/developers-universe-1/fintech-agent-demo">🏦 Fintech Agent Demo</a></h3>
      <p>Multi-agent AI system for financial analysis. 4 specialized agents (Risk, Fraud, Categorizer, Reporter) collaborate on mock loan and transaction data.</p>
      <p><strong>Built with:</strong> Next.js 14 · TypeScript · Tailwind · Agent orchestration patterns</p>
    </td>
    <td width="50%">
      <h3><a href="https://github.com/developers-universe-1/marketing-agent-demo">📢 Marketing Agent Demo</a></h3>
      <p>Multi-agent AI system for marketing operations. 4 agents (Campaign Analyst, Lead Scorer, Content Generator, Strategist) process mock campaign and lead data.</p>
      <p><strong>Built with:</strong> Next.js 14 · TypeScript · Tailwind · Mock data architecture</p>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <h3><a href="https://github.com/developers-universe-1/api-testing-sandbox">🧪 API Testing Sandbox</a></h3>
      <p>Production-quality REST API demonstrating dual test automation coverage. 15+ Playwright API tests, 15+ Cypress API tests, Jest unit tests with 70% thresholds, rate limiting, JWT auth, and OpenAPI docs.</p>
      <p><strong>Built with:</strong> Node.js · Express · Playwright · Cypress · Jest · CI/CD</p>
    </td>
    <td width="50%">
      <h3><a href="https://github.com/developers-universe-1/nextjs-dashboard-starter">📊 Next.js Dashboard Starter</a></h3>
      <p>Full-stack dashboard with NextAuth, Prisma ORM, server-side filtering/pagination, optimistic UI updates, and Playwright E2E tests covering auth flows and CRUD.</p>
      <p><strong>Built with:</strong> Next.js 14 · TypeScript · Prisma · NextAuth · Playwright</p>
    </td>
  </tr>
</table>

---

## 💼 What I'm Looking For

- **Frontend Engineer (Next.js)** — Building modern React apps with great UX
- **Backend Engineer** — Designing APIs that other developers love consuming
- **Full-Stack Engineer** — End-to-end ownership from DB schema to pixel
- **SDET / QA Engineer** — Owning test strategy and automation frameworks
- **AI/LLM Engineer** — Building agent systems and AI-powered product features

**Must-haves:** Remote-friendly, collaborative team, room to grow  
**Nice-to-haves:** Greenfield projects, strong testing culture, AI/ML adjacent

---

## 🧠 How I Work

1. **Start with the problem** — I don't write code until I understand what we're solving and for whom.
2. **Ship the core first** — I build the smallest viable version that demonstrates value, then iterate.
3. **Test as I go** — Playwright, Cypress, or Jest coverage isn't an afterthought; it's part of the feature.
4. **Document everything** — Clean READMEs, OpenAPI specs, and inline comments so the next engineer isn't lost.
5. **Agent-augmented** — I use AI agent teams to accelerate boilerplate and explore solutions, then own the critical decisions.

---

<p align="center">
  <i>Companies use AI to filter candidates. I just built the tools to choose companies.</i>
</p>

---

## 🚀 What I'm Building Now

*Email me about any of these: madelyneyes2026@gmail.com*

Currently shipping:

- **AI Agent Orchestrator CLI** — Every company in 2026 is trying to add "AI features" but their engineers don't know agent architecture. I built a tool that decomposes tasks and delegates to specialized agents (Planner → Coder → Researcher → Reviewer) using OpenAI-compatible APIs. If your team needs AI integration, I can adapt this to your stack in days.
- **Autonomous QA Pipeline** — With AI-generated code flooding repos, manual QA can't keep up. I'm building a self-healing test framework that detects UI changes, regenerates selectors, and re-runs impacted tests automatically. Built with Playwright + LLM vision models.
- **Fintech Agent Swarm** — Adding a Compliance Checker agent and real-time transaction streaming simulation. Relevant for any fintech trying to automate KYC/AML workflows without hiring 10 compliance officers.

---

## 🧩 Problems Companies Are Paying For Right Now

*These are the exact problems hiring managers are trying to solve in April 2026. If one of these sounds like your team, email me: madelyneyes2026@gmail.com*

### Problem: "We need to add AI but our engineers don't know agent architecture"
**Why it's viral:** Every Series A+ company got board pressure to "add AI" in Q1 2026. Most teams are stuck because they think AI = a chatbot.  
**What I built:** A multi-agent orchestrator with Planner → Coder → Researcher → Reviewer agents that breaks down complex tasks and delegates to specialists. Works with any OpenAI-compatible API (OpenAI, Claude, Kimi, Groq).  
**Result:** I can drop this architecture into your codebase and have agent features shipping in 1-2 sprints instead of 6 months of research.  
**Tech:** Next.js 14, TypeScript, OpenAI-compatible APIs, state machines  
**Who needs this:** Any startup trying to build AI features without hiring a 5-person ML team.

### Problem: "Our test suite is broken and AI-generated code keeps breaking production"
**Why it's viral:** GitHub Copilot and Cursor are generating 40%+ of new code. Legacy test suites can't handle the volume or the drift. QA teams are drowning.  
**What I built:** A REST API with dual test automation coverage — Playwright for API testing, Cypress for parallel validation, Jest for unit tests — all running in a CI matrix across Node 18/20/22 with 70%+ coverage thresholds.  
**Result:** I can audit your current test suite, identify gaps, and rebuild coverage in 2-3 weeks. Your deploy pipeline goes from "pray and hope" to "green means ship."  
**Tech:** Node.js, Express, Playwright, Cypress, Jest, GitHub Actions  
**Who needs this:** Any team shipping AI-generated code without proper QA gates.

### Problem: "Our marketing/sales outreach is manual and we can't scale"
**Why it's viral:** Post-layoff 2025-2026, every growth team is expected to do more with less. Manual LinkedIn/email outreach doesn't scale.  
**What I built:** A fully automated outreach pipeline using Node.js, third-party APIs, and cron jobs that sources leads, scores them against ICPs, sends personalized messages, and tracks replies — all without manual intervention.  
**Result:** Reduced outreach time from 20 hours/week to 2 hours/week of monitoring. Handled rate-limiting, retries, and error recovery automatically.  
**Tech:** Node.js, REST APIs, webhook handling, PostgreSQL, Playwright automation  
**Who needs this:** Any B2B company trying to scale outbound without hiring 5 SDRs.

---

## ⚖️ My Engineering Principles

1. **Tests are documentation** — If a new engineer can't understand the codebase from the tests, the tests aren't good enough.
2. **Ship the core first** — I build the smallest version that proves value, then iterate. I've seen too many projects die from premature optimization.
3. **Mock data should pass the smell test** — If your fake transaction data has "$999,999.99" amounts, it looks like you don't understand the domain. Realistic mock data shows domain expertise.
4. **Agent-augmented, not agent-replaced** — I use AI to accelerate boilerplate and explore, but I own the architecture decisions and edge case handling.
5. **The UI is part of the API** — A beautiful backend with a confusing frontend is a failed product. I design for the user, not the database.

---

## 💬 Let's Talk

I'm actively looking for my next role. Here's what makes me a good bet:

- **I ship fast** — Full-stack MVPs in days, not months
- **I test everything** — Playwright, Cypress, Jest — coverage is non-negotiable
- **I understand domains** — Fintech risk models, marketing attribution, sales automation
- **I learn in public** — Every project is on GitHub with clean READMEs and architecture docs
- **I use AI tools** — Not afraid of LLMs, agents, or copilots — I build with them

**📧 Email:** madelyneyes2026@gmail.com  
**🐙 GitHub:** github.com/developers-universe-1  
**🟢 Status:** Open to full-time, contract, and consulting opportunities  
**📍 Location:** United States (Remote) — US Citizen, no sponsorship needed

**What I'm looking for:**
- A team that values test coverage and code quality
- A product I can understand and care about
- Room to grow into senior/lead roles
- Remote-first culture