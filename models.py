"""Python port of Models/*.cs (BatchRequest, BatchResponse, StreamingRequest, StreamingResponse)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class BatchRequest(BaseModel):
    source_table: str = Field(..., pattern=r"^[A-Za-z0-9_]+$")
    destination_prefix: str | None = Field(default=None, max_length=200)
    limit: int | None = Field(default=None, ge=1, le=100000)
    trigger_airflow: bool = True
    run_great_expectations: bool = True


class BatchResponse(BaseModel):
    object_key: str = ""
    run_id: str | None = None
    ge_report: str | None = None
    status: str = "accepted"


class StreamingRequest(BaseModel):
    partition: int = Field(default=0, ge=0)
    payload: dict[str, Any] | None = None


class StreamingResponse(BaseModel):
    run_id: str
    status: str | None = None


class HealthCheck(BaseModel):
    status: str
    detail: str | None = None
    upstream: dict[str, Any] | None = None
    buckets: list[str] | None = None


class HealthResponse(BaseModel):
    status: str
    service: str = "data-engineering-pipeline"
    checks: dict[str, HealthCheck]


class DatasetSummary(BaseModel):
    table: str
    rows: int
    last_updated: str | None = None


class PipelineTriggerResponse(BaseModel):
    status: str
    dag_id: str
    run_id: str
