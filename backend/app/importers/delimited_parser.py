"""Delimited-text parsers (CSV and TSV) sharing one implementation."""

from __future__ import annotations

import csv
from pathlib import Path

from app.domain.enums import FileType
from app.importers.base import BaseParser, ParsedTable, ParseError


class DelimitedParser(BaseParser):
    """Shared CSV/TSV parser; subclasses only set the delimiter and file type."""

    delimiter: str

    def parse(self, path: Path) -> ParsedTable:
        try:
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                reader = csv.reader(handle, delimiter=self.delimiter)
                rows = list(reader)
        except (OSError, csv.Error, UnicodeDecodeError) as exc:
            raise ParseError(f"could not read delimited file: {exc}") from exc

        if not rows:
            return ParsedTable(headers=[], rows=[])

        headers = [cell.strip() for cell in rows[0]]
        raw_rows: list[list[object]] = [list(row) for row in rows[1:]]
        return ParsedTable(headers=headers, rows=self._build_rows(headers, raw_rows))


class CsvParser(DelimitedParser):
    """Comma-separated values."""

    file_type = FileType.CSV
    delimiter = ","


class TsvParser(DelimitedParser):
    """Tab-separated values."""

    file_type = FileType.TSV
    delimiter = "\t"
