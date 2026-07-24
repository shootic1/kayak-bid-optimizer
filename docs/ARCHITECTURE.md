# Architecture Overview

KAYAK Bid Optimizer Pro is a three-tier, decoupled web application delivered as a
GitHub monorepo. This document is the condensed reference; decisions of record
live in [`adr/`](adr/).

## System

```
Browser (Next.js UI) ──HTTPS/JSON──▶ FastAPI backend ──asyncpg──▶ PostgreSQL 16
        ◀── backend & DB status ───           ◀── SELECT 1 ──
```

The frontend never touches the database directly; the backend owns all data
access.

## Frontend (feature-first)

```
frontend/
  app/         App Router: layouts, pages, loading/error/not-found boundaries
  components/  ui/ (shadcn primitives) + shared/ (AppShell, Sidebar, Header, …)
  features/    domain-oriented UI (dashboard, system-status, settings)
  services/    typed API client (validates responses with @kayak/shared Zod schemas)
  lib/ hooks/ types/ styles/
```

- **State:** minimal — local `useState` + a `useSystemStatus` hook; theme via
  `next-themes`. No global store (KISS/YAGNI).
- **Styling:** Tailwind v4 (CSS-first tokens) + shadcn/ui; dark/light via class.

## Backend (layered / clean architecture)

```
api/ (HTTP)  →  services/ (use-cases)  →  domain/ (entities + ports)  →  repositories/  →  models/ + database/
core/ = config, logging, exceptions   |   schemas/ = API contracts (Pydantic)
```

- **API:** unversioned infra health (`/api/health`, `/api/health/ready`) +
  versioned app namespace (`/api/v1/...`). See ADR-0004.
- **Model separation:** API Schemas ≠ Domain Models ≠ Persistence Models (ADR-0005).
- **DI:** FastAPI `Depends` provides request-scoped sessions and cached settings.
- **DB:** async SQLAlchemy engine, pooled, `pool_pre_ping`, disposed on shutdown;
  no business tables in Phase 1.

## Reserved for future phases (inert scaffolds)

`shared` is active. The following are RESERVED (README/`__init__` only, no logic,
not referenced at runtime): `backend/app/{config,observability,plugins,workers,
tasks,optimizer,importers,exporters}`, `backend/migrations`, and
`storage/{uploads,exports,reports,logs}`.

## Cross-cutting

- **Config:** typed `Settings` (backend) / `lib/env` (frontend) — single entry points.
- **Logging:** structlog (backend, console/JSON) + console wrapper (frontend).
- **Errors:** global FastAPI handlers → canonical `{ "error": { code, message } }`;
  React error/not-found boundaries on the frontend.
- **Deployment:** Vercel (frontend) + Railway/Render (backend); Docker Compose is
  local-dev only. See ADR-0008.

For the full design rationale, see the Technical Design Document (v1.2).
