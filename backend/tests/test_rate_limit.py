from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
import pytest
import redis.exceptions

from app.core.rate_limit import (
    RateLimiter,
    get_optional_current_user,
    predict_rate_limiter,
)
from types import SimpleNamespace
from app.models.prediction import Prediction
from app.models.user import User


class FakeValkeyPipeline:
    def __init__(self, storage):
        self.storage = storage
        self.commands = []

    def zremrangebyscore(self, key, min_score, max_score):
        self.commands.append(("zremrangebyscore", key, min_score, max_score))
        return self

    def zcard(self, key):
        self.commands.append(("zcard", key))
        return self

    def zadd(self, key, mapping):
        self.commands.append(("zadd", key, mapping))
        return self

    def expire(self, key, seconds):
        self.commands.append(("expire", key, seconds))
        return self

    async def execute(self):
        results = []
        for cmd in self.commands:
            action = cmd[0]
            if action == "zremrangebyscore":
                key, min_s, max_s = cmd[1], cmd[2], cmd[3]
                zset = self.storage.setdefault(key, {})
                to_remove = [m for m, s in zset.items() if min_s <= s <= max_s]
                for m in to_remove:
                    del zset[m]
                results.append(len(to_remove))
            elif action == "zcard":
                key = cmd[1]
                zset = self.storage.get(key, {})
                results.append(len(zset))
            elif action == "zadd":
                key, mapping = cmd[1], cmd[2]
                zset = self.storage.setdefault(key, {})
                zset.update(mapping)
                results.append(len(mapping))
            elif action == "expire":
                results.append(True)
        return results

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class FakeValkeyClient:
    def __init__(self):
        self.storage = {}

    def pipeline(self, transaction=True):
        return FakeValkeyPipeline(self.storage)

    async def zrange(self, key, start, stop, withscores=False):
        zset = self.storage.get(key, {})
        sorted_items = sorted(zset.items(), key=lambda x: x[1])
        if stop == -1:
            slice_items = sorted_items[start:]
        else:
            slice_items = sorted_items[start : stop + 1]
        if withscores:
            return slice_items
        return [m for m, s in slice_items]

# Dedicated test application
sample_app = FastAPI()


@sample_app.get(
    "/test-rate-limit",
    dependencies=[Depends(RateLimiter(limit=3, window_seconds=60, prefix="test"))],
)
def rate_limited_endpoint():
    return {"message": "ok"}


@sample_app.get(
    "/test-predict-limit",
    dependencies=[Depends(predict_rate_limiter)],
)
def predict_limited_endpoint():
    return {"message": "predict ok"}


@pytest.fixture
def fake_valkey(monkeypatch):
    fake_client = FakeValkeyClient()
    monkeypatch.setattr("app.core.rate_limit.get_valkey_client", lambda: fake_client)
    return fake_client


@pytest.fixture
def test_client():
    return TestClient(sample_app)


def test_rate_limit_allows_under_quota(fake_valkey, test_client):
    """Verifies requests within quota return 200 and decrement remaining quota."""
    r1 = test_client.get("/test-rate-limit")
    assert r1.status_code == 200
    assert r1.headers["X-RateLimit-Limit"] == "3"
    assert r1.headers["X-RateLimit-Remaining"] == "2"
    assert "X-RateLimit-Reset" in r1.headers

    r2 = test_client.get("/test-rate-limit")
    assert r2.status_code == 200
    assert r2.headers["X-RateLimit-Remaining"] == "1"

    r3 = test_client.get("/test-rate-limit")
    assert r3.status_code == 200
    assert r3.headers["X-RateLimit-Remaining"] == "0"


def test_rate_limit_blocks_exceeding_quota(fake_valkey, test_client):
    """Verifies that exceeding quota triggers HTTP 429 with Retry-After header."""
    for _ in range(3):
        test_client.get("/test-rate-limit")

    # 4th request breaches the limit of 3
    breach = test_client.get("/test-rate-limit")
    assert breach.status_code == 429
    assert "Rate limit exceeded" in breach.json()["detail"]
    assert "Retry-After" in breach.headers
    assert int(breach.headers["Retry-After"]) > 0


