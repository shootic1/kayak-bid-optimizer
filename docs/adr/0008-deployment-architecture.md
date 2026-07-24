# 0008. Deployment architecture

- **Status:** Accepted
- **Date:** 2026-07-25

## Context

Frontend and backend must deploy independently and stay fully decoupled, with
distinct dev/staging/production configuration and no deployment-specific business
logic.

## Decision

- **Frontend → Vercel.** Project **Root Directory = `frontend`**; enable
  "Include files outside the Root Directory" so the `@kayak/shared` workspace
  resolves. `frontend/vercel.json` pins install/build to the workspace root.
- **Backend → Railway or Render.** Deploy `backend/Dockerfile`; the platform
  provides managed PostgreSQL and injects `DATABASE_URL`. Health check → `/api/health`.
- **Docker Compose is local development only** — not the production runtime.
- **CI is GitHub Actions; deployment is via the platforms' native Git
  integrations** (no cloud credentials in GitHub). The Actions-based `cd.yml` is
  reserved and disabled.

Environments (dev/staging/production) differ only by configuration; code is
identical. Secrets live in each platform's encrypted store, never in the repo.

## Consequences

- Independent scaling, rollback, and release cadence per tier.
- Decoupling enforced: communication is HTTPS/JSON only; `@kayak/shared` is a
  build-time frontend dependency, not a runtime coupling.

## Alternatives considered

- **Single container/host for both** — rejected: couples the tiers, defeats
  independent deployability.
- **Actions-driven CD now** — deferred: platform Git integrations are simpler and
  keep credentials out of CI for Phase 1.
