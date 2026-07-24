# storage/ — RESERVED

**Status:** RESERVED — architectural preparation; **not written to in Phase 1.**

Runtime data directories, designed as **volume mount points** into the backend
container (`/app/storage`) for future file I/O. Contents are git-ignored;
`.gitkeep` files preserve the directory structure.

| Directory | Future purpose |
|-----------|----------------|
| `uploads/` | Inbound KAYAK performance reports and current-bid workbooks |
| `exports/` | Generated Excel export workbooks |
| `reports/` | Generated audit reports |
| `logs/`    | Optional file log sink (Phase 1 logs to stdout only) |

No application code reads or writes these directories in Phase 1.
