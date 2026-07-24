# 0001. Monorepo structure

- **Status:** Accepted
- **Date:** 2026-07-25

## Context

The product comprises a Next.js frontend and a FastAPI backend that share
contracts and must evolve together, while remaining independently deployable.

## Decision

Use a single Git monorepo with top-level `frontend/`, `backend/`, `shared/`,
`docs/`, `scripts/`, `docker/`, `storage/`, and `.github/`. The frontend and the
`@kayak/shared` package are pnpm workspace members; the backend is a separate
uv-managed Python project.

## Consequences

- One clone, one CI, atomic cross-cutting changes, shared tooling config.
- Frontend and backend remain **decoupled** and independently deployable.
- Requires clear boundaries so the monorepo does not become a big ball of mud —
  enforced by the layered/feature-first architectures (ADR-0005).

## Alternatives considered

- **Polyrepo** — rejected: cross-contract changes span repos, harder to keep in
  sync for a small team.
- **Nx/Turborepo tooling** — deferred: pnpm workspaces + uv are sufficient for
  Phase 1; heavier orchestration is unjustified (KISS/YAGNI).
