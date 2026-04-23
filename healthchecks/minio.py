"""Port of HealthChecks/MinioHealthCheck.cs."""

from __future__ import annotations

import asyncio
from urllib.parse import urlparse

from minio import Minio

from config.minio_options import MinioOptions


def _parse_endpoint(endpoint: str) -> tuple[str, bool]:
    parsed = urlparse(endpoint if "://" in endpoint else f"http://{endpoint}")
    host = parsed.netloc or parsed.path
    secure = parsed.scheme == "https"
    return host, secure


async def check_minio(opts: MinioOptions, timeout: float = 3.0) -> dict:
    if not opts.endpoint or not opts.access_key:
        return {"status": "unavailable", "detail": "MinIO not configured"}

    host, secure = _parse_endpoint(opts.endpoint)
    access_key = opts.access_key
    secret_key = opts.secret_key

    def _probe() -> dict:
        client = Minio(host, access_key=access_key, secret_key=secret_key, secure=secure)
        buckets = client.list_buckets()
        return {"status": "healthy", "buckets": [b.name for b in buckets]}

    try:
        return await asyncio.wait_for(asyncio.to_thread(_probe), timeout=timeout)
    except Exception as exc:
        return {"status": "unavailable", "detail": str(exc)[:200]}
