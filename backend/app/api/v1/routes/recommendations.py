"""Recommendations API — list and inspect bid recommendations."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.database.session import get_db_session
from app.domain.enums import MatchStatus
from app.repositories.optimization_repository import BidRecommendationRepository
from app.schemas.optimization import (
    RecommendationDetail,
    RecommendationListResponse,
    RecommendationRead,
)

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

DbSession = Annotated[AsyncSession, Depends(get_db_session)]


@router.get("", response_model=RecommendationListResponse, summary="List recommendations")
async def list_recommendations(
    session: DbSession,
    run_id: Annotated[int | None, Query()] = None,
    status: Annotated[MatchStatus | None, Query()] = None,
    min_confidence: Annotated[float | None, Query(ge=0.0, le=1.0)] = None,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> RecommendationListResponse:
    items, total = await BidRecommendationRepository(session).list_page(
        limit=limit,
        offset=offset,
        run_id=run_id,
        status=status,
        min_confidence=min_confidence,
    )
    return RecommendationListResponse(
        items=[RecommendationRead.model_validate(r) for r in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{recommendation_id}", response_model=RecommendationDetail, summary="Get one")
async def get_recommendation(session: DbSession, recommendation_id: int) -> RecommendationDetail:
    rec = await BidRecommendationRepository(session).get_with_rules(recommendation_id)
    if rec is None:
        raise NotFoundError(f"recommendation {recommendation_id} not found")
    return RecommendationDetail.model_validate(rec)
