# 0009. uv for Python dependency management

- **Status:** Accepted
- **Date:** 2026-07-25

## Context

The backend needs fast, reproducible dependency management with an exact,
hash-locked graph and a single declarative manifest.

## Decision

Use **uv** with `pyproject.toml` (PEP 621 `[project]` dependencies + PEP 735
`[dependency-groups].dev`) and a committed **`uv.lock`** (exact versions + hashes
for the full transitive graph). Tool config (ruff, mypy, pytest) also lives in
`pyproject.toml`. The Docker image builds with a pinned uv via a multi-stage
`uv sync --frozen` flow. `requirements.txt` is not used.

## Consequences

- Fast, deterministic installs locally, in CI, and in Docker.
- One manifest for dependencies + tooling; hash-verified reproducibility.
- Contributors must install uv (documented in README).

## Alternatives considered

- **pip + requirements.txt** — rejected: weaker locking (no hashes/graph by
  default), split manifests.
- **Poetry / PDM** — rejected: uv is faster and consolidates the workflow;
  fewer moving parts for Docker.
