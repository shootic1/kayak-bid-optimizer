"""Parser abstractions and shared types.

A parser turns a source file into a :class:`ParsedTable` (headers + row dicts).
Row values are returned as-is (strings, numbers, dates); normalization happens
later in the import engine, so parsers contain no business logic.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from pathlib import Path

from app.domain.enums import FileType


class ParseError(Exception):
    """Raised when a source file cannot be read/parsed at all."""


@dataclass(frozen=True)
class ParsedTable:
    """The tabular contents of a parsed source file."""

    headers: list[str]
    rows: list[dict[str, object]] = field(default_factory=list)


class BaseParser(abc.ABC):
    """Base class for all file parsers."""

    #: File type this parser handles.
    file_type: FileType

    @abc.abstractmethod
    def parse(self, path: Path) -> ParsedTable:
        """Parse ``path`` into a :class:`ParsedTable`."""
        raise NotImplementedError

    @staticmethod
    def _build_rows(headers: list[str], raw_rows: list[list[object]]) -> list[dict[str, object]]:
        """Zip header labels with each raw row into a dict (shared helper)."""
        rows: list[dict[str, object]] = []
        for raw in raw_rows:
            row = {headers[i]: raw[i] if i < len(raw) else None for i in range(len(headers))}
            rows.append(row)
        return rows
