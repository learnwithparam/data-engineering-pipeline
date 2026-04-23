"""Port of HealthChecks/PostgresHealthCheck.cs."""

from __future__ import annotations

import asyncio

import asyncpg

from config.database_options import DatabaseOptions


def _asyncpg_dsn(dsn: str) -> str:
    # asyncpg accepts postgresql:// URLs; strip the SQLAlchemy +driver suffix if present
    if "+psycopg2" in dsn:
        dsn = dsn.replace("+psycopg2", "")
    return dsn


async def check_postgres(opts: DatabaseOptions, timeout: float = 3.0) -> dict:
    if not opts.postgres:
        return {"status": "unavailable", "detail": "DB_POSTGRES not set"}
    try:
        conn = await asyncio.wait_for(
            asyncpg.connect(_asyncpg_dsn(opts.postgres)),
            timeout=timeout,
        )
        try:
            await conn.execute("SELECT 1")
            return {"status": "healthy"}
        finally:
            await conn.close()
    except Exception as exc:
        return {"status": "unavailable", "detail": str(exc)[:200]}
