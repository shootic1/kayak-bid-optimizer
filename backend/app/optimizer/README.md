# app/optimizer

Pure bid-optimization logic. No database, HTTP, or I/O — everything here is
deterministic and unit-testable in isolation. The `OptimizationService`
(`app/services/optimization_service.py`) orchestrates these pieces; this package
holds the algorithms.

## Modules

- **`config.py`** — all strategy thresholds as frozen dataclasses
  (`RecommendationConfig`): device bid limits, CTR bands, increase percentages,
  data-sufficiency minimums, and confidence thresholds. No magic numbers live in
  the logic; change a rule here.
- **`rules.py`** — small pure helpers: CTR classification, increase percentage
  and rule-trigger lookup, confidence scoring, device derivation from the
  provider code, and bid clamping to device limits.
- **`recommendation.py`** — the `RecommendationEngine`. Given a device, current
  bid, and route metrics, it returns a `Recommendation` (action, recommended
  bid, reason, rule triggered, confidence, manual-review flag).
- **`matching.py`** — matches bid-file routes to historical `RouteSummary` data
  (matched / no-history / non-IATA / excluded).
- **`metrics.py`** — the `RouteMetrics` value object passed into the engine.
- **`bid_file_parser.py`** — parses uploaded KAYAK bid-file worksheets.
- **`excel_export.py`** — rewrites a bid workbook's Override CPC column in place
  from a set of updates, preserving every other cell, style, formula, sheet, and
  piece of metadata. It only applies decisions; `ExportService` decides which
  routes get a new bid (INCREASE only).

## Determinism

The engine is fully deterministic: the same input always yields the same output.
No AI, no randomization, and no heuristics outside the strategy defined in
`config.py`. The `ruleset_version` (`RecommendationConfig.version`) is recorded
on every optimization run for traceability.

## Strategy (KAYAK Position #1)

Primary objective: reach Average Position #1 while respecting device bid limits.
Order of evaluation per route:

1. Missing/invalid metrics → `MANUAL_REVIEW`.
2. Impressions below minimum → `INSUFFICIENT_DATA`.
3. Clicks below minimum → `INSUFFICIENT_DATA`.
4. Already at Position #1 → `KEEP`.
5. Current bid at the device maximum → `MANUAL_REVIEW`.
6. Failed to reach Position #1 after three runs → `MANUAL_REVIEW`.
7. Very Poor CTR → `MANUAL_REVIEW`.
8. Otherwise → `INCREASE` by the CTR-classified percentage, clamped to the
   device's `[minimum, maximum]` range.

Bids are never automatically reduced — the only actions are `KEEP`, `INCREASE`,
`MANUAL_REVIEW`, and `INSUFFICIENT_DATA`.
