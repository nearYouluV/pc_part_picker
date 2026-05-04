from collections import defaultdict, deque
from threading import Lock
from time import monotonic

from fastapi import HTTPException, Request, status


_rate_limit_lock = Lock()
_rate_limit_buckets: dict[str, deque[float]] = defaultdict(deque)


def _get_client_ip(request: Request) -> str:
    # Trust first hop if X-Forwarded-For is present (reverse proxy setup).
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        first_hop = forwarded_for.split(",", 1)[0].strip()
        if first_hop:
            return first_hop

    client = request.client
    if client and client.host:
        return client.host
    return "unknown"


def _enforce_sliding_window(
    request: Request,
    bucket: str,
    limit: int,
    window_seconds: int,
) -> None:
    now = monotonic()
    ip = _get_client_ip(request)
    bucket_key = f"{bucket}:{ip}"

    with _rate_limit_lock:
        timestamps = _rate_limit_buckets[bucket_key]
        while timestamps and (now - timestamps[0]) >= window_seconds:
            timestamps.popleft()

        if len(timestamps) >= limit:
            retry_after = int(max(1, window_seconds - (now - timestamps[0])))
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later.",
                headers={"Retry-After": str(retry_after)},
            )

        timestamps.append(now)


def per_ip_rate_limit(bucket: str, limit: int, window_seconds: int):
    async def dependency(request: Request) -> None:
        _enforce_sliding_window(request, bucket, limit, window_seconds)

    return dependency
