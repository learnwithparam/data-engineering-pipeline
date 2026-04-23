"""Business logic: trigger Airflow DAGs, query warehouse marts."""

from __future__ import annotations

import logging
import uuid
from typing import Any

import httpx
import structlog

from config import AirflowOptions, DatabaseOptions, GEOptions, MinioOptions
from healthchecks import check_airflow, check_minio, check_postgres
from models import BatchRequest, BatchResponse, DatasetSummary

logging.basicConfig(level=logging.INFO)
log = structlog.get_logger()


class PipelineService:
    def __init__(self) -> None:
        log.info("service.init")
        self.db = DatabaseOptions()
        self.airflow = AirflowOptions()
        self.minio = MinioOptions()
        self.ge = GEOptions()

    async def health(self) -> dict[str, Any]:
        checks = {
            "postgres": await check_postgres(self.db),
            "minio": await check_minio(self.minio),
            "airflow": await check_airflow(self.airflow),
        }
        overall = "ok" if any(c["status"] == "healthy" for c in checks.values()) else "degraded"
        return {"status": overall, "checks": checks}

    async def trigger_batch(self, req: BatchRequest) -> BatchResponse:
        run_id = str(uuid.uuid4())
        log.info("pipeline.trigger", source_table=req.source_table, run_id=run_id)

        # If Airflow is configured, attempt a real DAG trigger. Otherwise stub.
        if req.trigger_airflow and self.airflow.base_url:
            try:
                url = (
                    self.airflow.base_url.rstrip("/")
                    + f"/api/v1/dags/{self.airflow.batch_dag_id}/dagRuns"
                )
                async with httpx.AsyncClient(
                    timeout=self.airflow.request_timeout_seconds,
                    auth=(self.airflow.username, self.airflow.password),
                ) as client:
                    r = await client.post(
                        url,
                        json={
                            "dag_run_id": run_id,
                            "conf": {
                                "source_table": req.source_table,
                                "limit": req.limit,
                                "destination_prefix": req.destination_prefix,
                            },
                        },
                    )
                    if r.status_code in (200, 201):
                        log.info("pipeline.trigger.ok", run_id=run_id)
                    else:
                        log.warning("pipeline.trigger.upstream_fail", status=r.status_code)
            except Exception as exc:
                log.warning("pipeline.trigger.exception", error=str(exc)[:200])

        object_key = f"{self.minio.bucket_raw}/{req.source_table}/{run_id}.parquet"
        return BatchResponse(
            object_key=object_key,
            run_id=run_id,
            ge_report=None,
            status="accepted",
        )

    async def list_datasets(self) -> list[DatasetSummary]:
        # Graceful fallback when warehouse Postgres isn't up.
        if not self.db.postgres:
            return []
        try:
            import asyncpg  # type: ignore

            from healthchecks.postgres import _asyncpg_dsn

            conn = await asyncpg.connect(_asyncpg_dsn(self.db.postgres))
            try:
                rows = await conn.fetch(
                    """
                    SELECT table_name, 0::bigint AS rows
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    LIMIT 50
                    """
                )
                return [DatasetSummary(table=r["table_name"], rows=int(r["rows"])) for r in rows]
            finally:
                await conn.close()
        except Exception as exc:
            log.warning("datasets.list.error", error=str(exc)[:200])
            return []


pipeline_service = PipelineService()
