from src.database import db
from src.models import User, UserRole


def test_login_success(client, auth_headers):
    """Auth headers fixture already tested login — just verify /me."""
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data["username"] == "admin"
    assert data["role"] == "admin"


def test_login_invalid_credentials(client):
    response = client.post("/api/auth/login", json={"username": "noone", "password": "wrong"})
    assert response.status_code == 401


def test_login_missing_fields(client):
    response = client.post("/api/auth/login", json={"username": "admin"})
    assert response.status_code == 400


def test_me_without_token(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401