def test_client_ip_isolation(fake_valkey, test_client):
    """Verifies one client being rate-limited does not affect another client."""
    # Client A exhausts quota
    for _ in range(3):
        test_client.get("/test-rate-limit", headers={"X-Forwarded-For": "192.168.1.100"})

    breach_a = test_client.get(
        "/test-rate-limit", headers={"X-Forwarded-For": "192.168.1.100"}
    )
    assert breach_a.status_code == 429

    # Client B should still be allowed
    client_b = test_client.get(
        "/test-rate-limit", headers={"X-Forwarded-For": "192.168.1.200"}
    )
    assert client_b.status_code == 200
    assert client_b.headers["X-RateLimit-Remaining"] == "2"


def test_cloudflare_header_priority(fake_valkey, test_client):
    """Verifies CF-Connecting-IP takes precedence over X-Forwarded-For."""
    for _ in range(3):
        test_client.get(
            "/test-rate-limit",
            headers={
                "CF-Connecting-IP": "1.1.1.1",
                "X-Forwarded-For": "9.9.9.9",
            },
        )

    # 4th request with same CF IP gets blocked
    res = test_client.get(
        "/test-rate-limit",
        headers={
            "CF-Connecting-IP": "1.1.1.1",
            "X-Forwarded-For": "different.ip",
        },
    )
    assert res.status_code == 429


def test_fail_open_on_valkey_outage(monkeypatch, test_client):
    """Verifies that if Valkey is unreachable, requests fail open without crashing."""

    class FailingValkey:
        def pipeline(self, transaction=True):
            raise redis.exceptions.ConnectionError("Valkey server connection refused")

    monkeypatch.setattr("app.core.rate_limit.get_valkey_client", lambda: FailingValkey())

    response = test_client.get("/test-rate-limit")
    assert response.status_code == 200
    assert response.json() == {"message": "ok"}

def test_in_memory_fallback_enforces_quota_when_valkey_down(monkeypatch, test_client):
    """Verifies in-memory fallback enforces rate limits even when Valkey is completely down."""

    class FailingValkey:
        def pipeline(self, transaction=True):
            raise redis.exceptions.ConnectionError("Valkey server down")

    monkeypatch.setattr("app.core.rate_limit.get_valkey_client", lambda: FailingValkey())

    # First 3 requests should pass with in-memory fallback
    for _ in range(3):
        res = test_client.get(
            "/test-rate-limit", headers={"X-Forwarded-For": "10.10.10.10"}
        )
        assert res.status_code == 200

    # 4th request must be blocked by the in-memory fallback with HTTP 429!
    breach = test_client.get(
        "/test-rate-limit", headers={"X-Forwarded-For": "10.10.10.10"}
    )
    assert breach.status_code == 429
    assert "Retry-After" in breach.headers
    assert "Rate limit exceeded" in breach.json()["detail"]


def test_predict_rate_limiter_guest_tier(fake_valkey, test_client):
    """Verifies guest users get a 10 request limit on predict."""
    res = test_client.get("/test-predict-limit")
    assert res.status_code == 200
    assert res.headers["X-RateLimit-Limit"] == "10"
    assert res.headers["X-RateLimit-Remaining"] == "9"


def test_predict_rate_limiter_authenticated_tier(fake_valkey, test_client):
    """Verifies authenticated users get a 30 request limit keyed by user ID."""
    mock_user = SimpleNamespace(id="usr_test123", email="user@foodvision.ai")

    sample_app.dependency_overrides[get_optional_current_user] = lambda: mock_user

    try:
        res = test_client.get("/test-predict-limit")
        assert res.status_code == 200
        assert res.headers["X-RateLimit-Limit"] == "30"
        assert res.headers["X-RateLimit-Remaining"] == "29"
        # Verify key used in Valkey
        assert "rl:predict:user:usr_test123" in fake_valkey.storage
    finally:
        sample_app.dependency_overrides.clear()