"""Sample KAYAK bid workbook builder for tests (real structure)."""

from __future__ import annotations

import io

from openpyxl import Workbook

PROVIDER = "CheapTicketsDealM_FIOAD_US"

# (origin, destination, excluded, override_cpc)
DEFAULT_ROUTES: list[tuple[str, str, str, str]] = [
    ("JFK", "LAX", "false", "1.6"),  # matches seeded history
    ("JFK", "SFO", "false", "1.4"),  # matches seeded history
    ("ABE", "AUA", "false", "1.5"),  # valid IATA, no seeded history -> unmatched_no_history
    ("New York, NY", "MIA", "false", "1.7"),  # non-IATA origin -> unmatched_non_iata
    ("BOS", "MIA", "true", "1.8"),  # excluded -> skipped
]


def bid_xlsx_bytes(
    provider: str = PROVIDER,
    routes: list[tuple[str, str, str, str]] | None = None,
    mode: str = "Full",
) -> bytes:
    """Build a bid workbook. Provider Code is set only on the first data row,
    matching the real KAYAK export."""
    rows = routes if routes is not None else DEFAULT_ROUTES
    workbook = Workbook()
    search = workbook.active
    assert search is not None
    search.title = "Search Terms"
    search.append(["Provider Code", "Origin", "Destination", "Excluded", "Override CPC"])
    for index, (origin, destination, excluded, cpc) in enumerate(rows):
        provider_cell = provider if index == 0 else None
        search.append([provider_cell, origin, destination, excluded, cpc])

    mode_sheet = workbook.create_sheet("Mode")
    mode_sheet.append(["Mode", mode])
    mode_sheet.append(["Provider Code", provider])

    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()
