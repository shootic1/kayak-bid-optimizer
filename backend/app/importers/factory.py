"""Parser factory — selects the correct parser for a file type."""

from __future__ import annotations

from app.domain.enums import FileType
from app.importers.base import BaseParser
from app.importers.delimited_parser import CsvParser, TsvParser
from app.importers.excel_parser import ExcelParser

_PARSERS: dict[FileType, type[BaseParser]] = {
    FileType.XLSX: ExcelParser,
    FileType.CSV: CsvParser,
    FileType.TSV: TsvParser,
}


def get_parser(file_type: FileType) -> BaseParser:
    """Return a parser instance for ``file_type``."""
    try:
        return _PARSERS[file_type]()
    except KeyError as exc:  # pragma: no cover - guarded by upload validation
        raise ValueError(f"no parser for file type {file_type!r}") from exc
