# docker/postgres/ — RESERVED

**Status:** RESERVED — architectural preparation.

Reserved location for PostgreSQL container initialization scripts (e.g.
`init.sql` seed/extension scripts mounted into `/docker-entrypoint-initdb.d/`).

Phase 1 creates **no business tables** and no init scripts — the database
connection is verified only. Any future initialization SQL will live here and be
wired into `docker-compose.yml`.
