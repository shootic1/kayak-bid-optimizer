# 0002. Technology stack & version strategy

- **Status:** Accepted
- **Date:** 2026-07-25

## Context

We need a modern, maintainable, well-supported stack with a large hiring pool,
while avoiding the instability of brand-new major releases.

## Decision

- **Frontend:** Next.js 16 (App Router), React 19, TypeScript 5.9, Tailwind CSS
  4, shadcn/ui, React Hook Form + Zod, pnpm.
- **Backend:** Python 3.13, FastAPI, Pydantic v2, SQLAlchemy 2 (async) + asyncpg,
  structlog, uv (ADR-0009).
- **Database:** PostgreSQL 16 (Docker for local dev).

Where the newest major of a tool was only days old, we deliberately chose the
proven line: **TypeScript 5.9 (not 7.x)**, **ESLint 9 (not 10)**, **lucide-react
0.x (not 1.x)**, **mypy 1.x (not 2.x)**.

## Consequences

- Current, capable stack aligned with the mandated Next 16 / React 19.
- Lower risk from unvetted majors; ecosystem/tooling compatibility maximized.

## Alternatives considered

- Latest-of-everything — rejected for stability (see the deliberate step-backs).
- Django/Flask backend, Vite SPA frontend, MUI — rejected in the TDD for fit,
  async support, and bundle/lock-in concerns.
