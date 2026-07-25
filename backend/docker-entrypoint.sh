#!/bin/sh
# Container entrypoint: apply database migrations, then start the server.
# Runs on every deploy (Railway/Render/local Compose). `alembic upgrade head`
# is idempotent — a no-op when the database is already at the latest revision.
set -e

echo "[entrypoint] Applying database migrations (alembic upgrade head)…"
alembic upgrade head

echo "[entrypoint] Migrations complete. Starting application…"
exec "$@"
