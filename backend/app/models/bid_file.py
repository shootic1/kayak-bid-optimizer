"""Bid-file persistence models: an uploaded KAYAK bid workbook and its routes."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    LargeBinary,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.domain.enums import FileType
from app.models._column_types import file_type_enum

_Money = Numeric(14, 4, asdecimal=False)


class BidFile(Base):
    """An uploaded KAYAK bid workbook (Search Terms + Mode sheets)."""

    __tablename__ = "bid_files"

    id: Mapped[int] = mapped_column(primary_key=True)
    provider_code: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    mode: Mapped[str] = mapped_column(String(32), nullable=False, default="Full")
    original_filename: Mapped[str] = mapped_column(String(512), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    file_type: Mapped[FileType] = mapped_column(file_type_enum, nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    route_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # The raw uploaded workbook bytes, kept so exports survive container restarts
    # (the local UPLOAD_DIR is ephemeral on Railway). Deferred: never loaded by
    # normal list/get queries — only when explicitly accessed for an export.
    content: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True, deferred=True)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    routes: Mapped[list[BidFileRoute]] = relationship(
        back_populates="bid_file", cascade="all, delete-orphan", passive_deletes=True
    )


class BidFileRoute(Base):
    """A single parsed route (row) from a bid workbook's Search Terms sheet."""

    __tablename__ = "bid_file_routes"
    __table_args__ = (
        UniqueConstraint("bid_file_id", "origin", "destination", name="uq_bid_route_segment"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    bid_file_id: Mapped[int] = mapped_column(
        ForeignKey("bid_files.id", ondelete="CASCADE"), nullable=False, index=True
    )
    row_index: Mapped[int] = mapped_column(Integer, nullable=False)
    provider_code: Mapped[str] = mapped_column(String(128), nullable=False)
    origin: Mapped[str] = mapped_column(String(64), nullable=False)
    destination: Mapped[str] = mapped_column(String(64), nullable=False)
    excluded: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    current_override_cpc: Mapped[float | None] = mapped_column(_Money, nullable=True)
    origin_is_iata: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    destination_is_iata: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    bid_file: Mapped[BidFile] = relationship(back_populates="routes")
