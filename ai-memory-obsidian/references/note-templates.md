# Obsidian Vault Note Templates 📝

Standardized Markdown templates for Architectural Decision Records (ADRs), session digests, and daily developer logs.

---

## 1. Architectural Decision Record (ADR) Template

Save at: `decisions/ADR-YYYY-MM-DD-<slug-title>.md`

````markdown
---
title: "ADR: Database Engine for Telemetry Store"
date: 2026-09-27
status: accepted # accepted | proposed | deprecated | superseded
tags:
  - adr
  - architecture
  - database
---

# ADR: Database Engine for Telemetry Store

## 📌 Context & Problem
We require a local, high-frequency storage layer for agent telemetry and session metrics with sub-millisecond write latency and 30-day retention pruning.

## ⚖️ Decision
We chose **SQLite with WAL mode** enabled locally instead of provisioning an external database container.

## 🎯 Consequences & Trade-offs
- **Positive**: Zero external runtime dependencies, instantaneous boot, embeddable in CLI distributions.
- **Positive**: Blazing-fast FTS5 full-text queries for cross-session lookups.
- **Negative**: Single-writer process concurrency limitation.
````

---

## 2. Session Digest Template

Save at: `sessions/Session-YYYY-MM-DD_HHhMM-<agent>-<id>.md`

````markdown
---
title: "Session: Authentication Middleware Refactoring"
date: 2026-09-27
agent: claude-code # or antigravity, cursor
tags:
  - session
  - auth
  - refactor
---

# 🤖 Session 2026-09-27 — Auth Refactor

## 📋 Executive Summary
Refactored the JWT verification layer, isolating token lifecycle validation into a dedicated middleware module.

## 🛠️ Actions Taken
- Created `src/middlewares/auth.ts`.
- Updated `src/routes/api.ts` to attach the auth middleware.
- Validated unit test suite with 100% pass rate.

## 📌 Finalized Decisions
- Access token lifespan locked to 15 minutes; refresh tokens configured for 7 days.

## 🔄 Handoff for Next Session
- **Next Step**: Add load tests for the login endpoint under concurrency.
- **Critical Files**:
  - `src/middlewares/auth.ts`
  - `src/tests/load.test.ts`
- **Resume Command**:
> Continue load test implementation for the authentication endpoint in src/tests/load.test.ts.
````
