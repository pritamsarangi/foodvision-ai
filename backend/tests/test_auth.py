import uuid
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def unique_email() -> str:
    return f"user_{uuid.uuid4().hex[:8]}@example.com"


def test_register_user_success():
    email = unique_email()
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "SecurePassword123!"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == email
    assert data["role"] == "user"
    assert data["is_active"] is True
    assert "id" in data


def test_register_duplicate_email():
    email = unique_email()
    # First registration
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "SecurePassword123!"},
    )
    # Duplicate attempt
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "DifferentPassword123!"},
    )
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


def test_login_success():
    email = unique_email()
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "SecurePassword123!"},
    )

    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "SecurePassword123!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password():
    email = unique_email()
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "CorrectPassword123!"},
    )

    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "WrongPassword999!"},
    )
    assert response.status_code == 401


def test_get_current_user_profile():
    email = unique_email()
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "SecurePassword123!"},
    )
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "SecurePassword123!"},
    )
    token = login_res.json()["access_token"]

    # 1. Access with valid token
    res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    assert res.json()["email"] == email

    # 2. Access without token fails
    res_no_auth = client.get("/api/v1/auth/me")
    assert res_no_auth.status_code == 401


def test_token_rotation_and_reuse_detection():
    email = unique_email()
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "SecurePassword123!"},
    )
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "SecurePassword123!"},
    )
    initial_refresh = login_res.json()["refresh_token"]

    # 1. Normal rotation: use refresh token to get a new pair
    rotate_res = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": initial_refresh},
    )
    assert rotate_res.status_code == 200
    new_refresh = rotate_res.json()["refresh_token"]
    assert new_refresh != initial_refresh

    # 2. Attack Simulation / Reuse Detection: Try to reuse the old initial_refresh token!
    reuse_res = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": initial_refresh},
    )
    # The server MUST detect reuse and reject it
    assert reuse_res.status_code == 401
    assert "reuse detected" in reuse_res.json()["detail"].lower()


def test_logout():
    email = unique_email()
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "SecurePassword123!"},
    )
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "SecurePassword123!"},
    )
    refresh_token = login_res.json()["refresh_token"]

    # Logout
    logout_res = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token},
    )
    assert logout_res.status_code == 200

    # Using the logged-out refresh token should now fail
    retry_res = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert retry_res.status_code == 401


def test_cross_user_prediction_isolation():
    """Verifies that User A's prediction history is completely invisible to User B."""
    from app.services.prediction_service import save_prediction

    # 1. Register and Login User A
    user_a_email = unique_email()
    client.post("/api/v1/auth/register", json={"email": user_a_email, "password": "Password123!"})
    login_a = client.post("/api/v1/auth/login", json={"email": user_a_email, "password": "Password123!"})
    token_a = login_a.json()["access_token"]
    user_a_id = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token_a}"}).json()["id"]

    # 2. Register and Login User B
    user_b_email = unique_email()
    client.post("/api/v1/auth/register", json={"email": user_b_email, "password": "Password123!"})
    login_b = client.post("/api/v1/auth/login", json={"email": user_b_email, "password": "Password123!"})
    token_b = login_b.json()["access_token"]

    # 3. Create a private prediction owned by User A
    fake_top_5 = [{"food_name": "Baklava", "confidence": 0.99}]
    pred_a = save_prediction(
        food_name="Baklava",
        confidence=0.99,
        top_5=fake_top_5,
        model_version="test-v1",
        user_id=user_a_id,
    )

    # 4. User A requests prediction history -> Should see their Baklava prediction
    res_a = client.get("/api/v1/predictions", headers={"Authorization": f"Bearer {token_a}"})
    assert res_a.status_code == 200
    ids_a = [p["id"] for p in res_a.json()]
    assert pred_a.id in ids_a

    # 5. User B requests prediction history -> MUST NOT see User A's prediction!
    res_b = client.get("/api/v1/predictions", headers={"Authorization": f"Bearer {token_b}"})
    assert res_b.status_code == 200
    ids_b = [p["id"] for p in res_b.json()]
    assert pred_a.id not in ids_b

    # 6. User B attempts direct URL access to User A's prediction ID -> Must be rejected (404)
    res_b_direct = client.get(f"/api/v1/predictions/{pred_a.id}", headers={"Authorization": f"Bearer {token_b}"})
    assert res_b_direct.status_code == 404