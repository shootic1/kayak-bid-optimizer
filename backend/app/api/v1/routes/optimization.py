"""Optimization API — start and inspect optimization runs."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.schemas.optimization import (
    ExportSummary,
    OptimizationRunListResponse,
    OptimizationRunRead,
    OptimizationRunRequest,
)
from app.services.export_service import ExportService
from app.services.optimization_service import OptimizationService

router = APIRouter(prefix="/optimization", tags=["optimization"])

DbSession = Annotated[AsyncSession, Depends(get_db_session)]

XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@router.post(
    "/run",
    response_model=OptimizationRunRead,
    status_code=status.HTTP_201_CREATED,
    summary="Run optimization over a bid file",
)
async def start_run(session: DbSession, body: OptimizationRunRequest) -> OptimizationRunRead:
    run = await OptimizationService(session).run(body.bid_file_id)
    await session.commit()
    await session.refresh(run)
    return OptimizationRunRead.model_validate(run)


@router.get("/runs", response_model=OptimizationRunListResponse, summary="List runs")
async def list_runs(
    session: DbSession,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> OptimizationRunListResponse:
    runs, total = await OptimizationService(session).list_runs(limit=limit, offset=offset)
    return OptimizationRunListResponse(
        items=[OptimizationRunRead.model_validate(r) for r in runs],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/runs/{run_id}", response_model=OptimizationRunRead, summary="Get a run")
async def get_run(session: DbSession, run_id: int) -> OptimizationRunRead:
    run = await OptimizationService(session).get_run(run_id)
    return OptimizationRunRead.model_validate(run)


@router.get(
    "/runs/{run_id}/export/summary",
    response_model=ExportSummary,
    summary="Preview the export summary without downloading",
)
async def export_summary(session: DbSession, run_id: int) -> ExportSummary:
    result = await ExportService(session).build_export(run_id)
    return result.summary


@router.get(
    "/runs/{run_id}/export",
    response_class=Response,
    summary="Download the optimized KAYAK upload workbook",
)
async def export_run(session: DbSession, run_id: int) -> Response:
    result = await ExportService(session).build_export(run_id)
    return Response(
        content=result.content,
        media_type=XLSX_MEDIA_TYPE,
        headers={"Content-Disposition": f'attachment; filename="{result.filename}"'},
    )
