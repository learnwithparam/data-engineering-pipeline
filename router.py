"""FastAPI routes. Python port of Controllers/*.cs (BatchController, GovernanceController, MonitoringController)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from models import (
    BatchRequest,
    BatchResponse,
    DatasetSummary,
    HealthResponse,
    PipelineTriggerResponse,
)
from service import pipeline_service

router = APIRouter(prefix="/data-engineering-pipeline", tags=["data-engineering-pipeline"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    result = await pipeline_service.health()
    return HealthResponse(status=result["status"], checks=result["checks"])


@router.post("/pipeline/trigger", response_model=PipelineTriggerResponse)
async def trigger(req: BatchRequest) -> PipelineTriggerResponse:
    try:
        res = await pipeline_service.trigger_batch(req)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Trigger failed: {exc}")
    return PipelineTriggerResponse(
        status=res.status,
        dag_id=pipeline_service.airflow.batch_dag_id,
        run_id=res.run_id or "",
    )


@router.post("/batch", response_model=BatchResponse)
async def batch(req: BatchRequest) -> BatchResponse:
    """Compatible with the .NET BatchController endpoint."""
    try:
        return await pipeline_service.trigger_batch(req)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Batch failed: {exc}")


@router.get("/datasets", response_model=list[DatasetSummary])
async def list_datasets() -> list[DatasetSummary]:
    return await pipeline_service.list_datasets()
