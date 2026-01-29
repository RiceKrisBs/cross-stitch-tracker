"""
Tests for main application endpoints
"""

from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_homepage(client: TestClient):
    """Test that the homepage loads"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Cross-Stitch Tracker" in response.text
