"""Pydantic schemas for optimization runs and recommendations."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import (
    ConfidenceLevel,
    DeviceType,
    MatchStatus,
    RecommendationAction,
    RunStatus,
)


class OptimizationRunRequest(BaseModel):
    """Request body to start an optimization run."""

    bid_file_id: int


class OptimizationRunRead(BaseModel):
    """An optimization run and its summary counts."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    bid_file_id: int
    status: RunStatus
    ruleset_version: str
    total_routes: int
    matched_count: int
    unmatched_count: int
    skipped_count: int
    recommendation_count: int
    error_message: str | None
    started_at: datetime
    finished_at: datetime | None


class OptimizationRunListResponse(BaseModel):
    items: list[OptimizationRunRead]
    total: int
    limit: int
    offset: int


class RuleResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rule_key: str
    rule_version: str
    triggered: bool
    weight: float
    signal: float
    detail: dict[str, object]


class RecommendationRead(BaseModel):
    """A bid recommendation (list representation)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    optimization_run_id: int
    bid_file_route_id: int
    route_summary_id: int | None
    match_status: MatchStatus
    origin: str
    destination: str
    device: DeviceType | None
    action: RecommendationAction
    rule_triggered: str | None
    confidence_level: ConfidenceLevel | None
    manual_review: bool
    current_bid: float | None
    recommended_bid: float | None
    difference: float | None
    pct_change: float | None
    current_position: float | None
    ctr: float | None
    clicks: int | None
    impressions: int | None
    spend: float | None
    confidence: float | None
    reason: str | None
    created_at: datetime


class RecommendationDetail(RecommendationRead):
    """A recommendation including the contributing rule results."""

    rule_results: list[RuleResultRead] = Field(default_factory=list)


class RecommendationListResponse(BaseModel):
    items: list[RecommendationRead]
    total: int
    limit: int
    offset: int
