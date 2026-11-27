import time
import uuid
from contextvars import ContextVar
from typing import Optional
from fastapi import Request, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)
from starlette.middleware.base import BaseHTTPMiddleware

# Context variable for distributed request tracing
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")

# 1. Prometheus Metrics Definitions
HTTP_REQUESTS_TOTAL = Counter(
    "foodvision_http_requests_total",
    "Total count of HTTP requests processed by FoodVision AI",
    ["method", "endpoint", "status_code"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "foodvision_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

IN_FLIGHT_REQUESTS = Gauge(
    "foodvision_in_flight_requests",
    "Number of active HTTP requests currently being processed",
)

ML_INFERENCE_DURATION_SECONDS = Histogram(
    "foodvision_ml_inference_duration_seconds",
    "TensorFlow forward pass latency in seconds (pure CPU model computation)",
    ["model_version"],
    buckets=(0.02, 0.05, 0.1, 0.2, 0.35, 0.5, 0.75, 1.0, 2.0, 5.0),
)

PREDICTIONS_TOTAL = Counter(
    "foodvision_predictions_total",
    "Total classification predictions served by food category",
    ["top_food", "is_ood"],
)

RATE_LIMIT_HITS_TOTAL = Counter(
    "foodvision_rate_limit_hits_total",
    "Count of requests throttled by sliding-window rate limiting",
    ["prefix"],
)


def get_current_request_id() -> str:
    """Returns the current request's correlation ID."""
    return request_id_ctx.get()


class TelemetryMiddleware(BaseHTTPMiddleware):
    """
    Production Telemetry Middleware:
      1. Generates or propagates X-Request-ID for distributed tracing.
      2. Measures request execution duration and tracks in-flight gauges.
      3. Normalizes route endpoints to avoid Prometheus cardinality explosion.
      4. Injects X-Request-ID and X-Response-Time headers into every response.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Ignore prometheus scrape endpoint from request tracking to keep metrics clean
        if request.url.path == "/metrics":
            return await call_next(request)

        # 1. Extract or generate Correlation Request ID
        req_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        token = request_id_ctx.set(req_id)

        # 2. Track in-flight gauge and start timer
        IN_FLIGHT_REQUESTS.inc()
        start_time = time.perf_counter()

        try:
            response = await call_next(request)
            duration = time.perf_counter() - start_time
            status_code = response.status_code
        except Exception:
            duration = time.perf_counter() - start_time
            status_code = 500
            endpoint = self._normalize_path(request)
            HTTP_REQUESTS_TOTAL.labels(
                method=request.method,
                endpoint=endpoint,
                status_code=str(status_code),
            ).inc()
            HTTP_REQUEST_DURATION_SECONDS.labels(
                method=request.method,
                endpoint=endpoint,
            ).observe(duration)
            raise
        finally:
            IN_FLIGHT_REQUESTS.dec()
            request_id_ctx.reset(token)

        # 3. Normalize endpoint path to prevent label cardinality explosion
        endpoint = self._normalize_path(request)

        # 4. Record Prometheus Metrics
        HTTP_REQUESTS_TOTAL.labels(
            method=request.method,
            endpoint=endpoint,
            status_code=str(status_code),
        ).inc()

        HTTP_REQUEST_DURATION_SECONDS.labels(
            method=request.method,
            endpoint=endpoint,
        ).observe(duration)

        # 5. Inject Tracing and Performance Headers
        response.headers["X-Request-ID"] = req_id
        response.headers["X-Response-Time"] = f"{duration * 1000:.2f}ms"

        return response

    @staticmethod
    def _normalize_path(request: Request) -> str:
        """
        Extracts matched route template (e.g. /api/v1/predictions/{id})
        instead of raw path to avoid metric cardinality explosion.
        """
        if hasattr(request.app, "routes"):
            for route in request.app.routes:
                match, _ = route.matches(request.scope)
                if match.name == "FULL":
                    return getattr(route, "path", request.url.path)
        return request.url.path