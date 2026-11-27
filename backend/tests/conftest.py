import pytest
from app.core.rate_limit import _in_memory_limiter


@pytest.fixture(autouse=True)
def reset_rate_limits():
    """
    Resets in-memory rate limiting windows between tests to guarantee test isolation.
    """
    _in_memory_limiter._windows.clear()
    yield
    _in_memory_limiter._windows.clear()