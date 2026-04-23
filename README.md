# Data Engineering Pipeline

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Airflow](https://img.shields.io/badge/Airflow-2.7.3-017CEE?logo=apacheairflow&logoColor=white)](https://airflow.apache.org/)
[![Spark](https://img.shields.io/badge/Spark-3.5.3-E25A1C?logo=apachespark&logoColor=white)](https://spark.apache.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![MinIO](https://img.shields.io/badge/MinIO-C72E49?logo=minio&logoColor=white)](https://min.io/)
[![Great Expectations](https://img.shields.io/badge/Great_Expectations-6A0DAD)](https://greatexpectations.io/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![learnwithparam](https://img.shields.io/badge/learnwithparam.com-0a0a0a?logo=readthedocs&logoColor=white)](https://www.learnwithparam.com)

Intermediate data engineering workshop. A slimmed, teachable data platform: Airflow orchestrates batch ingestion, Spark does the heavy lifting, PostgreSQL is the warehouse, MinIO is the lake, Great Expectations validates quality, and a Python FastAPI backend is the control plane.

Originally sampled from a .NET-8 reference architecture; the backend has been ported 1:1 (in spirit) to Python so the entire platform is a single language + toolchain.

This is the middle tier of the [learnwithparam.com](https://www.learnwithparam.com) data engineering track. Between [`data-engineering-medallion`](../data-engineering-medallion) (notebook-first) and [`end-to-end-data-pipeline`](../end-to-end-data-pipeline) (full production stack).

## Architecture

```
 MySQL (source)                               MinIO (raw)
       │                                           ▲
       │  Airflow batch_ingestion_dag              │
       ├─────── extract ───────────────────────────┘
       │
       │  Great Expectations validate
       │
       │  Airflow warehouse_transform_dag
       ├─────── Spark batch job ──────┐
       │                              │
       ▼                              ▼
   PostgreSQL (star schema)    MinIO (processed)
       ▲
       │
       │   FastAPI  /health  /pipeline/trigger  /datasets
       │
    User / BI / notebook
```

## Tech

- **Python 3.11**, **uv** for env management
- **FastAPI** + **Pydantic v2** + **pydantic-settings** (.NET Options → pydantic BaseSettings)
- **Airflow 2.7** with DAGs for batch ingestion, streaming monitoring, warehouse transform
- **Spark 3.5** for batch processing (one job out of the box)
- **PostgreSQL 15** as the warehouse (star schema SQL in `scripts/init_warehouse.sql`)
- **MinIO** as the S3-compatible lake (raw + processed buckets)
- **Great Expectations** for data quality
- **Docker Compose** glues the stack together

## Quick start

```bash
# 1. Install deps (creates .venv)
uv sync

# 2. Create env file
cp .env.example .env

# 3. Run the FastAPI alone (no compose needed)
make dev           # /docs on http://localhost:8000/docs

# OR: stand up the whole stack
make up            # postgres, minio, airflow, spark-master, spark-worker, api
make airflow-dag   # trigger the batch_ingestion_dag
make spark-job     # submit the Spark batch job
make down
```

## Endpoints

- `GET  /`                                          → service banner
- `GET  /health`                                    → aggregate health of Postgres / MinIO / Airflow
- `GET  /data-engineering-pipeline/health`          → same, prefixed form
- `POST /data-engineering-pipeline/pipeline/trigger` → trigger the batch DAG
- `POST /data-engineering-pipeline/batch`           → compatible with the original .NET `BatchController`
- `GET  /data-engineering-pipeline/datasets`        → list tables in the warehouse

All endpoints gracefully degrade when the compose stack isn't running — `/health` reports `unavailable` per check and returns 200, and the trigger endpoint stubs the run when Airflow is unreachable.

## Project layout

```
data-engineering-pipeline/
├── main.py                  FastAPI app
├── router.py                Routes (ported from Controllers/*.cs)
├── service.py               PipelineService (ported from BatchService/DbService)
├── models.py                Pydantic models (ported from Models/*.cs)
├── config/
│   ├── database_options.py  ← DatabaseOptions.cs
│   ├── airflow_options.py   ← AirflowOptions.cs
│   ├── minio_options.py     ← MinioOptions.cs
│   └── ge_options.py        ← GEOptions.cs
├── healthchecks/
│   ├── postgres.py          ← PostgresHealthCheck.cs
│   ├── minio.py             ← MinioHealthCheck.cs
│   └── airflow.py           ← AirflowHealthCheck.cs
├── airflow/                 DAGs, plugins, Airflow Dockerfile
│   └── dags/
│       ├── batch_ingestion_dag.py
│       ├── warehouse_transform_dag.py
│       └── streaming_monitoring_dag.py
├── spark/                   Spark master/worker Dockerfile + batch job
├── great_expectations/      Expectations + checkpoints
├── scripts/                 init_db.sql, init_warehouse.sql
├── pyproject.toml           uv-managed deps
├── uv.lock
├── Makefile
├── Dockerfile               python:3.11-slim + uv
├── docker-compose.yml       5 services + api
└── README.md
```

## Progression

- Previous: [`data-engineering-medallion`](../data-engineering-medallion) — notebook-first DuckDB walkthrough.
- Next: [`end-to-end-data-pipeline`](../end-to-end-data-pipeline) — full 20-service production platform with Kafka, Snowflake, MLflow, Prometheus, Grafana, Kubernetes, Terraform, Helm.

## Learn more

- Full course: [learnwithparam.com](https://www.learnwithparam.com)

## License

MIT. See `LICENSE`.
