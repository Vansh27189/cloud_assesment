"""Tests for observability metrics and distributed telemetry headers."""


def test_metrics_and_telemetry_headers(client):
    """Test 8: Verify telemetry headers on all responses and metrics endpoint aggregation."""
    # Send a request to generate traffic
    res = client.get("/health")
    assert res.status_code == 200

    # Verify custom distributed tracing headers
    assert "X-Instance-ID" in res.headers
    assert "X-Response-Time-Ms" in res.headers
    assert "X-Service-Version" in res.headers

    # Check metrics endpoint
    metrics_res = client.get("/metrics")
    assert metrics_res.status_code == 200
    metrics = metrics_res.json()
    assert metrics["total_requests"] > 0
    assert "requests_by_endpoint" in metrics
    assert "/health" in metrics["requests_by_endpoint"]
