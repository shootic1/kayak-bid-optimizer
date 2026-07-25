"""PerformanceReport persistence model — one normalized report row."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Date,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.domain.enums import DeviceType, ReportType
from app.models._column_types import device_type_enum, report_type_enum

if TYPE_CHECKING:
    from app.models.upload import Upload

# Numeric columns are stored with fixed scale but surfaced as floats
# (asdecimal=False) to keep JSON serialization simple and consistent.
_Rate = Numeric(10, 4, asdecimal=False)
_Money = Numeric(14, 4, asdecimal=False)


class PerformanceReport(Base):
    """A single normalized performance row imported from a KAYAK report."""

    __tablename__ = "performance_reports"
    __table_args__ = (Index("ix_performance_reports_route", "origin", "destination", "device"),)

    id: Mapped[int] = mapped_column(primary_key=True)

    upload_id: Mapped[int] = mapped_column(
        ForeignKey("uploads.id", ondelete="CASCADE"), nullable=False, index=True
    )

    report_type: Mapped[ReportType] = mapped_column(report_type_enum, nullable=False)
    report_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    origin: Mapped[str] = mapped_column(String(3), nullable=False)
    destination: Mapped[str] = mapped_column(String(3), nullable=False)
    device: Mapped[DeviceType] = mapped_column(device_type_enum, nullable=False)

    impressions: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    clicks: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    ctr: Mapped[float | None] = mapped_column(_Rate, nullable=True)
    avg_cpc: Mapped[float | None] = mapped_column(_Money, nullable=True)
    spend: Mapped[float] = mapped_column(_Money, nullable=False, default=0)
    # Nullable: real KAYAK reports have no bookings column (store NULL, not 0).
    bookings: Mapped[int | None] = mapped_column(Integer, nullable=True)
    avg_position: Mapped[float | None] = mapped_column(_Rate, nullable=True)

    upload: Mapped[Upload] = relationship(back_populates="reports")
