# 0003. Exact version pinning & lock files

- **Status:** Accepted
- **Date:** 2026-07-25

## Context

Reproducible builds across developer machines and CI are essential; floating
ranges introduce non-deterministic upgrades.

## Decision

Pin **exact** versions for all application dependencies (no `^`/`~`). Commit lock
files: `pnpm-lock.yaml` (frontend/shared) and `uv.lock` (backend). CI installs
with `--frozen-lockfile` / `uv sync --frozen`.

Upgrade policy: upgrades are deliberate, reviewed PRs — bump the pin, regenerate
the lock, run the full CI gate. Patch freely, minor with review, major only with
written justification and a stack-wide compatibility check.

## Consequences

- Deterministic, auditable builds; no surprise transitive upgrades.
- Slightly more manual upgrade effort (accepted trade-off).

## Alternatives considered

- Caret/tilde ranges — rejected: non-deterministic across time and machines.
- Renovate/Dependabot auto-merge — deferred; may assist upgrades later but does
  not change the pin-and-lock policy.
