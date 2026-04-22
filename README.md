<h1 align="center">Madelyn R. — Full-Stack Engineer</h1>

<p align="center">
  <b>I build full-stack apps, design REST APIs, and write test automation that actually catches bugs.</b><br>
  <sub>3–5 years shipping code. Next.js · TypeScript · Node.js · Playwright · Cypress</sub>
</p>

<p align="center">
  <a href="mailto:your-email@example.com"><img src="https://img.shields.io/badge/Email-D14836?style=flat-square&logo=gmail&logoColor=white" /></a>
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
