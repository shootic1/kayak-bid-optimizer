# KAYAK Bid Optimizer Pro — Backend

FastAPI service (Phase 1 foundation). Python 3.13, managed with **uv**.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Liveness (unversioned infra) |
| GET | `/api/health/ready` | Readiness incl. live DB check (200/503) |
| GET | `/api/v1/version` | Application version/metadata (versioned) |
| GET | `/docs` | OpenAPI (Swagger) UI |

## Local development

```bash
uv sync                       # create .venv from uv.lock
uv run uvicorn app.main:app --reload --port 8000
```

A reachable PostgreSQL is required for the readiness probe to report healthy.
Start just the database with `docker compose up db` from the repo root.

## Quality gates

```bash
uv run ruff check .           # lint
uv run ruff format --check .  # format check
uv run mypy app               # type-check
uv run pytest                 # tests
```

## Architecture (layers)

```
api/ (HTTP)  →  services/ (use-cases)  →  domain/ (entities + ports)  →  repositories/ (persistence)
```

See `../docs/ARCHITECTURE.md` and `../docs/adr/` for the design of record.
Reserved packages (`config`, `observability`, `plugins`, `workers`, `tasks`,
`optimizer`, `importers`, `exporters`) and `migrations/` are inert scaffolds for
future phases.
