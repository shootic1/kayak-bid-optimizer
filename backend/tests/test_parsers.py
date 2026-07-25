"""Parser tests for Excel, CSV, and TSV (real KAYAK structure)."""

from __future__ import annotations

from pathlib import Path

import pytest
from tests import samples

from app.domain.enums import FileType
from app.importers.base import ParseError
from app.importers.delimited_parser import CsvParser, TsvParser
from app.importers.excel_parser import ExcelParser
from app.importers.factory import get_parser


def test_factory_returns_correct_parser() -> None:
    assert isinstance(get_parser(FileType.XLSX), ExcelParser)
    assert isinstance(get_parser(FileType.CSV), CsvParser)
    assert isinstance(get_parser(FileType.TSV), TsvParser)


def test_tsv_parser_reads_real_inline_headers_and_rows(tmp_path: Path) -> None:
    path = tmp_path / "inline.tsv"
    path.write_bytes(samples.inline_tsv_bytes())

    table = TsvParser().parse(path)

    assert table.headers == samples.INLINE_HEADERS
    assert len(table.rows) == len(samples.INLINE_ROWS)
    assert table.rows[0]["Origin"] == "JFK"
    assert table.rows[0]["Est. Impressions"] == "1000"


def test_csv_parser_reads_legacy_rows(tmp_path: Path) -> None:
    path = tmp_path / "legacy.csv"
    path.write_bytes(samples.legacy_csv_bytes())

    table = CsvParser().parse(path)

    assert table.headers == samples.LEGACY_HEADERS
    assert table.rows[1]["Destination"] == "SFO"


def test_excel_parser_reads_real_inline_rows(tmp_path: Path) -> None:
    path = tmp_path / "inline.xlsx"
    path.write_bytes(samples.inline_xlsx_bytes())

    table = ExcelParser().parse(path)

    assert table.headers == samples.INLINE_HEADERS
    assert table.rows[0]["Destination"] == "LAX"


def test_excel_parser_rejects_non_excel(tmp_path: Path) -> None:
    path = tmp_path / "bad.xlsx"
    path.write_bytes(b"this is not a zip archive")
    with pytest.raises(ParseError):
        ExcelParser().parse(path)
