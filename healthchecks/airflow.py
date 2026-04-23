"""Port of HealthChecks/AirflowHealthCheck.cs."""

from __future__ import annotations

import httpx

from config.airflow_options import AirflowOptions


async def check_airflow(opts: AirflowOptions, timeout: float = 3.0) -> dict:
    if not opts.base_url:
        return {"status": "unavailable", "detail": "AIRFLOW_BASE_URL not set"}
    url = opts.base_url.rstrip("/") + "/health"
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.get(url)
            if r.status_code == 200:
                payload = None
                if r.headers.get("content-type", "").startswith("application/json"):
                    payload = r.json()
                return {"status": "healthy", "upstream": payload}
            return {"status": "unavailable", "detail": f"HTTP {r.status_code}"}
    except Exception as exc:
        return {"status": "unavailable", "detail": str(exc)[:200]}
