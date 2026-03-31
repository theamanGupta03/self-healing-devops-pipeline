import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from app import app as flask_app


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


def test_home_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200

def test_home_json_structure(client):
    response = client.get("/")
    data = response.get_json()
    assert "status" in data
    assert data["status"] == "running"

def test_health_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200

def test_health_json_structure(client):
    response = client.get("/health")
    data = response.get_json()
    assert data["status"] == "UP"
    assert "uptime_seconds" in data

def test_info_endpoint(client):
    response = client.get("/info")
    assert response.status_code == 200
    data = response.get_json()
    assert "version" in data

def test_nonexistent_route_returns_404(client):
    response = client.get("/doesnotexist")
    assert response.status_code == 404
