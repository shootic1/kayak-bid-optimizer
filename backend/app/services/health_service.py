"""Health/readiness service.

Encapsulates the logic for probing downstream dependencies. Keeping this in a
service (rather than inline in the route) keeps the API layer thin and makes the
checks independently testable.
"""

from __future__ import annotations

import time

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.logging import get_logger
from app.database.session import get_session_factory
from app.schemas.health import DependencyHealth, HealthStatus, ReadinessResponse

logger = get_logger("app.services.health")


async def check_database() -> DependencyHealth:
    """Verify database connectivity with a lightweight ``SELECT 1``.

    Never raises — connectivity problems are reported as an ``unhealthy``
    dependency so the readiness endpoint can return a structured response.
    """
    factory = get_session_factory()
    start = time.perf_counter()
    try:
        async with factory() as session:
            await session.execute(text("SELECT 1"))
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        return DependencyHealth(
            name="database",
            status=HealthStatus.HEALTHY,
            detail="connection ok",
            latency_ms=latency_ms,
        )
    except (SQLAlchemyError, OSError) as exc:
        logger.warning("database_healthcheck_failed", error=str(exc))
        return DependencyHealth(
            name="database",
            status=HealthStatus.UNHEALTHY,
            detail="connection failed",
        )


async def get_readiness() -> ReadinessResponse:
    """Aggregate dependency checks into an overall readiness response."""
    dependencies = [await check_database()]
    overall = (
        HealthStatus.HEALTHY
        if all(dep.status is HealthStatus.HEALTHY for dep in dependencies)
        else HealthStatus.UNHEALTHY
    )
    return ReadinessResponse(
        status=overall,
        service=settings.SERVICE_NAME,
        version=settings.APP_VERSION,
        dependencies=dependencies,
    )
