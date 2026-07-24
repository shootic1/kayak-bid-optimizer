"""Integration tests for the unversioned health endpoints."""

from __future__ import annotations

from unittest.mock import patch

from httpx import AsyncClient

from app.schemas.health import DependencyHealth, HealthStatus


async def test_health_returns_exact_contract(client: AsyncClient) -> None:
    """`GET /api/health` returns the exact mandated liveness body."""
    response = await client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "backend",
        "version": "1.0.0",
    }


async def test_readiness_healthy_when_database_up(client: AsyncClient) -> None:
    """`/api/health/ready` returns 200 and healthy when the DB check passes."""
    healthy_db = DependencyHealth(
        name="database", status=HealthStatus.HEALTHY, detail="connection ok", latency_ms=1.0
    )
    with patch("app.services.health_service.check_database", return_value=healthy_db):
        response = await client.get("/api/health/ready")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert body["service"] == "backend"
    assert body["dependencies"][0]["name"] == "database"


async def test_readiness_503_when_database_down(client: AsyncClient) -> None:
    """`/api/health/ready` returns 503 when the DB dependency is unhealthy."""
    down_db = DependencyHealth(
        name="database", status=HealthStatus.UNHEALTHY, detail="connection failed"
    )
    with patch("app.services.health_service.check_database", return_value=down_db):
        response = await client.get("/api/health/ready")

    assert response.status_code == 503
    assert response.json()["status"] == "unhealthy"
