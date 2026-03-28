from fastapi.testclient import TestClient

from app.main import app


def test_health_returns_200():
    client = TestClient(app)
    response = client.get("/health/")
    assert response.status_code == 200


def test_health_response_body():
    client = TestClient(app)
    response = client.get("/health/")
    data = response.json()
    assert data["status"] == "online"
    assert data["system"] == "String Free Build"
    assert data["version"] == "0.1.0"
