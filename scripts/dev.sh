#!/usr/bin/env bash
# Convenience wrapper for common developer tasks.
# Usage: ./scripts/dev.sh <up|down|logs|verify>
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

cmd="${1:-up}"
case "$cmd" in
  up)
    [ -f .env ] || cp .env.example .env
    docker compose up --build
    ;;
  down)
    docker compose down "${@:2}"
    ;;
  logs)
    docker compose logs -f "${@:2}"
    ;;
  verify)
    echo "== shared ==";   pnpm --filter @kayak/shared typecheck
    echo "== frontend =="; pnpm --filter @kayak/frontend lint && pnpm --filter @kayak/frontend typecheck && pnpm --filter @kayak/frontend build
    echo "== backend ==";  (cd backend && uv run ruff check app tests && uv run mypy app && uv run pytest)
    ;;
  *)
    echo "Usage: ./scripts/dev.sh <up|down|logs|verify>" >&2
    exit 1
    ;;
esac
