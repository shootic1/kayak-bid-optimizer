# KAYAK Bid Optimizer Pro

Internal Online Travel Agency (OTA) tool for optimizing KAYAK Inline Ads and
Dynamic Inline Ads. This repository is a **GitHub monorepo** containing a
decoupled Next.js frontend and FastAPI backend.

> **Phase 1 — Project Foundation.** This is the production-grade *foundation*
> only. It contains **no business logic**: no report import, optimization, Excel
> generation, analytics, authentication, or database tables. See
> [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) and
> [`docs/adr/`](docs/adr/) for the design of record.

---

## Tech stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 16 · React 19 · TypeScript 5.9 · Tailwind CSS 4 · shadcn/ui · React Hook Form · Zod |
| Backend | Python 3.13 · FastAPI · Pydantic v2 · SQLAlchemy 2 (async) · structlog |
| Database | PostgreSQL 16 (Docker Compose) |
| Tooling | pnpm (frontend) · uv (backend) · ESLint · Prettier · Ruff · mypy · Docker |

All application dependency versions are **exact-pinned** and locked
(`pnpm-lock.yaml`, `uv.lock`).

---

## Repository layout

```
kayak-bid-optimizer/
├── shared/      @kayak/shared — cross-cutting types, constants, validation (TS)
├── frontend/    Next.js 16 App Router application (deployable to Vercel)
├── backend/     FastAPI service (Docker; deployable to Railway / Render)
├── docker/      container assets (reserved)
├── storage/     reserved runtime data dirs (uploads/exports/reports/logs)
├── docs/        architecture docs + ADRs
├── scripts/     developer convenience scripts
├── .github/     GitHub Actions CI (+ reserved CD)
└── docker-compose.yml   one-command local dev stack
```

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full tree and rationale.

---

## Prerequisites

- **Node.js** ≥ 22 (validated on 26)
- **pnpm** ≥ 11 — `npm install -g pnpm`
- **Python** 3.13
- **uv** — `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Docker Desktop** (Engine + Compose v2)

---

## Quick start (Docker — recommended)

One command starts the whole stack (frontend + backend + PostgreSQL):

```bash
cp .env.example .env
docker compose up --build
```

- Frontend → http://localhost:3000
- Backend API docs → http://localhost:8000/docs
- Health → http://localhost:8000/api/health
- Version → http://localhost:8000/api/v1/version

Stop with `Ctrl+C`; remove volumes with `docker compose down -v`.

---

## Local development (without Docker)

**Frontend**

```bash
pnpm install
pnpm frontend
```

**Backend**

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

(The backend needs a reachable PostgreSQL. Start just the DB with
`docker compose up db`.)

---

## Quality gates

| Task | Frontend | Backend |
|------|----------|---------|
| Build | `pnpm build` | `docker build backend` |
| Lint | `pnpm lint` | `uv run ruff check .` |
| Format check | `pnpm --filter @kayak/frontend format:check` | `uv run ruff format --check .` |
| Type-check | `pnpm typecheck` | `uv run mypy app` |
| Test | — | `uv run pytest` |

CI runs all of these on every pull request — see
[`.github/workflows/ci.yml`](.github/workflows/ci.yml).

---

## Deployment

Frontend and backend are **completely decoupled** and deploy independently:

- **Frontend → Vercel** (Root Directory `frontend/`).
- **Backend → Railway or Render** (Docker, `backend/Dockerfile`).
- **Docker Compose is local development only** — not the production runtime.

See [`docs/adr/0008-deployment-architecture.md`](docs/adr/0008-deployment-architecture.md).

---

## License

Internal — proprietary. © KAYAK Bid Optimizer Pro.
