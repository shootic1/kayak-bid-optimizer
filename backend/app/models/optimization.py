"""Optimization run, recommendation, and rule-result persistence models."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.domain.enums import (
    ConfidenceLevel,
    DeviceType,
    MatchStatus,
    RecommendationAction,
    RunStatus,
)
from app.models._column_types import (
    confidence_level_enum,
    device_type_enum,
    match_status_enum,
    recommendation_action_enum,
    run_status_enum,
)

_Money = Numeric(14, 4, asdecimal=False)
_Rate = Numeric(10, 4, asdecimal=False)


class OptimizationRun(Base):
    """One execution of the recommendation engine over a bid file."""

    __tablename__ = "optimization_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    bid_file_id: Mapped[int] = mapped_column(
        ForeignKey("bid_files.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[RunStatus] = mapped_column(run_status_enum, nullable=False, index=True)
    ruleset_version: Mapped[str] = mapped_column(String(64), nullable=False)

    total_routes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    matched_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    unmatched_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    skipped_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    recommendation_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    error_message: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    recommendations: Mapped[list[BidRecommendation]] = relationship(
        back_populates="run", cascade="all, delete-orphan", passive_deletes=True
    )


class BidRecommendation(Base):
    """A recommended bid for one matched route within an optimization run."""

    __tablename__ = "bid_recommendations"

    id: Mapped[int] = mapped_column(primary_key=True)
    optimization_run_id: Mapped[int] = mapped_column(
        ForeignKey("optimization_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    bid_file_route_id: Mapped[int] = mapped_column(
        ForeignKey("bid_file_routes.id", ondelete="CASCADE"), nullable=False
    )
    route_summary_id: Mapped[int | None] = mapped_column(
        ForeignKey("route_summaries.id", ondelete="SET NULL"), nullable=True
    )

    match_status: Mapped[MatchStatus] = mapped_column(match_status_enum, nullable=False, index=True)
    origin: Mapped[str] = mapped_column(String(64), nullable=False)
    destination: Mapped[str] = mapped_column(String(64), nullable=False)
    device: Mapped[DeviceType | None] = mapped_column(device_type_enum, nullable=True)

    # Deterministic engine output.
    action: Mapped[RecommendationAction] = mapped_column(
        recommendation_action_enum, nullable=False, index=True
    )
    rule_triggered: Mapped[str | None] = mapped_column(String(64), nullable=True)
    confidence_level: Mapped[ConfidenceLevel | None] = mapped_column(
        confidence_level_enum, nullable=True
    )
    manual_review: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    current_bid: Mapped[float | None] = mapped_column(_Money, nullable=True)
    recommended_bid: Mapped[float | None] = mapped_column(_Money, nullable=True)
    difference: Mapped[float | None] = mapped_column(_Money, nullable=True)
    pct_change: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Metric snapshot captured at recommendation time.
    current_position: Mapped[float | None] = mapped_column(_Rate, nullable=True)
    ctr: Mapped[float | None] = mapped_column(_Rate, nullable=True)
    clicks: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    impressions: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    spend: Mapped[float | None] = mapped_column(_Money, nullable=True)

    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    reason: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    run: Mapped[OptimizationRun] = relationship(back_populates="recommendations")
    rule_results: Mapped[list[RuleResult]] = relationship(
        back_populates="recommendation", cascade="all, delete-orphan", passive_deletes=True
    )


class RuleResult(Base):
    """The outcome of a single rule contributing to a recommendation."""

    __tablename__ = "rule_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    bid_recommendation_id: Mapped[int] = mapped_column(
        ForeignKey("bid_recommendations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    rule_key: Mapped[str] = mapped_column(String(64), nullable=False)
    rule_version: Mapped[str] = mapped_column(String(32), nullable=False)
    triggered: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    signal: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    detail: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict)

    recommendation: Mapped[BidRecommendation] = relationship(back_populates="rule_results")
