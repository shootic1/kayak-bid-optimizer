# Development Guide

## Prerequisites

- Node.js ≥ 22 (validated on 26), pnpm 11, Python 3.13, uv, Docker Desktop.

## First-time setup

```bash
cp .env.example .env
pnpm install            # installs frontend + shared workspaces
cd backend && uv sync   # creates backend/.venv from uv.lock
```

## Run everything (Docker — recommended)

```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend docs: http://localhost:8000/docs
- Health: http://localhost:8000/api/health · Version: http://localhost:8000/api/v1/version

`docker compose down` stops; add `-v` to drop the database volume.

## Run services individually

```bash
pnpm frontend                                        # Next.js dev server
docker compose up db                                 # just PostgreSQL
cd backend && uv run uvicorn app.main:app --reload   # FastAPI (needs a DB)
```

## Quality gates

Frontend / shared:

```bash
pnpm --filter @kayak/shared typecheck
pnpm --filter @kayak/frontend lint
pnpm --filter @kayak/frontend format:check
pnpm --filter @kayak/frontend typecheck
pnpm --filter @kayak/frontend build
```

Backend (from `backend/`):

```bash
uv run ruff check app tests
uv run ruff format --check app tests
uv run mypy app
uv run pytest
```

CI runs all of the above on every PR (`.github/workflows/ci.yml`).

## Conventions

- **TypeScript:** strict, no `any`; `PascalCase` components, `camelCase` values;
  import shared contracts from `@kayak/shared`.
- **Python:** full type hints, `from __future__ import annotations`; Ruff + mypy
  (strict) enforced; layered imports only (routes → services → domain → repositories).
- **Reserved dirs** stay empty (README/`__init__` only) until their phase.

## Adding a new backend endpoint (future)

1. Define an API Schema in `app/schemas`.
2. Add a route module under `app/api/v1/routes` and include it in `app/api/v1/router.py`.
3. Put orchestration in `app/services`; data access behind a repository/domain port.
4. Add tests under `tests/`.
