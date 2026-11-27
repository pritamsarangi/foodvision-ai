import asyncio
from collections import defaultdict, deque
import logging
import time
from typing import Callable, Optional
from fastapi import Depends, HTTPException, Request, Response, status
import redis.asyncio as redis
from redis.exceptions import RedisError
from app.core.telemetry import RATE_LIMIT_HITS_TOTAL

from app.api.deps import get_optional_current_user
from app.core.config import settings
from app.models.user import User

logger = logging.getLogger(__name__)

# Reusable async Redis/Valkey client instance
_valkey_client: Optional[redis.Redis] = None
_valkey_offline_logged: bool = False


def get_valkey_client() -> redis.Redis:
    """Returns a singleton async Redis/Valkey client."""
    global _valkey_client
    if _valkey_client is None:
        _valkey_client = redis.from_url(
            settings.valkey_url,
            decode_responses=True,
            socket_connect_timeout=0.5,
            socket_timeout=0.5,
        )
    return _valkey_client


class InMemorySlidingWindow:
    """
    High-performance in-memory sliding-window log fallback.
    Used when Valkey/Redis is unreachable (e.g. single-container Render free tier).
    Guarantees rate limiting protection with automatic memory reclamation.
    """

    def __init__(self):
        self._windows: dict[str, deque[float]] = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def check_and_record(
        self, key: str, limit: int, window_seconds: int
    ) -> tuple[bool, int, int]:
        """
        Checks quota and records request in sliding window.
        Returns: (is_allowed, remaining, retry_after)
        """
        now = time.time()
        window_start = now - window_seconds

        async with self._lock:
            timestamps = self._windows[key]

            # 1. Prune expired entries
            while timestamps and timestamps[0] <= window_start:
                timestamps.popleft()

            current_count = len(timestamps)

            # 2. Check if quota exceeded
            if current_count >= limit:
                oldest_ts = timestamps[0]
                retry_after = max(1, int(window_seconds - (now - oldest_ts)) + 1)
                return False, 0, retry_after

            # 3. Record within quota
            timestamps.append(now)
            remaining = max(0, limit - (current_count + 1))

            # Clean up empty keys if map grows large (> 5000 items)
            if len(self._windows) > 5000:
                expired_keys = [
                    k for k, q in self._windows.items() if not q or q[-1] <= window_start
                ]
                for k in expired_keys:
                    self._windows.pop(k, None)

            return True, remaining, window_seconds


# Global in-memory fallback singleton
_in_memory_limiter = InMemorySlidingWindow()


def get_client_ip(request: Request) -> str:
    """
    Extracts the client IP from Cloudflare / Caddy reverse-proxy headers,
    falling back to request.client.host.
    """
    # 1. Cloudflare header (highest priority behind Cloudflare)
    cf_connecting_ip = request.headers.get("CF-Connecting-IP")
    if cf_connecting_ip:
        return cf_connecting_ip.strip()

    # 2. Standard X-Forwarded-For (originating client IP is first)
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()

    # 3. Direct socket connection host
    if request.client and request.client.host:
        return request.client.host

    return "127.0.0.1"


async def check_rate_limit(
    request: Request,
    response: Response,
    limit: int,
    window_seconds: int,
    prefix: str,
    identifier: str,
) -> None:
    """
    Dual-layer sliding-window rate limiter:
      1. Primary: Valkey / Redis distributed sorted set (ZSET).
      2. Fallback: In-memory sliding-window log (for single-container free deployments).
      3. Fail-Open: If an unexpected internal error occurs, allows traffic through.
    """
    global _valkey_offline_logged
    key = f"{prefix}:{identifier}"
    now = time.time()
    window_start = now - window_seconds

    # Attempt primary Valkey rate limiting
    try:
        client = get_valkey_client()

        async with client.pipeline(transaction=True) as pipe:
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zcard(key)
            results = await pipe.execute()

        current_count = int(results[1])

        if current_count >= limit:
            RATE_LIMIT_HITS_TOTAL.labels(prefix=prefix).inc()
            oldest_entries = await client.zrange(key, 0, 0, withscores=True)
            if oldest_entries:
                oldest_ts = oldest_entries[0][1]
                retry_after = max(1, int(window_seconds - (now - oldest_ts)) + 1)
            else:
                retry_after = window_seconds

            response.headers["X-RateLimit-Limit"] = str(limit)
            response.headers["X-RateLimit-Remaining"] = "0"
            response.headers["X-RateLimit-Reset"] = str(int(now + retry_after))
            response.headers["Retry-After"] = str(retry_after)

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Try again in {retry_after} seconds.",
                headers={"Retry-After": str(retry_after)},
            )

        member = f"{now}:{time.time_ns()}"
        async with client.pipeline(transaction=True) as pipe:
            pipe.zadd(key, {member: now})
            pipe.expire(key, window_seconds + 5)
            await pipe.execute()

        remaining = max(0, limit - (current_count + 1))
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(now + window_seconds))
        return

    except HTTPException:
        raise
    except (RedisError, ConnectionError, OSError):
        # Valkey unavailable: smoothly engage in-memory fallback
        if not _valkey_offline_logged:
            logger.info("Valkey is offline; engaging in-memory sliding-window rate limiter.")
            _valkey_offline_logged = True

    # In-memory sliding-window fallback
    try:
        allowed, remaining, reset_or_retry = await _in_memory_limiter.check_and_record(
            key=key, limit=limit, window_seconds=window_seconds
        )

        if not allowed:
            RATE_LIMIT_HITS_TOTAL.labels(prefix=prefix).inc()
            retry_after = reset_or_retry
            response.headers["X-RateLimit-Limit"] = str(limit)
            response.headers["X-RateLimit-Remaining"] = "0"
            response.headers["X-RateLimit-Reset"] = str(int(now + retry_after))
            response.headers["Retry-After"] = str(retry_after)

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Try again in {retry_after} seconds.",
                headers={"Retry-After": str(retry_after)},
            )

        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(now + window_seconds))

    except HTTPException:
        raise
    except Exception as exc:
        # Ultimate fail-open safety net
        logger.warning("Rate limiter fallback error (%s). Failing open for %s.", exc, request.url.path)
        return


class RateLimiter:
    """FastAPI Dependency for route-level rate limiting by client IP."""

    def __init__(
        self,
        limit: int,
        window_seconds: int,
        prefix: str = "rl",
        key_func: Optional[Callable[[Request], str]] = None,
    ):
        self.limit = limit
        self.window_seconds = window_seconds
        self.prefix = prefix
        self.key_func = key_func

    async def __call__(self, request: Request, response: Response) -> None:
        identifier = self.key_func(request) if self.key_func else get_client_ip(request)
        await check_rate_limit(
            request=request,
            response=response,
            limit=self.limit,
            window_seconds=self.window_seconds,
            prefix=self.prefix,
            identifier=identifier,
        )


async def predict_rate_limiter(
    request: Request,
    response: Response,
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> None:
    """
    Tiered rate limiting for ML Inference:
      - Authenticated users: 30 requests / 60 seconds (keyed by user_id)
      - Unauthenticated guests: 10 requests / 60 seconds (keyed by IP)
    """
    if current_user:
        limit = 30
        prefix = "rl:predict:user"
        identifier = current_user.id
    else:
        limit = 10
        prefix = "rl:predict:guest"
        identifier = get_client_ip(request)

    await check_rate_limit(
        request=request,
        response=response,
        limit=limit,
        window_seconds=60,
        prefix=prefix,
        identifier=identifier,
    )