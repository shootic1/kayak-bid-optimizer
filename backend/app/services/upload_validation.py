"""Pure validation helpers for uploaded files (extension, size, MIME/content)."""

from __future__ import annotations

from pathlib import PurePath

from app.core.exceptions import (
    PayloadTooLargeError,
    UnsupportedMediaTypeError,
)
from app.domain.enums import EXTENSION_TO_FILE_TYPE, FileType

# Accepted declared MIME types per file type. Kept permissive because browsers
# frequently send ``application/octet-stream`` for these formats; the content
# sniff below is the authoritative check.
_ALLOWED_CONTENT_TYPES: dict[FileType, frozenset[str]] = {
    FileType.XLSX: frozenset(
        {
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-excel",
            "application/zip",
            "application/octet-stream",
            "",
        }
    ),
    FileType.CSV: frozenset(
        {"text/csv", "application/csv", "text/plain", "application/octet-stream", ""}
    ),
    FileType.TSV: frozenset(
        {"text/tab-separated-values", "text/csv", "text/plain", "application/octet-stream", ""}
    ),
}

# .xlsx is a ZIP archive; it always begins with the local-file-header signature.
_ZIP_MAGIC = b"PK\x03\x04"


def resolve_file_type(filename: str) -> FileType:
    """Map a filename's extension to a :class:`FileType`, or raise 415."""
    ext = PurePath(filename).suffix.lower().lstrip(".")
    file_type = EXTENSION_TO_FILE_TYPE.get(ext)
    if file_type is None:
        raise UnsupportedMediaTypeError(
            f"unsupported file extension '.{ext}'; allowed: .xlsx, .csv, .tsv"
        )
    return file_type


def validate_size(size: int, max_size: int) -> None:
    """Reject empty or oversized files."""
    if size <= 0:
        raise UnsupportedMediaTypeError("the uploaded file is empty")
    if size > max_size:
        raise PayloadTooLargeError(f"file is {size} bytes; maximum allowed is {max_size} bytes")


def validate_content(file_type: FileType, content_type: str, data: bytes) -> None:
    """Validate the declared MIME type and sniff the file contents."""
    allowed = _ALLOWED_CONTENT_TYPES[file_type]
    declared = (content_type or "").split(";")[0].strip().lower()
    if declared not in allowed:
        raise UnsupportedMediaTypeError(
            f"content type '{declared}' is not valid for a {file_type.value} file"
        )

    if file_type is FileType.XLSX:
        if not data.startswith(_ZIP_MAGIC):
            raise UnsupportedMediaTypeError("file is not a valid .xlsx (Excel) document")
    else:
        # Delimited formats must be UTF-8 decodable text without NUL bytes.
        if b"\x00" in data[:4096]:
            raise UnsupportedMediaTypeError("file does not appear to be valid text")
        try:
            data[:4096].decode("utf-8")
        except UnicodeDecodeError as exc:
            raise UnsupportedMediaTypeError("file is not valid UTF-8 text") from exc
