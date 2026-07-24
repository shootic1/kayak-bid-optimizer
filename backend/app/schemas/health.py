"""Pydantic response schemas for health and readiness endpoints."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class HealthStatus(StrEnum):
    """Overall health state of the service or a dependency."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthResponse(BaseModel):
    """Liveness response — confirms the process is up and serving requests."""

    status: HealthStatus = Field(examples=[HealthStatus.HEALTHY])
    service: str = Field(examples=["backend"])
    version: str = Field(examples=["1.0.0"])


class DependencyHealth(BaseModel):
    """Health of a single downstream dependency (e.g. the database)."""

    name: str = Field(examples=["database"])
    status: HealthStatus = Field(examples=[HealthStatus.HEALTHY])
    detail: str | None = Field(default=None, examples=["connection ok"])
    latency_ms: float | None = Field(default=None, examples=[3.42])


class ReadinessResponse(BaseModel):
    """Readiness response — confirms the service and its dependencies are ready."""

    status: HealthStatus
    service: str
    version: str
    dependencies: list[DependencyHealth]
