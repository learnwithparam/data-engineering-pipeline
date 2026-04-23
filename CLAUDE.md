# CLAUDE.md

Guidance for Claude Code when working in this repo.

## What this is

Intermediate-level data engineering workshop for [learnwithparam.com](https://www.learnwithparam.com).

Core stack:

- **Airflow** orchestrates ingestion + transform DAGs.
- **Spark** does batch processing.
- **PostgreSQL** is the warehouse (star schema).
- **MinIO** is the S3-compatible raw/processed lake.
- **Great Expectations** validates data quality.
- **Python FastAPI** is the control-plane API (ported 1:1 in spirit from a .NET 8 sample in the parent source repo).

See `README.md` for the full walkthrough.

## Quick start

```bash
uv sync
cp .env.example .env    # defaults work for local compose
make dev                # FastAPI on :8000, /docs renders
```

Full stack:

```bash
make up                 # docker compose up -d
make airflow-dag        # trigger the batch DAG
make spark-job          # submit the Spark batch job
make down
```

## Smoke test

Covered by the shared sweep in `../smoke_test_all.sh`:

```bash
bash ../smoke_test_all.sh data-engineering-pipeline
```

The FastAPI `/health` returns 200 even when the compose stack is down (each underlying check reports `"unavailable"` gracefully). `/data-engineering-pipeline/pipeline/trigger` returns `{"status": "accepted", ...}` — Airflow is called only when `AIRFLOW_BASE_URL` is reachable.

## Push workflow

Before every push:

1. Run the smoke test above. It must pass.
2. `.gitignore` covers `.env`, `__pycache__/`, `.venv/`, `/data/`, `/logs/`, `mlruns/`, `great_expectations/uncommitted/`.
3. `git status` — no secrets or scratch artefacts.
4. Commit with a descriptive message.
5. `git push origin main` — remote is `git@github.com:learnwithparam/data-engineering-pipeline.git`.

Never force-push. Never commit `.env`.
