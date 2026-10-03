"""Tests for NLP text and sentiment analysis service."""


def test_positive_sentiment_analysis(client):
    """Test 3: Verify positive sentiment scoring on positive inputs."""
    payload = {
        "text": "AWS container deployment was seamless, fast, reliable, and highly scalable!",
        "category": "cloud"
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["sentiment_label"] == "POSITIVE"
    assert data["polarity_score"] > 0
    assert data["word_count"] > 0
    assert "processed_by_instance" in data


def test_negative_sentiment_analysis(client):
    """Test 4: Verify negative sentiment scoring on negative inputs."""
    payload = {
        "text": "The server crashed with a slow sluggish memory leak and broken database.",
        "category": "infrastructure"
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["sentiment_label"] == "NEGATIVE"
    assert data["polarity_score"] < 0


def test_empty_text_validation_fails(client):
    """Test 5: Verify input validation rejects empty payloads with HTTP 400 or 422."""
    response = client.post("/api/analyze", json={"text": "   "})
    assert response.status_code in [400, 422]
