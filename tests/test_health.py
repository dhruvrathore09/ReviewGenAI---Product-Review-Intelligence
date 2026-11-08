"""Unit and integration tests for the /api/health endpoint."""

import pytest


def test_health_check_success(client):
    """Verify /api/health returns 200, healthy status, and connected database."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert "timestamp" in data
    assert data["version"] == "1.0.0"


def test_cors_origin_restrictions(client):
    """Verify only authorized local frontend origins receive CORS allow headers."""
    # Allowed local Vite origin
    resp_allowed = client.options(
        "/api/health",
        headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "GET"},
    )
    assert resp_allowed.headers.get("access-control-allow-origin") == "http://localhost:5173"

    # Unauthorized origin
    resp_blocked = client.options(
        "/api/health",
        headers={"Origin": "http://unauthorized-domain.com", "Access-Control-Request-Method": "GET"},
    )
    assert resp_blocked.headers.get("access-control-allow-origin") is None

