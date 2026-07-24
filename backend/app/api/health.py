"""Unversioned infrastructure health routes.

* ``GET /api/health``       — liveness (process is up).
* ``GET /api/health/ready`` — readiness (process + database are up).

These are UNVERSIONED by design: orchestrators and load balancers point at a
stable path that does not change across API versions (see ADR-0004). Liveness is
dependency-free so "process alive" is distinguishable from "ready to serve".
"""

from __future__ import annotations

from fastapi import APIRouter, Response, status

from app.core.config import settings
from app.schemas.health import HealthResponse, HealthStatus, ReadinessResponse
from app.services.health_service import get_readiness

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, summary="Liveness probe")
async def health() -> HealthResponse:
    """Return service liveness. Does not touch any dependency."""
    return HealthResponse(
        status=HealthStatus.HEALTHY,
        service=settings.SERVICE_NAME,
        version=settings.APP_VERSION,
    )


@router.get(
    "/health/ready",
    response_model=ReadinessResponse,
    summary="Readiness probe",
    responses={503: {"description": "One or more dependencies are unavailable."}},
)
async def readiness(response: Response) -> ReadinessResponse:
    """Return readiness, including a live database connectivity check.

    Responds ``503`` when any dependency is unhealthy so load balancers withhold
    traffic until the service is truly ready.
    """
    result = await get_readiness()
    if result.status is not HealthStatus.HEALTHY:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return result
