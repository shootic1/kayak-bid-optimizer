# 0007. Reserved async processing

- **Status:** Accepted
- **Date:** 2026-07-25

## Context

Future phases will run long tasks (report import, optimization, export
generation) that should not block HTTP requests.

## Decision

Reserve `app/tasks` (enqueue-able task definitions) and `app/workers` (worker
process entrypoints / queue consumers) as documented, empty scaffolds. A commented
worker service is documented for `docker-compose.yml`. **No queue technology is
chosen and nothing runs in Phase 1.**

## Consequences

- The async topology is anticipated in the structure without premature
  implementation (YAGNI).
- Workers will run as separate deployments off the same backend image.

## Alternatives considered

- **Pick a queue now (Celery / RQ / arq)** — rejected: no workload yet; the
  choice deserves its own ADR when requirements are concrete.
- **Background threads / FastAPI BackgroundTasks only** — insufficient for the
  expected heavy, retryable jobs; revisit per-use-case later.
