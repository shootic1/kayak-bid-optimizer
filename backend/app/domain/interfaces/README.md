# app/domain/interfaces — Ports (Dependency-Inversion seam)

Repository and service **Ports** expressed as `typing.Protocol`. Services depend
on these abstractions; `app/repositories` provides the implementations. The
pattern is established here in Phase 1; no concrete ports are required until
business entities exist.
