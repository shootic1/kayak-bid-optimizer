# 0006. Shared workspace package

- **Status:** Accepted
- **Date:** 2026-07-25

## Context

Frontend code needs one source of truth for API contracts, constants, and
validation to avoid drift.

## Decision

Create `@kayak/shared`, a pnpm workspace package holding constants, TypeScript
types, and Zod validation schemas. Types are **derived from** the Zod schemas
(single source of truth). The frontend consumes it via `workspace:*` and Next's
`transpilePackages` (source-compiled, no prebuilt dist required at dev time).

## Consequences

- DRY contracts/constants for the frontend; validation and types cannot drift.
- **Known limitation:** the package is TypeScript, so the Python backend cannot
  import it. Contract parity with the backend's Pydantic schemas is maintained by
  convention and review in Phase 1.

## Alternatives considered

- **Duplicate types in frontend + backend** — rejected: drift risk.
- **Language-neutral canonical contract** (JSON Schema generating both TS types
  and Pydantic models) — deferred to a future ADR; adds tooling not warranted in
  Phase 1 (YAGNI).
