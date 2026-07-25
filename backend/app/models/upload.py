"""Upload persistence model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.domain.enums import FileType, UploadStatus
from app.models._column_types import file_type_enum, upload_status_enum

if TYPE_CHECKING:
    from app.models.performance_report import PerformanceReport


class Upload(Base):
    """A single uploaded source file and the outcome of importing it."""

    __tablename__ = "uploads"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Stored (on-disk) filename and the client's original filename.
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(512), nullable=False)

    file_type: Mapped[FileType] = mapped_column(file_type_enum, nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)

    # SHA-256 hex digest; unique to prevent duplicate uploads.
    checksum: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)

    upload_status: Mapped[UploadStatus] = mapped_column(
        upload_status_enum,
        nullable=False,
        default=UploadStatus.PENDING,
        index=True,
    )

    # Detected report type (populated during processing).
    report_type: Mapped[str | None] = mapped_column(String(32), nullable=True)

    # --- Import result metrics (populated when processing completes) ---------
    imported_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    skipped_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    processing_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # List of {"row": int, "field": str, "message": str} validation errors.
    validation_errors: Mapped[list[dict[str, object]]] = mapped_column(
        JSONB, nullable=False, default=list
    )
    # Populated when upload_status == FAILED.
    error_message: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    # --- Timestamps ----------------------------------------------------------
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    reports: Mapped[list[PerformanceReport]] = relationship(
        back_populates="upload", cascade="all, delete-orphan", passive_deletes=True
    )

    @property
    def error_count(self) -> int:
        """Number of recorded row validation errors."""
        return len(self.validation_errors)
