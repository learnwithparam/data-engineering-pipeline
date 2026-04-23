.PHONY: help setup install dev run smoke build up down logs restart clean clean-all airflow-dag spark-job

.DEFAULT_GOAL := help

BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m

VENV := .venv
UV := uv

help: ## Show this help
	@echo "$(BLUE)Data Engineering Pipeline - learnwithparam.com$(NC)"
	@echo ""
	@echo "$(GREEN)Usage:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'

setup: ## Initial setup (create .env, install uv, uv sync)
	@if [ ! -f .env ]; then \
		echo "$(BLUE)Creating .env file...$(NC)"; \
		cp .env.example .env; \
		echo "$(GREEN)OK: .env created$(NC)"; \
	else \
		echo "$(YELLOW).env already exists$(NC)"; \
	fi
	@if ! command -v uv >/dev/null 2>&1; then \
		echo "$(BLUE)Installing uv...$(NC)"; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
	else \
		echo "$(GREEN)OK: uv is installed$(NC)"; \
	fi
	@$(UV) sync
	@echo "$(GREEN)OK: Environment ready$(NC)"

install: ## Install dependencies
	@$(UV) sync

dev: setup run ## Setup and run

run: ## Start FastAPI server on :8000
	@echo "$(BLUE)Starting FastAPI on http://localhost:8000/docs$(NC)"
	@$(UV) run uvicorn main:app --reload --host 0.0.0.0 --port 8000

smoke: ## Run shared smoke test for this project
	@bash ../smoke_test_all.sh data-engineering-pipeline

build: ## Build Docker image
	docker compose build

up: ## Start full compose stack (postgres, minio, airflow, spark, api)
	docker compose up -d

down: ## Stop stack
	docker compose down

logs: ## Tail compose logs
	docker compose logs -f

restart: down up ## Restart stack

airflow-dag: ## Trigger the batch ingestion DAG
	docker compose exec airflow-webserver airflow dags trigger batch_ingestion_dag

spark-job: ## Submit the Spark batch job
	docker compose exec spark-master spark-submit /opt/spark-apps/spark_batch_job.py

clean: ## Remove venv, cache, temp files
	rm -rf $(VENV)
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf great_expectations/uncommitted
	@$(UV) cache clean

clean-all: clean down ## Clean everything including Docker volumes
	docker compose down -v
