# syntax=docker/dockerfile:1
# ---------------------------------------------------------------------------
# KAYAK Bid Optimizer Pro — Backend image (Python 3.13 + uv)
# Multi-stage: dependencies are resolved from the committed uv.lock, then the
# project is installed into an isolated virtualenv copied into a slim runtime.
# ---------------------------------------------------------------------------

FROM python:3.13-slim AS base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
# Pinned uv, copied from the official image (matches local toolchain).
COPY --from=ghcr.io/astral-sh/uv:0.11.32 /uv /uvx /bin/

# ---- Builder: create the .venv from the frozen lockfile --------------------
FROM base AS builder
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy
# Install dependencies first (layer cached on the lockfile) without the project.
# No BuildKit cache mounts: uses only portable Docker features so the image
# builds on Railway/Render's builder as well as locally. UV_NO_CACHE keeps the
# image lean since a persistent uv cache is not available without a cache mount.
ENV UV_NO_CACHE=1
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev
# Then install the project itself.
COPY . .
RUN uv sync --frozen --no-dev

# ---- Runner: minimal runtime as a non-root user ---------------------------
FROM base AS runner
WORKDIR /app
RUN groupadd --system app && useradd --system --gid app --uid 1001 app
COPY --from=builder --chown=app:app /app /app
ENV PATH="/app/.venv/bin:$PATH"
USER app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
