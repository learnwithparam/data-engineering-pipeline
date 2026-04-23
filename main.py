"""FastAPI entry point. Python port of Program.cs."""

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from router import router

app = FastAPI(
    title="Data Engineering Pipeline",
    description=(
        "Intermediate data engineering workshop: Airflow + Spark + Postgres + MinIO + "
        "Great Expectations. learnwithparam.com"
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
async def root() -> dict:
    return {"service": "data-engineering-pipeline", "docs": "/docs"}


@app.get("/health")
async def root_health() -> dict:
    """Unprefixed /health for smoke tests and container orchestrators."""
    from service import pipeline_service

    return await pipeline_service.health()
