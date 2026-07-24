# 0005. Clean architecture & domain layer

- **Status:** Accepted
- **Date:** 2026-07-25

## Context

The backend will grow real domain complexity (reports, bids, optimization). We
want dependencies to point inward and to keep transport, domain, and persistence
concerns separate.

## Decision

Adopt layered / clean architecture:

```
api/ (HTTP) → services/ (use-cases) → domain/ (entities + ports) → repositories/ (persistence) → models/database
```

Maintain three distinct model families that never cross boundaries:

- **API Schemas** — `app/schemas` (Pydantic, transport).
- **Domain Models** — `app/domain/entities`, `value_objects` (framework-free).
- **Persistence Models** — `app/models` (SQLAlchemy).

Services depend on domain **Ports** (`app/domain/interfaces`, `typing.Protocol`);
repositories implement them (Dependency Inversion).

## Consequences

- Testable use-cases (fake repositories via ports), no DB shape leaking to HTTP.
- More layers/mapping code — justified by long-term maintainability.
- In Phase 1 only API Schemas are populated; domain & persistence families are
  empty, documented boundaries.

## Alternatives considered

- **Active Record / fat models** — rejected: couples transport, domain, and
  persistence; hard to test and evolve.
