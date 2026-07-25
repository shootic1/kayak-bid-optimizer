"""RouteSummary persistence model — aggregated stats per origin→destination→device."""

from __future__ import annotations

from datetime import date

from sqlalchemy import BigInteger, Date, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.domain.enums import DeviceType
from app.models._column_types import device_type_enum

_Rate = Numeric(10, 4, asdecimal=False)
_Money = Numeric(16, 4, asdecimal=False)


class RouteSummary(Base):
    """Aggregated performance statistics for a single route + device segment."""

    __tablename__ = "route_summaries"
    __table_args__ = (
        UniqueConstraint("origin", "destination", "device", name="uq_route_summary_segment"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    origin: Mapped[str] = mapped_column(String(3), nullable=False)
    destination: Mapped[str] = mapped_column(String(3), nullable=False)
    device: Mapped[DeviceType] = mapped_column(device_type_enum, nullable=False)

    total_reports: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_impressions: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    total_clicks: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    average_ctr: Mapped[float | None] = mapped_column(_Rate, nullable=True)
    average_cpc: Mapped[float | None] = mapped_column(_Money, nullable=True)
    average_position: Mapped[float | None] = mapped_column(_Rate, nullable=True)
    total_spend: Mapped[float] = mapped_column(_Money, nullable=False, default=0)
    total_bookings: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    last_report_date: Mapped[date | None] = mapped_column(Date, nullable=True)
