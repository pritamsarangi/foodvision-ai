from io import BytesIO
from types import SimpleNamespace
from unittest.mock import patch
from PIL import Image
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _make_dummy_image_bytes() -> bytes:
    img = Image.new("RGB", (224, 224), color="blue")
    buf = BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_request_id_generated_and_returned_in_header():
    """Verifies each request receives an X-Request-ID and X-Response-Time header."""
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    assert "X-Request-ID" in res.headers
    assert len(res.headers["X-Request-ID"]) >= 16
    assert "X-Response-Time" in res.headers
    assert res.headers["X-Response-Time"].endswith("ms")


def test_request_id_propagated_when_provided():
    """Verifies incoming X-Request-ID (from Cloudflare/Caddy) is preserved for distributed tracing."""
    custom_trace_id = "trace-cf-9876543210"
    res = client.get("/api/v1/health", headers={"X-Request-ID": custom_trace_id})
    assert res.status_code == 200
    assert res.headers["X-Request-ID"] == custom_trace_id


def test_prometheus_metrics_endpoint():
    """Verifies /metrics returns OpenMetrics plain text with standard gauges and counters."""
    client.get("/api/v1/health")

    res = client.get("/metrics")
    assert res.status_code == 200
    assert "text/plain" in res.headers["content-type"]
    assert "foodvision_http_requests_total" in res.text
    assert "foodvision_http_request_duration_seconds" in res.text
    assert "foodvision_in_flight_requests" in res.text


def test_metric_path_normalization_prevents_cardinality_explosion():
    """
    Verifies that requests to parameterized routes are labeled with the route template
    (e.g. /api/v1/predictions/{prediction_id}) rather than the raw unique ID.
    """
    fake_uuid = "123e4567-e89b-12d3-a456-426614174000"
    client.get(f"/api/v1/predictions/{fake_uuid}")

    metrics_res = client.get("/metrics")
    assert metrics_res.status_code == 200
    assert 'endpoint="/api/v1/predictions/{prediction_id}"' in metrics_res.text
    assert fake_uuid not in metrics_res.text


def test_ml_inference_and_prediction_metrics_recorded():
    """Verifies inference latency histogram and prediction counters are incremented."""
    fake_top_5 = [
        {"food_name": "Ramen", "confidence": 0.96},
        {"food_name": "Udon", "confidence": 0.02},
        {"food_name": "Soba", "confidence": 0.01},
        {"food_name": "Pho", "confidence": 0.005},
        {"food_name": "Laksa", "confidence": 0.005},
    ]

    image_bytes = _make_dummy_image_bytes()

    with patch("app.main.predict_image", return_value=fake_top_5):
        with patch("app.main.save_prediction") as mock_save:
            mock_save.return_value = SimpleNamespace(id="pred_test999")

            res = client.post(
                "/api/v1/predict",
                files={"file": ("test.jpg", image_bytes, "image/jpeg")},
            )
            assert res.status_code == 200

    metrics_res = client.get("/metrics")
    assert metrics_res.status_code == 200
    assert "foodvision_ml_inference_duration_seconds" in metrics_res.text
    assert 'foodvision_predictions_total{is_ood="False",top_food="Ramen"}' in metrics_res.text