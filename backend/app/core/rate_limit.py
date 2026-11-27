import logging
import time
from typing import Callable, Optional
from fastapi import Depends, HTTPException, Request, Response, status
import redis.asyncio as redis
from redis.exceptions import RedisError

from app.api.deps import get_optional_current_user
from app.core.config import settings
from app.models.user import User

logger = logging.getLogger(__name__)

# Reusable async Redis/Valkey client instance
_valkey_client: Optional[redis.Redis] = None


def get_valkey_client() -> redis.Redis:
    """Returns a singleton async Redis/Valkey client."""
    global _valkey_client
    if _valkey_client is None:
        _valkey_client = redis.from_url(
            settings.valkey_url,
            decode_responses=True,
            socket_connect_timeout=1.0,
            socket_timeout=1.0,
        )
    return _valkey_client


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
    Sliding-Window Log rate limiter using Valkey (Redis-compatible) Sorted Sets.
    
    Algorithm:
      1. Prune timestamps older than (now - window_seconds) via ZREMRANGEBYSCORE.
      2. Count requests remaining in the current sliding window via ZCARD.
      3. If count >= limit, reject with HTTP 429 and Retry-After header.
      4. Otherwise, record the current timestamp via ZADD and refresh TTL via EXPIRE.
      5. Inject standard X-RateLimit-* headers into the response.
    
    Fail-Open:
      If Valkey is unreachable, down, or times out, logs a warning and allows
      traffic through to prevent service denial caused by cache outages.
    """
    key = f"{prefix}:{identifier}"
    now = time.time()
    window_start = now - window_seconds

    try:
        client = get_valkey_client()

        # Execute atomic sliding window check
        async with client.pipeline(transaction=True) as pipe:
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zcard(key)
            results = await pipe.execute()

        current_count = int(results[1])

        if current_count >= limit:
            # Query oldest entry in window to calculate exact seconds until quota frees up
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

        # Within limit: Record request timestamp with high-precision member key
        member = f"{now}:{time.time_ns()}"
        async with client.pipeline(transaction=True) as pipe:
            pipe.zadd(key, {member: now})
            pipe.expire(key, window_seconds + 5)
            await pipe.execute()

        remaining = max(0, limit - (current_count + 1))
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(now + window_seconds))

    except HTTPException:
        raise
    except (RedisError, ConnectionError, OSError) as exc:
        logger.warning(
            "Valkey rate limiter unavailable (%s). Failing open for %s.",
            exc,
            request.url.path,
        )
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