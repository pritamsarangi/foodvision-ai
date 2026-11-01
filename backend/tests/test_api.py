
from types import SimpleNamespace
from unittest.mock import patch
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

FAKE_TOP_5 = [
    {"food_name": "Pizza", "confidence": 0.95},
    {"food_name": "Burger", "confidence": 0.03},
    {"food_name": "Pasta", "confidence": 0.01},
    {"food_name": "Sandwich", "confidence": 0.006},
    {"food_name": "Salad", "confidence": 0.004},
]


def test_health_endpoint():
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert isinstance(response.json()["model_loaded"], bool)


def test_reject_unsupported_image():
    response = client.post(
        "/api/v1/predict",
        files={"file": ("test.txt", b"hello", "text/plain")},
    )

    assert response.status_code == 415


def test_reject_empty_image():
    response = client.post(
        "/api/v1/predict",
        files={"file": ("empty.jpg", b"", "image/jpeg")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Image is empty"


def test_reject_oversized_image():
    response = client.post(
        "/api/v1/predict",
        files={
            "file": (
                "large.jpg",
                b"x" * (10 * 1024 * 1024 + 1),
                "image/jpeg",
            )
        },
    )

    assert response.status_code == 413


def test_successful_prediction():
    saved_record = SimpleNamespace(id="test-prediction-123")

    with (
        patch("app.main.predict_image", return_value=FAKE_TOP_5),
        patch("app.main.save_prediction", return_value=saved_record),
    ):
        response = client.post(
            "/api/v1/predict",
            files={
                "file": (
                    "food.jpg",
                    b"fake-image-bytes",
                    "image/jpeg",
                )
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["prediction_id"] == "test-prediction-123"
    assert data["food_name"] == "Pizza"
    assert data["confidence"] == 0.95
    assert len(data["top_5"]) == 5
    assert data["model_version"] == "efficientnet-b0-finetuned-v1"
    assert data["is_mock"] is False


def test_invalid_image():
    with patch(
        "app.main.predict_image",
        side_effect=ValueError("Invalid image"),
    ):
        response = client.post(
            "/api/v1/predict",
            files={
                "file": (
                    "bad.jpg",
                    b"invalid-image",
                    "image/jpeg",
                )
            },
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or unsupported image"

def test_prediction_history():
    fake_record = {
        "id": "test-123",
        "food_name": "Pizza",
        "confidence": 0.95,
    }

    mock_session = MagicMock()
    mock_session.scalars.return_value.all.return_value = [fake_record]

    with patch("app.api.predict.SessionLocal") as mock_db:
        mock_db.return_value.__enter__.return_value = mock_session

        response = client.get("/api/v1/predictions")

    assert response.status_code == 200
    assert response.json()[0]["food_name"] == "Pizza"


def test_prediction_not_found():
    mock_session = MagicMock()
    mock_session.get.return_value = None

    with patch("app.api.predict.SessionLocal") as mock_db:
        mock_db.return_value.__enter__.return_value = mock_session

        response = client.get("/api/v1/predictions/missing-id")

    assert response.status_code == 404
    assert response.json()["detail"] == "Prediction not found"


def test_cors_preflight():
    response = client.options(
        "/api/v1/predict",
        headers={
            "Origin": "http://localhost:8080",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 200
    assert (
        response.headers["access-control-allow-origin"]
        == "http://localhost:8080"
    )
    assert "POST" in response.headers["access-control-allow-methods"]


from sqlalchemy.exc import OperationalError


def test_prediction_database_failure():
    with (
        patch("app.main.predict_image", return_value=FAKE_TOP_5),
        patch(
            "app.main.save_prediction",
            side_effect=OperationalError(
                "INSERT",
                {},
                Exception("Database unavailable"),
            ),
        ),
    ):
        response = client.post(
            "/api/v1/predict",
            files={
                "file": (
                    "food.jpg",
                    b"fake-image-bytes",
                    "image/jpeg",
                )
            },
        )

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "Prediction storage temporarily unavailable"
    )


def test_prediction_history_database_failure():
    from sqlalchemy.exc import OperationalError

    mock_session = MagicMock()
    mock_session.scalars.side_effect = OperationalError(
        "SELECT", {}, Exception("Database unavailable")
    )

    with patch("app.api.predict.SessionLocal") as mock_db:
        mock_db.return_value.__enter__.return_value = mock_session

        response = client.get("/api/v1/predictions")

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "Prediction history temporarily unavailable"
    )


def test_prediction_detail_database_failure():
    from sqlalchemy.exc import OperationalError

    mock_session = MagicMock()
    mock_session.get.side_effect = OperationalError(
        "SELECT", {}, Exception("Database unavailable")
    )

    with patch("app.api.predict.SessionLocal") as mock_db:
        mock_db.return_value.__enter__.return_value = mock_session

        response = client.get("/api/v1/predictions/test-123")

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "Prediction history temporarily unavailable"
    )
