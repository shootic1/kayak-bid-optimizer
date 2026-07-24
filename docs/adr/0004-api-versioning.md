# 0004. API versioning (infra-unversioned / app-versioned)

- **Status:** Accepted
- **Date:** 2026-07-25

## Context

The API must evolve without breaking clients, while orchestrators need stable
health probe paths.

## Decision

- **Infrastructure endpoints are unversioned:** `GET /api/health`,
  `GET /api/health/ready`. These are orchestrator/load-balancer contracts that
  remain stable across API versions.
- **Application endpoints are versioned** under `/api/v1`: e.g.
  `GET /api/v1/version`. All future business endpoints live under `/api/v1`;
  breaking changes ship as `/api/v2`.

## Consequences

- Health/readiness paths never churn — safe for Kubernetes/LB probes.
- Clear, additive evolution path for the application API.
- Preserves the originally mandated exact `/api/health` liveness contract.

## Alternatives considered

- **Everything under `/api/v1`** (including health) — rejected: version-independent
  probes should not move when the API version bumps. (Easily reversible: it is a
  one-line change to the router mount prefixes.)
- **Header/media-type versioning** — rejected: path versioning is simpler and
  more discoverable for an internal tool.
