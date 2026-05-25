import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_home_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200


def test_home_returns_json(client):
    response = client.get("/")
    data = response.get_json()
    assert "message" in data
    assert "host" in data
    assert "env" in data


def test_home_message_content(client):
    response = client.get("/")
    data = response.get_json()
    assert "Flask" in data["message"]


def test_health_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_health_returns_healthy(client):
    response = client.get("/health")
    data = response.get_json()
    assert data["status"] == "healthy"


def test_unknown_route_returns_404(client):
    response = client.get("/does-not-exist")
    assert response.status_code == 404
