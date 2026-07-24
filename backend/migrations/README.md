# backend/migrations — RESERVED (Alembic architecture only)

**Status:** RESERVED — architectural preparation. **No migrations are authored
and Alembic is not executed in Phase 1** (there are no tables).

## Intended architecture

- `alembic.ini` (backend root) — Alembic configuration.
- `migrations/env.py` — binds Alembic to `app.models.base.Base.metadata` and the
  async engine from `app.database.session`, supporting offline and online modes.
- `migrations/versions/` — revision scripts (empty in Phase 1).

The declarative base defines an explicit constraint **naming convention**
(`app/database/base.py`) so future `alembic revision --autogenerate` diffs are
stable.

## When the first table arrives (future phase)

```bash
uv run alembic revision --autogenerate -m "create <table>"
uv run alembic upgrade head
```
