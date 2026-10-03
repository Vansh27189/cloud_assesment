"""Tests for health check and system information endpoints."""


def test_health_check_returns_healthy(client):
    """Test 1: Verify /health returns 200, status 'healthy', and required telemetry."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "uptime_seconds" in data
    assert "instance_id" in data
    assert "memory_usage_mb" in data
    assert "cpu_percent" in data


def test_system_info_metadata(client):
    """Test 2: Verify /api/info returns service metadata, features, and platform info."""
    response = client.get("/api/info")
    assert response.status_code == 200
    data = response.json()
    assert data["service_name"] == "CloudPulse Microservice"
    assert data["version"] == "1.0.0"
    assert "Containerized (Docker)" in data["features"]
    assert "Automated CI/CD (GitHub Actions)" in data["features"]
